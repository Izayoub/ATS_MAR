from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Initialise le service de matching CV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-reload',
            action='store_true',
            help='Force le rechargement du modèle',
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Lance les tests après initialisation',
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 Initialisation du service de matching CV...")

        try:
            from ai_engine.services.matching_service import django_matching_service

            # Vérification de l'état
            health = django_matching_service.get_health_status()

            if health['model_ready']:
                self.stdout.write(
                    self.style.SUCCESS('✅ Service déjà initialisé et prêt')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('⚠️ Service en cours d\'initialisation...')
                )

                # Attendre que le modèle soit prêt (timeout 60s)
                import time
                timeout = 60
                start_time = time.time()

                while time.time() - start_time < timeout:
                    health = django_matching_service.get_health_status()
                    if health['model_ready']:
                        break
                    time.sleep(2)
                    self.stdout.write('.', ending='')

                if health['model_ready']:
                    self.stdout.write(
                        self.style.SUCCESS('\n✅ Service initialisé avec succès')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('\n❌ Timeout initialisation service')
                    )
                    return

            # Affichage du statut
            self.stdout.write("\n📊 Statut du service:")
            self.stdout.write(f"   Modèle: {'✅ Prêt' if health['model_ready'] else '❌ Erreur'}")
            self.stdout.write(f"   Cache: {'✅ Activé' if health['cache_enabled'] else '❌ Désactivé'}")
            self.stdout.write(f"   Batch max: {health['max_batch_size']} CV")

            # Tests optionnels
            if options['test']:
                self.stdout.write("\n🧪 Lancement des tests...")
                from ai_engine.services.matching_service import run_simplified_tests
                run_simplified_tests()
                self.stdout.write(
                    self.style.SUCCESS('✅ Tests terminés')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur initialisation: {e}')
            )
