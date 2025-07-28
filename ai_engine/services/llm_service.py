import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from django.conf import settings
from .base import BaseAIService
import logging

logger = logging.getLogger(__name__)


class LLMService(BaseAIService):
    def __init__(self):
        super().__init__()
        self.model_path = settings.AI_CONFIG.get('MISTRAL_MODEL_PATH')
        self.tokenizer = None

    def load_model(self):
        try:
            # Charger Mistral 7B quantized
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                load_in_4bit=True  # Quantization 4-bit
            )

            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            self.is_loaded = True
            logger.info("Mistral 7B model loaded successfully")

        except Exception as e:
            logger.error(f"Erreur chargement Mistral: {e}")
            raise

    def generate_text(self, prompt, max_length=512, temperature=0.7):
        """Génération de texte avec Mistral"""
        try:
            self.ensure_model_loaded()

            # Tokenization
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=1024
            )

            # Génération
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Décoder la réponse
            response = self.tokenizer.decode(
                outputs[0][inputs.input_ids.shape[1]:],
                skip_special_tokens=True
            )

            return response.strip()

        except Exception as e:
            logger.error(f"Erreur génération LLM: {e}")
            return ""

    def process(self, input_data):
        """Interface générique pour le service LLM"""
        prompt = input_data.get('prompt', '')
        max_length = input_data.get('max_length', 512)
        temperature = input_data.get('temperature', 0.7)

        return self.generate_text(prompt, max_length, temperature)