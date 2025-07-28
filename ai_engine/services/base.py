import logging
from abc import ABC, abstractmethod
from django.conf import settings

logger = logging.getLogger(__name__)


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