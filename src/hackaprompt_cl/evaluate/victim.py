"""Modelo víctima: recibe prompts y devuelve respuestas.

Cada prompt del dataset (plantilla del nivel + ataque) se envía como un único
mensaje de usuario con la plantilla de chat del modelo, sin mensaje de sistema
adicional, con decodificación greedy (temperatura 0) para que sea reproducible.

Backends:
- `transformers`: Llama en 4 bits sobre GPU (Colab o Kaggle, T4 de 16 GB alcanza).
- `ollama`: servidor local de Ollama (http://localhost:11434).
"""

import os
from typing import Protocol


class Victim(Protocol):
    name: str

    def generate(self, prompts: list[str]) -> list[str]: ...


class TransformersVictim:
    def __init__(self, model_id: str, max_tokens: int = 64, load_in_4bit: bool = True):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

        if not torch.cuda.is_available():
            raise RuntimeError(
                "No hay GPU. En Colab: Entorno de ejecución → Cambiar tipo de entorno → T4 GPU."
            )
        token = os.environ.get("HF_TOKEN", "").strip() or None
        self.name = model_id
        self.max_tokens = max_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, token=token)
        self.tokenizer.padding_side = "left"  # necesario para generar en lotes
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        quant = (
            BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
            )
            if load_in_4bit
            else None
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            token=token,
            device_map="auto",
            quantization_config=quant,
            torch_dtype=torch.float16,
        )
        self.model.eval()
        self._torch = torch

    def generate(self, prompts: list[str]) -> list[str]:
        texts = [
            self.tokenizer.apply_chat_template(
                [{"role": "user", "content": p}], tokenize=False, add_generation_prompt=True
            )
            for p in prompts
        ]
        batch = self.tokenizer(
            texts, return_tensors="pt", padding=True, add_special_tokens=False
        ).to(self.model.device)
        with self._torch.no_grad():
            out = self.model.generate(
                **batch,
                max_new_tokens=self.max_tokens,
                do_sample=False,
                temperature=None,
                top_p=None,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        new_tokens = out[:, batch["input_ids"].shape[1] :]
        return self.tokenizer.batch_decode(new_tokens, skip_special_tokens=True)


class OllamaVictim:
    def __init__(self, model: str, max_tokens: int = 64, host: str = "http://localhost:11434"):
        self.name = f"ollama:{model}"
        self.model = model
        self.max_tokens = max_tokens
        self.host = host

    def generate(self, prompts: list[str]) -> list[str]:
        import requests

        answers = []
        for p in prompts:
            r = requests.post(
                f"{self.host}/api/chat",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": p}],
                    "stream": False,
                    "options": {"temperature": 0, "num_predict": self.max_tokens},
                },
                timeout=300,
            )
            r.raise_for_status()
            answers.append(r.json()["message"]["content"])
        return answers


def load_victim(cfg: dict) -> Victim:
    """Crea el modelo víctima según `victim` en configs/experiment.yaml."""
    v = cfg["victim"]
    if v["backend"] == "transformers":
        return TransformersVictim(v["model"], max_tokens=v["max_tokens"])
    if v["backend"] == "ollama":
        return OllamaVictim(v["ollama_model"], max_tokens=v["max_tokens"])
    raise ValueError(f"backend desconocido: {v['backend']}")
