# ai_engine/tests/conftest.py
import sys
from unittest.mock import MagicMock

# Simulation de torch pour éviter l'import
sys.modules['torch'] = MagicMock()

# Idem pour les modules transformers si besoin
sys.modules['transformers'] = MagicMock()
