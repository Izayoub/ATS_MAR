import logging
from abc import ABC, abstractmethod
from django.conf import settings

logger = logging.getLogger(__name__)

# ai_engine/services/base.py
import os
import logging
import torch
from django.conf import settings
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from paddleocr import PaddleOCR
from transformers import AutoTokenizer, AutoModel


logger = logging.getLogger(__name__)


class BaseAIService:
    """Classe de base pour tous les services AI"""

    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.models_cache_dir = getattr(settings, 'MODELS_CACHE_DIR', None)

    def get_cache_dir(self):
        """Retourne le répertoire de cache des modèles"""
        return self.models_cache_dir


class ModelManager(BaseAIService):
    """Gestionnaire centralisé pour tous les modèles AI"""

    _instance = None
    _models = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            super().__init__()
            self.initialized = True

    def load_tinyllama(self):
        """Charge le modèle TinyLLaMA"""
        if 'tinyllama' not in self._models:
            try:
                logger.info("Chargement de TinyLLaMA...")
                model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

                tokenizer = AutoTokenizer.from_pretrained(
                    model_name,
                    cache_dir=self.models_cache_dir
                )

                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    cache_dir=self.models_cache_dir,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )

                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token

                self._models['tinyllama'] = {
                    'model': model,
                    'tokenizer': tokenizer
                }

                logger.info("TinyLLaMA chargé avec succès")

            except Exception as e:
                logger.error(f"Erreur lors du chargement de TinyLLaMA: {e}")
                raise

        return self._models['tinyllama']['model'], self._models['tinyllama']['tokenizer']

    def load_bge_m3(self):
        """Charge le modèle BGE-M3 sans FlagEmbedding"""
        if 'bge_m3' not in self._models:
            try:
                logger.info("Chargement de BGE-M3 via Transformers...")

                tokenizer = AutoTokenizer.from_pretrained(
                    "BAAI/bge-m3",
                    cache_dir=self.models_cache_dir,
                    trust_remote_code=True
                )
                model = AutoModel.from_pretrained(
                    "BAAI/bge-m3",
                    cache_dir=self.models_cache_dir,
                    trust_remote_code=True
                )
                model.eval()
                model.to(self.device)

                self._models['bge_m3'] = {
                    'tokenizer': tokenizer,
                    'model': model
                }

                logger.info("BGE-M3 chargé avec succès via Transformers")

            except Exception as e:
                logger.error(f"Erreur lors du chargement de BGE-M3: {e}")
                raise

        return self._models['bge_m3']

    def load_sentence_bert(self):
        """Charge Sentence-BERT"""
        if 'sentence_bert' not in self._models:
            try:
                logger.info("Chargement de Sentence-BERT...")
                self._models['sentence_bert'] = SentenceTransformer(
                    'all-MiniLM-L6-v2',
                    cache_folder=self.models_cache_dir,
                    device=self.device
                )
                logger.info("Sentence-BERT chargé avec succès")

            except Exception as e:
                logger.error(f"Erreur lors du chargement de Sentence-BERT: {e}")
                raise

        return self._models['sentence_bert']

    def load_paddle_ocr(self, lang='en'):
        """Charge PaddleOCR"""
        ocr_key = f'paddle_ocr_{lang}'
        if ocr_key not in self._models:
            try:
                logger.info(f"Chargement de PaddleOCR ({lang})...")
                self._models[ocr_key] = PaddleOCR(
                    use_angle_cls=True,
                    lang=lang,
                    use_gpu=True if self.device == "cuda" else False,
                    show_log=False
                )
                logger.info("PaddleOCR chargé avec succès")

            except Exception as e:
                logger.error(f"Erreur lors du chargement de PaddleOCR: {e}")
                raise

        return self._models[ocr_key]

    def get_model_status(self):
        """Retourne le statut des modèles chargés"""
        return {
            'tinyllama_loaded': 'tinyllama' in self._models,
            'bge_m3_loaded': 'bge_m3' in self._models,
            'sentence_bert_loaded': 'sentence_bert' in self._models,
            'paddle_ocr_loaded': any(key.startswith('paddle_ocr_') for key in self._models.keys()),
            'device': self.device,
            'loaded_models': list(self._models.keys())
        }

    def unload_models(self):
        """Décharge tous les modèles"""
        logger.info("Déchargement des modèles...")

        for key in list(self._models.keys()):
            del self._models[key]

        self._models.clear()

        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        logger.info("Modèles déchargés")


# Instance globale
model_manager = ModelManager()
class BaseAIService(ABC):
    def __init__(self):
        self.model_path = None
        self.model = None
        self.is_loaded = False

    @abstractmethod
    def load_model(self):
        pass

    @abstractmethod
    def process(self, input_data):
        pass

    def ensure_model_loaded(self):
        if not self.is_loaded:
            self.load_model()