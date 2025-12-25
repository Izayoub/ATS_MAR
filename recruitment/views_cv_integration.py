# recruitment/views_cv_integration.py
"""
Vues Django pour l'intégration CV Parser
"""

import json
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from .models import Candidate
from .cv_integration import get_cv_integration_instance
from ai_engine.services.cv_parser import CVParser  # Ajustez selon votre structure

logger = logging.getLogger(__name__)



@permission_classes([AllowAny])
def cv_upload_and_parse(request):
    """
    Vue pour uploader et parser un CV
    """
    if request.method == 'POST':
        if 'cv_file' not in request.FILES:
            messages.error(request, "Aucun fichier sélectionné")
            return redirect('cv_upload_and_parse')

        cv_file = request.FILES['cv_file']

        # Vérifier le type de fichier
        if not cv_file.name.lower().endswith('.pdf'):
            messages.error(request, "Seuls les fichiers PDF sont acceptés")
            return redirect('cv_upload_and_parse')

        try:
            # Sauvegarder temporairement le fichier
            temp_path = default_storage.save(f'temp_cvs/{cv_file.name}', cv_file)
            full_path = default_storage.path(temp_path)

            # Initialiser l'intégration CV
            cv_parser = CVParser()
            cv_integration = get_cv_integration_instance(cv_parser)

            # Traiter le CV
            result = cv_integration.process_cv_file_to_candidate(
                cv_file_path=full_path,
                save_to_db=True
            )

            # Nettoyer le fichier temporaire
            default_storage.delete(temp_path)

            if result['success']:
                candidate = result['candidate']
                action = 'créé' if result['created'] else 'mis à jour'

                messages.success(
                    request,
                    f"Candidat {action} avec succès : {candidate.first_name} {candidate.last_name}"
                )

                # Rediriger vers le profil du candidat
                return redirect('candidate_detail', pk=candidate.id)
            else:
                messages.error(request, f"Erreur lors du parsing : {result.get('error', 'Erreur inconnue')}")

        except Exception as e:
            logger.error(f"Erreur upload CV : {e}")
            messages.error(request, f"Erreur lors du traitement : {str(e)}")

    return render(request, 'recruitment/cv_upload.html')


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def cv_text_parse_ajax(request):
    """
    Vue AJAX pour parser du texte CV directement
    """
    try:
        data = json.loads(request.body)
        cv_text = data.get('cv_text', '').strip()

        if not cv_text:
            return JsonResponse({
                'success': False,
                'error': 'Texte CV vide'
            })

        # Initialiser l'intégration CV
        cv_parser = CVParser()
        cv_integration = get_cv_integration_instance(cv_parser)

        # Traiter le texte CV
        result = cv_integration.process_cv_text_to_candidate(
            cv_text=cv_text,
            filename="text_direct.txt",
            save_to_db=data.get('save_to_db', True)
        )

        if result['success']:
            response_data = {
                'success': True,
                'created': result['created'],
                'parsing_confidence': result['parsing_confidence'],
                'extracted_data': result['extracted_data']
            }

            if result.get('candidate'):
                response_data.update({
                    'candidate_id': result['candidate'].id,
                    'candidate_name': f"{result['candidate'].first_name} {result['candidate'].last_name}",
                    'candidate_email': result['candidate'].email
                })

            return JsonResponse(response_data)
        else:
            return JsonResponse({
                'success': False,
                'error': result.get('error', 'Erreur inconnue')
            })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Format JSON invalide'
        })
    except Exception as e:
        logger.error(f"Erreur parsing texte CV : {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def cv_batch_upload(request):
    """
    Vue pour le traitement en lot de CVs
    """
    if request.method == 'POST':
        # Vérifier qu'on a des fichiers
        files = request.FILES.getlist('cv_files')

        if not files:
            messages.error(request, "Aucun fichier sélectionné")
            return redirect('cv_batch_upload')

        # Filtrer les fichiers PDF
        pdf_files = [f for f in files if f.name.lower().endswith('.pdf')]

        if not pdf_files:
            messages.error(request, "Aucun fichier PDF trouvé")
            return redirect('cv_batch_upload')

        try:
            # Initialiser l'intégration CV
            cv_parser = CVParser()
            cv_integration = get_cv_integration_instance(cv_parser)

            results = {
                'total_files': len(pdf_files),
                'processed': 0,
                'created_candidates': 0,
                'updated_candidates': 0,
                'errors': 0,
                'details': []
            }

            # Traiter chaque fichier
            for cv_file in pdf_files:
                try:
                    # Sauvegarder temporairement
                    temp_path = default_storage.save(f'temp_cvs/{cv_file.name}', cv_file)
                    full_path = default_storage.path(temp_path)

                    # Traiter le CV
                    result = cv_integration.process_cv_file_to_candidate(
                        cv_file_path=full_path,
                        save_to_db=True
                    )

                    # Nettoyer
                    default_storage.delete(temp_path)

                    results['processed'] += 1

                    if result['success']:
                        if result['created']:
                            results['created_candidates'] += 1
                        else:
                            results['updated_candidates'] += 1

                        candidate = result['candidate']
                        results['details'].append({
                            'filename': cv_file.name,
                            'success': True,
                            'candidate_name': f"{candidate.first_name} {candidate.last_name}",
                            'candidate_email': candidate.email,
                            'created': result['created']
                        })
                    else:
                        results['errors'] += 1
                        results['details'].append({
                            'filename': cv_file.name,
                            'success': False,
                            'error': result.get('error', 'Erreur inconnue')
                        })

                except Exception as e:
                    results['errors'] += 1
                    results['details'].append({
                        'filename': cv_file.name,
                        'success': False,
                        'error': str(e)
                    })
                    logger.error(f"Erreur traitement {cv_file.name}: {e}")

            # Messages de retour
            if results['created_candidates'] > 0:
                messages.success(request, f"{results['created_candidates']} nouveaux candidats créés")

            if results['updated_candidates'] > 0:
                messages.info(request, f"{results['updated_candidates']} candidats mis à jour")

            if results['errors'] > 0:
                messages.warning(request, f"{results['errors']} fichiers en erreur")

            # Stocker les résultats dans la session pour affichage détaillé
            request.session['batch_results'] = results

            return redirect('cv_batch_results')

        except Exception as e:
            logger.error(f"Erreur traitement en lot : {e}")
            messages.error(request, f"Erreur lors du traitement en lot : {str(e)}")

    return render(request, 'recruitment/cv_batch_upload.html')


@login_required
def cv_batch_results(request):
    """
    Vue pour afficher les résultats du traitement en lot
    """
    results = request.session.get('batch_results', None)

    if not results:
        messages.warning(request, "Aucun résultat de traitement en lot trouvé")
        return redirect('cv_batch_upload')

    # Calculer le taux de réussite
    success_rate = 0
    if results['total_files'] > 0:
        success_rate = ((results['created_candidates'] + results['updated_candidates']) /
                        results['total_files'] * 100)

    results['success_rate'] = round(success_rate, 1)

    # Nettoyer la session
    if 'batch_results' in request.session:
        del request.session['batch_results']

    return render(request, 'recruitment/cv_batch_results.html', {
        'results': results
    })


@login_required
def candidate_update_from_cv(request, pk):
    """
    Vue pour mettre à jour un candidat existant depuis un nouveau CV
    """
    try:
        candidate = Candidate.objects.get(pk=pk)
    except Candidate.DoesNotExist:
        messages.error(request, "Candidat introuvable")
        return redirect('candidate_list')

    if request.method == 'POST':
        if 'cv_file' in request.FILES:
            cv_file = request.FILES['cv_file']

            if not cv_file.name.lower().endswith('.pdf'):
                messages.error(request, "Seuls les fichiers PDF sont acceptés")
                return redirect('candidate_update_from_cv', pk=pk)

            try:
                # Sauvegarder temporairement
                temp_path = default_storage.save(f'temp_cvs/{cv_file.name}', cv_file)
                full_path = default_storage.path(temp_path)

                # Initialiser l'intégration CV
                cv_parser = CVParser()
                cv_integration = get_cv_integration_instance(cv_parser)

                # Forcer la mise à jour en utilisant l'email du candidat existant
                result = cv_integration.process_cv_file_to_candidate(
                    cv_file_path=full_path,
                    save_to_db=True
                )

                # Nettoyer
                default_storage.delete(temp_path)

                if result['success']:
                    messages.success(request, "Candidat mis à jour avec succès depuis le nouveau CV")
                    return redirect('candidate_detail', pk=candidate.id)
                else:
                    messages.error(request, f"Erreur lors de la mise à jour : {result.get('error')}")

            except Exception as e:
                logger.error(f"Erreur mise à jour candidat {pk} : {e}")
                messages.error(request, f"Erreur lors de la mise à jour : {str(e)}")

    return render(request, 'recruitment/candidate_update_cv.html', {
        'candidate': candidate
    })


@login_required
@require_http_methods(["GET"])
def candidate_parsed_data_view(request, pk):
    """
    Vue pour afficher les données parsées d'un candidat
    """
    try:
        candidate = Candidate.objects.get(pk=pk)
    except Candidate.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Candidat introuvable'
        })

    return JsonResponse({
        'success': True,
        'candidate_id': candidate.id,
        'candidate_name': f"{candidate.first_name} {candidate.last_name}",
        'parsed_data': candidate.cv_parsed_data,
        'skills_extracted': candidate.skills_extracted,
        'experience_years': candidate.experience_years,
        'education_level': candidate.education_level,
        'languages': candidate.languages,
        'ai_summary': candidate.ai_summary
    })


