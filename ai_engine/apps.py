from django.apps import AppConfig


class AiEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_engine'
    verbose_name = 'AI Engine - Service Matching CV'

    def ready(self):
        """Initialisation du service de matching au démarrage"""
        try:
            # Import ici pour éviter les imports circulaires
            from ai_engine.services.matching_service import model_manager

            if model_manager.is_ready():
                logger.info("✅ Service de matching CV initialisé avec succès")
            else:
                logger.warning("⚠️ Service de matching en cours de chargement...")

        except Exception as e:
            logger.error(f"❌ Erreur initialisation service matching: {e}")
