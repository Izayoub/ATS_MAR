from django.core.management.base import BaseCommand
import json
import sys


class Command(BaseCommand):
    help = 'Teste le matching depuis la ligne de commande'

    def add_arguments(self, parser):
        parser.add_argument('cv_file', type=str, help='Fichier JSON du CV')
        parser.add_argument('job_file', type=str, help='Fichier JSON du job')
        parser.add_argument('--output', type=str, help='Fichier de sortie JSON')
        parser.add_argument('--no-cache', action='store_true', help='Désactive le cache')

    def handle(self, *args, **options):
        try:
            # Lecture des fichiers
            with open(options['cv_file'], 'r', encoding='utf-8') as f:
                cv_data = json.load(f)

            with open(options['job_file'], 'r', encoding='utf-8') as f:
                job_data = json.load(f)

            # Matching
            from ai_engine.services.matching_service import django_matching_service

            result = django_matching_service.match_cv_to_job(
                cv_data,
                job_data,
                cv_id=options['cv_file'],
                use_cache=not options['no_cache']
            )

            # Affichage
            self.stdout.write(f"🎯 Résultat Matching:")
            self.stdout.write(f"   Score: {result['total_score']}/100")
            self.stdout.write(f"   Domaine: {result['cv_domain']}")
            self.stdout.write(f"   Action: {result['interpretation']['action']}")
            self.stdout.write(f"   Temps: {result['execution_time_ms']}ms")

            if result.get('from_cache'):
                self.stdout.write("   📋 Résultat du cache")

            # Export optionnel
            if options['output']:
                with open(options['output'], 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                self.stdout.write(f"✅ Résultat exporté: {options['output']}")

        except FileNotFoundError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Fichier non trouvé: {e}')
            )
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f'❌ JSON invalide: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur: {e}')
            )