# === VUES DE STATISTIQUES ===

@login_required
def cv_parsing_stats(request):
    """
    Vue pour afficher les statistiques de parsing CV
    """
    from django.db.models import Count, Q
    from django.utils import timezone
    from datetime import timedelta

    # Statistiques générales
    total_candidates = Candidate.objects.count()
    candidates_with_cv = Candidate.objects.exclude(cv_file='').count()
    candidates_with_parsed_data = Candidate.objects.exclude(cv_parsed_data={}).count()

    # Statistiques par période (30 derniers jours)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_candidates = Candidate.objects.filter(created_at__gte=thirty_days_ago).count()

    # Répartition par niveau d'éducation
    education_stats = (
        Candidate.objects
        .exclude(education_level='')
        .values('education_level')
        .annotate(count=Count('id'))
        .order_by('-count')
    )

    # Répartition par années d'expérience
    experience_ranges = [
        ('0-2 ans', Q(experience_years__gte=0, experience_years__lte=2)),
        ('3-5 ans', Q(experience_years__gte=3, experience_years__lte=5)),
        ('6-10 ans', Q(experience_years__gte=6, experience_years__lte=10)),
        ('10+ ans', Q(experience_years__gt=10)),
    ]

    experience_stats = []
    for label, query in experience_ranges:
        count = Candidate.objects.filter(query).count()
        experience_stats.append({'range': label, 'count': count})

    # Top compétences
    from collections import Counter
    all_skills = []
    for candidate in Candidate.objects.exclude(skills_extracted=[]):
        all_skills.extend(candidate.skills_extracted)

    top_skills = Counter(all_skills).most_common(10)

    context = {
        'total_candidates': total_candidates,
        'candidates_with_cv': candidates_with_cv,
        'candidates_with_parsed_data': candidates_with_parsed_data,
        'parsing_rate': round((candidates_with_parsed_data / total_candidates * 100), 1) if total_candidates > 0 else 0,
        'recent_candidates': recent_candidates,
        'education_stats': education_stats,
        'experience_stats': experience_stats,
        'top_skills': [{'skill': skill, 'count': count} for skill, count in top_skills]
    }

    return render(request, 'recruitment/cv_parsing_stats.html', context)