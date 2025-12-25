# recruitment/views.py - Architecture Unifiée
import json
import time
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Dict, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Q, Count, Avg, Prefetch
from django.core.cache import cache
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import Company
from .models import JobOffer, Candidate, Application, Interview, CandidateNote, MatchingCache,GroupCandidate
from .serializers import (
    JobOfferListSerializer, JobOfferDetailSerializer,
    CandidateListSerializer, CandidateDetailSerializer, CandidateMatchingSerializer,
    ApplicationUnifiedSerializer, InterviewUnifiedSerializer, CandidateNoteSerializer,
    MatchingResultSerializer, BatchMatchingResultSerializer, MatchingAnalyticsSerializer,GroupCandidateListSerializer, GroupCandidateDetailSerializer,
    GroupCandidateCreateUpdateSerializer, GroupCandidateSummarySerializer,CandidatGroupeMembershipSerializer,CandidatePendingSerializer,CandidateUploadSerializer
)

# Import du service de matching refactorisé
from ai_engine.services.matching_service import matching_service

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


# ==========================================
# ViewSets Unifiés et Optimisés
# ==========================================

class CandidateViewSet(viewsets.ModelViewSet):
    """ViewSet unifié pour la gestion des candidats"""
    queryset = Candidate.objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    filterset_fields = ['city', 'experience_years', 'education_level', 'status']

    def get_queryset(self):
        queryset = Candidate.objects.select_related().prefetch_related(
            'applications__job_offer__company',
            'notes'
        )

        # Filtre par compétences (nouveau système unifié)
        skills = self.request.query_params.get('skills')
        if skills:
            skill_list = [s.strip().lower() for s in skills.split(',')]
            queryset = queryset.filter(
                Q(technical_skills__overlap=skill_list) |
                Q(soft_skills__overlap=skill_list)
            )

        # Filtre par disponibilité des embeddings
        has_embeddings = self.request.query_params.get('has_embeddings')
        if has_embeddings:
            if has_embeddings.lower() in ['true', '1', 'yes']:
                queryset = queryset.exclude(cv_embeddings={}).exclude(embeddings_generated_at__isnull=True)
            elif has_embeddings.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(Q(cv_embeddings={}) | Q(embeddings_generated_at__isnull=True))

        # Recherche textuelle
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(cv_text__icontains=search) |
                Q(ai_summary__icontains=search) |
                Q(email__icontains=search)
            )

        # Filtre par score de matching
        min_score = self.request.query_params.get('min_match_score')
        if min_score:
            try:
                min_score_float = float(min_score) / 100
                queryset = queryset.filter(global_match_score__gte=min_score_float)
            except ValueError:
                pass

        # Filtre par statut d'extraction
        is_extracted = self.request.query_params.get('is_extracted')
        if is_extracted:
            if is_extracted.lower() in ['true', '1', 'yes']:
                queryset = queryset.filter(is_extracted=True)
            elif is_extracted.lower() in ['false', '0', 'no']:
                queryset = queryset.filter(is_extracted=False)

        return queryset.annotate(
            applications_count=Count('applications')
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CandidateDetailSerializer
        elif self.action in ['find_matching_jobs', 'matching_analysis']:
            return CandidateMatchingSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CandidateCreateUpdateSerializer
        elif self.action == 'embeddings_detail':
            return CandidateEmbeddingsSerializer
        return CandidateListSerializer

    def create(self, request, *args, **kwargs):
        """Création d'un candidat avec validation"""
        try:
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                # Sauvegarder le candidat
                candidate = serializer.save(status='new', is_extracted=True)

                logger.info(f"Candidat créé avec succès: {candidate.id} - {candidate.full_name}")

                # Retourner les détails complets
                response_serializer = CandidateDetailSerializer(candidate)
                return Response({
                    'success': True,
                    'message': 'Candidat créé avec succès',
                    'candidate': response_serializer.data
                }, status=status.HTTP_201_CREATED)

            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Erreur lors de la création du candidat: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        """Mise à jour complète d'un candidat"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)

            if serializer.is_valid():
                # Sauvegarder les modifications
                candidate = serializer.save()

                logger.info(f"Candidat mis à jour avec succès: {candidate.id} - {candidate.full_name}")

                # Retourner les détails complets mis à jour
                response_serializer = CandidateDetailSerializer(candidate)
                return Response({
                    'success': True,
                    'message': 'Candidat mis à jour avec succès',
                    'candidate': response_serializer.data
                })

            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du candidat {kwargs.get('pk')}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, *args, **kwargs):
        """Mise à jour partielle d'un candidat"""
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """Récupération détaillée d'un candidat avec données optimisées"""
        instance = self.get_object()

        # Précharger les données liées pour éviter les N+1 queries
        instance = Candidate.objects.select_related().prefetch_related(
            Prefetch('applications',
                     queryset=Application.objects.select_related('job_offer', 'job_offer__company')
                     .order_by('-applied_at')[:10],
                     to_attr='recent_applications_prefetch'),
            'notes__author'
        ).get(pk=instance.pk)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_cv(self, request):
        """Upload d'un CV et création d'un candidat en attente d'extraction"""
        try:
            # Vérifier qu'un fichier est bien présent
            if 'cv_file' not in request.FILES:
                return Response({
                    'success': False,
                    'error': 'Aucun fichier CV fourni',
                    'available_files': list(request.FILES.keys())
                }, status=status.HTTP_400_BAD_REQUEST)

            cv_file = request.FILES['cv_file']

            # Validation du type de fichier
            allowed_extensions = ('.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png')
            if not cv_file.name.lower().endswith(allowed_extensions):
                return Response({
                    'success': False,
                    'error': f'Type de fichier non supporté: {cv_file.name}',
                    'allowed_types': list(allowed_extensions)
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer = CandidateUploadSerializer(data=request.data)

            if serializer.is_valid():
                candidate = serializer.save()

                logger.info(f"CV uploaded for candidate {candidate.id}: {candidate.cv_file_path}")

                return Response({
                    'success': True,
                    'message': 'CV uploadé avec succès',
                    'candidate': {
                        'id': candidate.id,
                        'cv_file_path': candidate.cv_file_path,
                        'cv_file_url': candidate.cv_file.url if candidate.cv_file else None,
                        'status': candidate.status,
                        'upload_date': candidate.created_at.isoformat(),
                        'file_size': cv_file.size,
                        'file_type': cv_file.content_type
                    }
                }, status=status.HTTP_201_CREATED)

            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error uploading CV: {e}")
            return Response({
                'success': False,
                'error': f'Erreur lors de l\'upload du CV: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def pending_extraction(self, request):
        """Liste des candidats en attente d'extraction"""
        try:
            pending_candidates = Candidate.objects.filter(
                status='pending_extraction',
                is_extracted=False
            ).order_by('-created_at')

            paginator = Paginator(pending_candidates, 20)
            page = paginator.get_page(request.query_params.get('page', 1))

            serializer = CandidatePendingSerializer(page, many=True)

            return Response({
                'success': True,
                'candidates': serializer.data,
                'pagination': {
                    'current_page': page.number,
                    'total_pages': paginator.num_pages,
                    'total_count': paginator.count,
                    'has_next': page.has_next(),
                    'has_previous': page.has_previous()
                }
            })

        except Exception as e:
            logger.error(f"Error getting pending candidates: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def extract_cv_data(self, request, pk=None):
        """Extraire les données du CV et remplir les champs (pour plus tard)"""
        try:
            candidate = self.get_object()

            if candidate.is_extracted:
                return Response({
                    'success': False,
                    'message': 'Les données ont déjà été extraites pour ce candidat'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not candidate.cv_file:
                return Response({
                    'success': False,
                    'message': 'Aucun CV trouvé pour ce candidat'
                }, status=status.HTTP_400_BAD_REQUEST)

            # TODO: Ici vous ajouterez votre logique d'extraction
            # Pour l'instant, on marque juste comme prêt pour extraction

            return Response({
                'success': True,
                'message': 'Candidat prêt pour extraction',
                'candidate_id': candidate.id,
                'cv_file_path': candidate.cv_file_path,
                'has_embeddings': candidate.has_embeddings()
            })

        except Exception as e:
            logger.error(f"Error preparing extraction for candidate {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def embeddings_detail(self, request, pk=None):
        """Détails des embeddings d'un candidat"""
        try:
            candidate = self.get_object()
            serializer = CandidateEmbeddingsSerializer(candidate)

            return Response({
                'success': True,
                'embeddings': serializer.data
            })

        except Exception as e:
            logger.error(f"Error getting embeddings for candidate {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def generate_embeddings(self, request, pk=None):
        """Générer les embeddings pour un candidat"""
        try:
            candidate = self.get_object()

            if not candidate.cv_text:
                return Response({
                    'success': False,
                    'message': 'Aucun texte de CV disponible pour générer les embeddings'
                }, status=status.HTTP_400_BAD_REQUEST)

            # TODO: Ici vous ajouterez votre logique de génération d'embeddings
            # Pour l'instant, on simule la génération

            # Exemple de structure d'embeddings
            sample_embeddings = {
                'profile_summary': [],  # Vous remplirez avec vos vrais embeddings
                'experience': [],
                'skills': [],
                'education': [],
                'full_cv': []
            }

            candidate.cv_embeddings = sample_embeddings
            candidate.mark_embeddings_generated()

            logger.info(f"Embeddings generated for candidate {candidate.id}")

            return Response({
                'success': True,
                'message': 'Embeddings générés avec succès',
                'candidate_id': candidate.id,
                'sections_generated': list(sample_embeddings.keys()),
                'generated_at': candidate.embeddings_generated_at.isoformat()
            })

        except Exception as e:
            logger.error(f"Error generating embeddings for candidate {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def embedding_section(self, request, pk=None):
        """Récupérer les embeddings d'une section spécifique"""
        try:
            candidate = self.get_object()
            section_name = request.query_params.get('section')

            if not section_name:
                return Response({
                    'success': False,
                    'error': 'Paramètre "section" requis'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not candidate.has_embeddings():
                return Response({
                    'success': False,
                    'message': 'Aucun embedding disponible pour ce candidat'
                }, status=status.HTTP_404_NOT_FOUND)

            section_embeddings = candidate.get_embedding_section(section_name)

            return Response({
                'success': True,
                'candidate_id': candidate.id,
                'section': section_name,
                'embeddings': section_embeddings,
                'vector_count': len(section_embeddings) if isinstance(section_embeddings, list) else 0
            })

        except Exception as e:
            logger.error(f"Error getting embedding section for candidate {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def embeddings_stats(self, request):
        """Statistiques globales sur les embeddings"""
        try:
            total_candidates = Candidate.objects.count()
            candidates_with_embeddings = Candidate.objects.exclude(
                cv_embeddings={}
            ).exclude(
                embeddings_generated_at__isnull=True
            ).count()

            recent_embeddings = Candidate.objects.filter(
                embeddings_generated_at__gte=timezone.now() - timedelta(days=7)
            ).count()

            return Response({
                'success': True,
                'stats': {
                    'total_candidates': total_candidates,
                    'candidates_with_embeddings': candidates_with_embeddings,
                    'coverage_percentage': round(
                        (candidates_with_embeddings / total_candidates * 100) if total_candidates > 0 else 0,
                        2
                    ),
                    'recent_embeddings_generated': recent_embeddings,
                    'candidates_without_embeddings': total_candidates - candidates_with_embeddings
                }
            })

        except Exception as e:
            logger.error(f"Error getting embeddings stats: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def bulk_upload(self, request):
        """Upload multiple CVs à la fois"""
        try:
            files = request.FILES.getlist('cv_files')

            if not files:
                return Response({
                    'success': False,
                    'error': 'Aucun fichier fourni',
                    'debug_info': {
                        'files_keys': list(request.FILES.keys()),
                        'expected_key': 'cv_files',
                        'help': 'Utilisez le champ "cv_files" pour envoyer plusieurs fichiers'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            results = []
            errors = []
            allowed_extensions = ('.pdf', '.txt', '.doc', '.docx', '.jpg', '.jpeg', '.png')

            for i, file in enumerate(files):
                try:
                    # Validation du type de fichier
                    if not file.name.lower().endswith(allowed_extensions):
                        errors.append(
                            f"Fichier {file.name}: Format non supporté (autorisés: {', '.join(allowed_extensions)})")
                        continue

                    # Validation de la taille (exemple: max 10MB)
                    max_size = 10 * 1024 * 1024  # 10MB
                    if file.size > max_size:
                        errors.append(f"Fichier {file.name}: Trop volumineux ({file.size} bytes, max {max_size})")
                        continue

                    # Créer le candidat avec un email unique
                    timestamp = int(timezone.now().timestamp() * 1000)
                    temp_email = f"temp_{timestamp}_{i}@upload.temp"

                    candidate = Candidate.objects.create(
                        first_name='N/A',
                        last_name='N/A',
                        email=temp_email,
                        cv_file=file,
                        cv_file_path=file.name,
                        status='pending_extraction',
                        is_extracted=False
                    )

                    results.append({
                        'candidate_id': candidate.id,
                        'filename': file.name,
                        'cv_file_url': candidate.cv_file.url,
                        'status': 'uploaded',
                        'file_size': file.size,
                        'file_type': file.content_type
                    })

                    logger.info(f"Bulk upload: Created candidate {candidate.id} for file {file.name}")

                except Exception as e:
                    logger.error(f"Error processing file {file.name}: {e}")
                    errors.append(f"Fichier {file.name}: {str(e)}")

            return Response({
                'success': True,
                'uploaded_count': len(results),
                'error_count': len(errors),
                'results': results,
                'errors': errors,
                'summary': {
                    'total_files_received': len(files),
                    'successful_uploads': len(results),
                    'failed_uploads': len(errors)
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in bulk upload: {e}")
            return Response({
                'success': False,
                'error': f'Erreur lors de l\'upload en lot: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class JobOfferViewSet(viewsets.ModelViewSet):
    """ViewSet unifié pour la gestion des offres d'emploi"""
    queryset = JobOffer.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'experience_level', 'contract_type', 'remote_allowed']
    search_fields = ['title', 'description', 'requirements']

    def get_queryset(self):
        queryset = JobOffer.objects.filter(
            company=self.request.user.company
        ).select_related('company', 'created_by').prefetch_related(
            'applications__candidate'
        ).order_by('-created_at')

        # Filtres additionnels
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(requirements__icontains=search)
            )

        if self.action == "list":
            return queryset.filter(status="active").annotate(
                applications_count=Count('applications'),
                top_match_score=Avg('applications__ai_match_score')
            )

        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return JobOfferDetailSerializer
        elif self.action in ['matching_config']:
            return JobOfferMatchingConfigSerializer
        return JobOfferListSerializer

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            company=self.request.user.company
        )

    def perform_update(self, serializer):
        """Invalider le cache lors de la modification"""
        job_offer = serializer.save()

        # If matching service is available, invalidate cache
        if 'matching_weights' in serializer.validated_data or 'system_prompt' in serializer.validated_data:
            try:
                # FIXED: Uncomment when matching_service is available
                # invalidated_count = matching_service.invalidate_cache(job_id=job_offer.id)
                # logger.info(f"Invalidated {invalidated_count} cache entries for job {job_offer.id}")
                logger.info(f"Matching config updated for job {job_offer.id}")
            except Exception as e:
                logger.warning(f"Could not invalidate cache for job {job_offer.id}: {e}")
    def retrieve(self, request, *args, **kwargs):
        """Récupération détaillée d'une offre avec données optimisées"""
        instance = self.get_object()

        # Précharger les données liées
        instance = JobOffer.objects.select_related('company', 'created_by').prefetch_related(
            Prefetch('applications',
                     queryset=Application.objects.select_related('candidate')
                     .order_by('-applied_at')[:15],
                     to_attr='recent_apps_prefetch')
        ).get(pk=instance.pk)

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'patch'])
    def matching_config(self, request, pk=None):
        """Gestion de la configuration de matching personnalisée"""
        job_offer = self.get_object()

        if request.method == 'GET':
            serializer = JobOfferMatchingConfigSerializer(job_offer)
            return Response({
                'success': True,
                'config': serializer.data,
                'default_weights': {
                    'technical_skills': 0.35,
                    'soft_skills': 0.15,
                    'experience': 0.30,
                    'education': 0.20
                }
            })

        elif request.method == 'PATCH':
            serializer = JobOfferMatchingConfigSerializer(
                job_offer, data=request.data, partial=True
            )

            if serializer.is_valid():
                old_weights = job_offer.matching_weights.copy() if job_offer.matching_weights else {}
                old_prompt = job_offer.system_prompt

                updated_job = serializer.save()

                # Invalider le cache si la config a changé
                if (updated_job.matching_weights != old_weights or
                        updated_job.system_prompt != old_prompt):
                    try:
                        # FIXED: Uncomment when matching_service is available
                        # invalidated_count = matching_service.invalidate_cache(job_id=updated_job.id)
                        invalidated_count = 0  # Placeholder

                        return Response({
                            'success': True,
                            'message': f'Configuration mise à jour. {invalidated_count} entrées de cache invalidées.',
                            'config': JobOfferMatchingConfigSerializer(updated_job).data
                        })
                    except Exception as e:
                        logger.error(f"Error invalidating cache: {e}")

                return Response({
                    'success': True,
                    'message': 'Configuration mise à jour.',
                    'config': serializer.data
                })

            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reset_matching_config(self, request, pk=None):
        """Réinitialise la configuration de matching aux valeurs par défaut"""
        job_offer = self.get_object()

        job_offer.matching_weights = {}
        job_offer.system_prompt = ''
        job_offer.save()

        # Invalider le cache
        try:
            # FIXED: Uncomment when matching_service is available
            # invalidated_count = matching_service.invalidate_cache(job_id=job_offer.id)
            invalidated_count = 0  # Placeholder
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            invalidated_count = 0

        return Response({
            'success': True,
            'message': f'Configuration réinitialisée. {invalidated_count} entrées de cache invalidées.',
            'config': JobOfferMatchingConfigSerializer(job_offer).data
        })

    @action(detail=True, methods=['post'])
    def find_matching_candidates(self, request, pk=None):
        """Trouve les meilleurs candidats pour une offre - ENDPOINT UNIQUE"""
        start_time = time.time()

        try:
            job_offer = self.get_object()
            top_n = min(int(request.data.get('top_n', 15)), 50)
            min_score = float(request.data.get('min_score', 0.0))
            exclude_applied = request.data.get('exclude_applied', True)
            use_custom_config = request.data.get('use_custom_config', True)

            # FIXED: Mock response when matching service is not available
            # Replace with actual service call when available
            try:
                # matches = matching_service.find_matches_for_job(...)
                # For now, return mock data
                matches = []

                # Get some candidates as example
                candidates = Candidate.objects.filter(
                    company=self.request.user.company
                )[:top_n]

                formatted_matches = []
                for candidate in candidates:
                    # Check if already applied
                    already_applied = Application.objects.filter(
                        candidate=candidate, job_offer=job_offer
                    ).exists()

                    if exclude_applied and already_applied:
                        continue

                    formatted_matches.append({
                        'candidate_id': candidate.id,
                        'candidate_name': candidate.full_name,
                        'email': candidate.email,
                        'phone': getattr(candidate, 'phone', ''),
                        'city': getattr(candidate, 'city', ''),
                        'linkedin_url': getattr(candidate, 'linkedin_url', ''),
                        'experience_years': getattr(candidate, 'experience_years', 0),
                        'education_level': getattr(candidate, 'education_level', ''),
                        'technical_skills': getattr(candidate, 'technical_skills', [])[:7],
                        'soft_skills': getattr(candidate, 'soft_skills', [])[:4],
                        'overall_score': 75.0,  # Mock score
                        'recommendation': "Good potential match",  # Mock recommendation
                        'confidence_level': 'medium',  # Mock confidence
                        'already_applied': already_applied,
                        'application_status': None,
                        'breakdown': {
                            'technical_skills': {
                                'score': 80.0,
                                'confidence': 0.8,
                                'weight_used': 0.35,
                                'analysis': {
                                    'candidate_strength': 'Strong technical background',
                                    'job_requirement': 'Technical skills required'
                                }
                            },
                            'soft_skills': {
                                'score': 70.0,
                                'confidence': 0.7,
                                'weight_used': 0.15,
                                'analysis': {
                                    'candidate_strength': 'Good communication',
                                    'job_requirement': 'Team collaboration'
                                }
                            }
                        },
                        'profile_completeness': 85
                    })

            except Exception as e:
                logger.error(f"Error in matching service: {e}")
                formatted_matches = []

            processing_time = time.time() - start_time

            # Get effective weights
            try:
                effective_weights = job_offer.get_matching_weights() if hasattr(job_offer,
                                                                                'get_matching_weights') else None
            except:
                effective_weights = job_offer.matching_weights

            return Response({
                'success': True,
                'job': {
                    'id': job_offer.id,
                    'title': job_offer.title,
                    'company_name': job_offer.company.name if job_offer.company else 'N/A',
                    'experience_level': job_offer.experience_level,
                    'contract_type': job_offer.contract_type,
                    'remote_allowed': job_offer.remote_allowed,
                    'matching_config': {
                        'weights_used': effective_weights if use_custom_config else None,
                        'custom_prompt_used': bool(job_offer.system_prompt and use_custom_config),
                        'custom_config_applied': use_custom_config
                    }
                },
                'matching': {
                    'total_matches': len(formatted_matches),
                    'processing_time_ms': round(processing_time * 1000, 1),
                    'filters_applied': {
                        'min_score': min_score,
                        'top_n': top_n,
                        'exclude_applied': exclude_applied,
                        'use_custom_config': use_custom_config
                    },
                    'matches': formatted_matches
                },
                'generated_at': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error finding candidates for job {pk}: {e}")
            return Response({
                'success': False,
                'error': f'Candidate matching failed: {str(e)}',
                'job_id': pk
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def invalidate_cache(self, request, pk=None):
        """Invalider le cache quand l'offre est modifiée"""
        try:
            job_offer = self.get_object()

            # FIXED: Uncomment when matching_service is available
            # invalidated_count = matching_service.invalidate_cache(job_id=job_offer.id)
            invalidated_count = 0  # Placeholder

            return Response({
                'success': True,
                'message': f'Invalidated {invalidated_count} matching cache entries',
                'job_id': job_offer.id
            })

        except Exception as e:
            logger.error(f"Error invalidating cache for job {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApplicationViewSet(viewsets.ModelViewSet):
    """ViewSet unifié pour les candidatures"""
    queryset = Application.objects.all()
    serializer_class = ApplicationUnifiedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'job_offer', 'candidate']

    def get_queryset(self):
        return Application.objects.filter(
            job_offer__company=self.request.user.company
        ).select_related('candidate', 'job_offer', 'job_offer__company').order_by('-applied_at')

    @action(detail=True, methods=['post'])
    def update_matching_score(self, request, pk=None):
        """Recalculer le score de matching pour une candidature"""
        try:
            application = self.get_object()

            # Utiliser le service de matching unifié
            match_result = matching_service.quick_match(
                candidate_id=application.candidate.id,
                job_id=application.job_offer.id
            )

            if match_result:
                with transaction.atomic():
                    application.ai_match_score = round(match_result.overall_score * 100, 1)
                    application.ai_analysis = {
                        'recommendation': match_result.recommendation,
                        'confidence_level': match_result.confidence_level,
                        'breakdown': {
                            fm.field_name: fm.similarity_score
                            for fm in match_result.field_matches
                        },
                        'updated_at': timezone.now().isoformat()
                    }
                    application.last_updated = timezone.now()
                    application.save()

                return Response({
                    'success': True,
                    'application_id': application.id,
                    'updated_score': application.ai_match_score,
                    'recommendation': match_result.recommendation,
                    'confidence': match_result.confidence_level
                })
            else:
                return Response({
                    'success': False,
                    'error': 'Failed to calculate matching score'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            logger.error(f"Error updating matching score for application {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InterviewViewSet(viewsets.ModelViewSet):
    """ViewSet unifié pour les entretiens"""
    queryset = Interview.objects.all()
    serializer_class = InterviewUnifiedSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['interview_type', 'application']

    def get_queryset(self):
        return Interview.objects.filter(
            application__job_offer__company=self.request.user.company
        ).select_related(
            'application__candidate',
            'application__job_offer'
        ).order_by('-scheduled_at')


class MatchingAnalyticsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet pour les analytics de matching"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        """Vue d'ensemble des statistiques de matching"""
        return matching_analytics(request)

    @action(detail=False, methods=['post'])
    def clear_cache(self, request):
        """Vider le cache de matching"""
        return clear_cache(request)



class GroupCandidateViewSet(viewsets.ModelViewSet):
    """ViewSet unifié pour la gestion des groupes de candidats"""
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['type_groupe', 'is_active', 'couleur']

    def get_queryset(self):
        """Get queryset filtered by user"""
        if not self.request.user.is_authenticated:
            return GroupCandidate.objects.none()

        # Base queryset - only groups created by the current user
        queryset = GroupCandidate.objects.filter(
            created_by=self.request.user
        ).annotate(
            # Use a different name to avoid conflict with the property
            candidats_count_annotated=Count('candidats')
        ).select_related('created_by')

        # Filtres additionnels
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(nom__icontains=search) |
                Q(description__icontains=search)
            )

        # Filtre par candidat (groupes contenant ce candidat)
        candidat_id = self.request.query_params.get('candidat_id')
        if candidat_id:
            try:
                queryset = queryset.filter(candidats__id=candidat_id)
            except ValueError:
                pass

        # Tri
        ordering = self.request.query_params.get('ordering', 'ordre_affichage')
        if ordering in ['nom', '-nom', 'created_at', '-created_at', 'candidats_count', '-candidats_count']:
            if ordering in ['candidats_count', '-candidats_count']:
                # Use the annotated field for ordering
                queryset = queryset.order_by(
                    'candidats_count_annotated' if ordering == 'candidats_count'
                    else '-candidats_count_annotated'
                )
            else:
                queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('ordre_affichage', 'nom')

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'retrieve':
            return GroupCandidateDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return GroupCandidateCreateUpdateSerializer
        elif self.action in ['list_summary']:
            return GroupCandidateSummarySerializer
        return GroupCandidateListSerializer

    def perform_create(self, serializer):
        """Création avec données automatiques"""
        serializer.save(created_by=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """Récupération détaillée d'un groupe avec analytics"""
        try:
            instance = self.get_object()

            # Précharger les données liées pour optimiser
            instance = GroupCandidate.objects.select_related(
                'created_by'
            ).prefetch_related(
                'candidats'
            ).get(pk=instance.pk)

            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error retrieving group {kwargs.get('pk')}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def list_summary(self, request):
        """Liste résumée des groupes pour sélections"""
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'success': True,
                'groupes': serializer.data
            })
        except Exception as e:
            logger.error(f"Error in list_summary: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def add_candidats(self, request, pk=None):
        """Ajouter des candidats à un groupe"""
        try:
            groupe = self.get_object()
            candidat_ids = request.data.get('candidat_ids', [])

            if not isinstance(candidat_ids, list):
                return Response({
                    'success': False,
                    'error': 'candidat_ids doit être une liste'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Vérifier que tous les candidats existent
            from .models import Candidate
            candidats = Candidate.objects.filter(id__in=candidat_ids)
            if len(candidats) != len(candidat_ids):
                missing_ids = set(candidat_ids) - set(candidats.values_list('id', flat=True))
                return Response({
                    'success': False,
                    'error': f'Candidats introuvables: {missing_ids}'
                }, status=status.HTTP_404_NOT_FOUND)

            # Ajouter les candidats
            added_count = 0
            already_in_group = []

            for candidat in candidats:
                if not groupe.candidats.filter(id=candidat.id).exists():
                    groupe.add_candidat(candidat)
                    added_count += 1
                else:
                    already_in_group.append(candidat.full_name)

            return Response({
                'success': True,
                'groupe_id': groupe.id,
                'groupe_nom': groupe.nom,
                'added_count': added_count,
                'already_in_group': already_in_group,
                'total_candidats': groupe.candidats_count
            })

        except Exception as e:
            logger.error(f"Error adding candidats to group {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def remove_candidats(self, request, pk=None):
        """Retirer des candidats d'un groupe"""
        try:
            groupe = self.get_object()
            candidat_ids = request.data.get('candidat_ids', [])

            if not isinstance(candidat_ids, list):
                return Response({
                    'success': False,
                    'error': 'candidat_ids doit être une liste'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Retirer les candidats
            removed_count = 0
            not_in_group = []

            for candidat_id in candidat_ids:
                try:
                    from .models import Candidate
                    candidat = Candidate.objects.get(id=candidat_id)
                    if groupe.candidats.filter(id=candidat.id).exists():
                        groupe.remove_candidat(candidat)
                        removed_count += 1
                    else:
                        not_in_group.append(candidat.full_name)
                except Candidate.DoesNotExist:
                    not_in_group.append(f'ID:{candidat_id}')

            return Response({
                'success': True,
                'groupe_id': groupe.id,
                'groupe_nom': groupe.nom,
                'removed_count': removed_count,
                'not_in_group': not_in_group,
                'total_candidats': groupe.candidats_count
            })

        except Exception as e:
            logger.error(f"Error removing candidats from group {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def sync_auto_criteria(self, request, pk=None):
        """Synchroniser un groupe avec ses critères automatiques"""
        try:
            groupe = self.get_object()

            if not groupe.auto_populate:
                return Response({
                    'success': False,
                    'error': 'Ce groupe n\'a pas la population automatique activée'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not groupe.criteria_json:
                return Response({
                    'success': False,
                    'error': 'Aucun critère automatique défini'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Appliquer les critères
            added_count = groupe.apply_auto_criteria()

            return Response({
                'success': True,
                'groupe_id': groupe.id,
                'groupe_nom': groupe.nom,
                'added_count': added_count,
                'total_candidats': groupe.candidats_count,
                'last_sync': groupe.last_sync.isoformat() if groupe.last_sync else None,
                'criteria_applied': groupe.criteria_json
            })

        except Exception as e:
            logger.error(f"Error syncing group {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """Analytics détaillées d'un groupe"""
        try:
            groupe = self.get_object()
            analytics_data = groupe.get_analytics()

            # Ajouter des métriques supplémentaires
            candidats = groupe.candidats.all()

            # Répartition par statut d'application
            application_stats = {}
            for candidat in candidats:
                apps_count = candidat.applications.count() if hasattr(candidat, 'applications') else 0
                if apps_count == 0:
                    key = 'no_applications'
                elif apps_count <= 2:
                    key = 'few_applications'
                elif apps_count <= 5:
                    key = 'moderate_applications'
                else:
                    key = 'many_applications'

                application_stats[key] = application_stats.get(key, 0) + 1

            # Candidats récents
            recent_additions = candidats.order_by('-created_at')[:5]

            enhanced_analytics = {
                **analytics_data,
                'application_activity': application_stats,
                'recent_additions': [
                    {
                        'id': c.id,
                        'name': c.full_name,
                        'email': c.email,
                        'created_at': c.created_at.isoformat() if c.created_at else None,
                        'experience_years': getattr(c, 'experience_years', 0),
                        'top_skills': (getattr(c, 'technical_skills', None) or [])[:3]
                    }
                    for c in recent_additions
                ],
                'matching_performance': {
                    'high_performers': candidats.filter(
                        global_match_score__gte=0.8
                    ).count() if hasattr(candidats.model, 'global_match_score') else 0,
                    'avg_global_score': candidats.aggregate(
                        avg_score=models.Avg('global_match_score')
                    )['avg_score'] or 0 if hasattr(candidats.model, 'global_match_score') else 0
                },
                'geographic_distribution': dict(
                    candidats.exclude(city__isnull=True).exclude(city='')
                    .values('city').annotate(count=models.Count('id'))
                    .values_list('city', 'count')
                ) if hasattr(candidats.model, 'city') else {}
            }

            return Response({
                'success': True,
                'groupe': {
                    'id': groupe.id,
                    'nom': groupe.nom,
                    'type_groupe': groupe.type_groupe,
                    'couleur': groupe.couleur
                },
                'analytics': enhanced_analytics,
                'generated_at': timezone.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error getting analytics for group {pk}: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def bulk_actions(self, request):
        """Actions en lot sur plusieurs groupes"""
        try:
            action = request.data.get('action')
            groupe_ids = request.data.get('groupe_ids', [])

            if action not in ['activate', 'deactivate', 'delete', 'sync_all']:
                return Response({
                    'success': False,
                    'error': 'Action non supportée. Actions disponibles: activate, deactivate, delete, sync_all'
                }, status=status.HTTP_400_BAD_REQUEST)

            if not isinstance(groupe_ids, list) or not groupe_ids:
                return Response({
                    'success': False,
                    'error': 'groupe_ids doit être une liste non vide'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Filtrer les groupes de l'utilisateur
            groupes = GroupCandidate.objects.filter(
                id__in=groupe_ids,
                created_by=request.user
            )

            if len(groupes) != len(groupe_ids):
                missing_ids = set(groupe_ids) - set(groupes.values_list('id', flat=True))
                return Response({
                    'success': False,
                    'error': f'Groupes introuvables: {missing_ids}'
                }, status=status.HTTP_404_NOT_FOUND)

            results = []
            successful_count = 0

            for groupe in groupes:
                try:
                    if action == 'activate':
                        groupe.is_active = True
                        groupe.save(update_fields=['is_active'])
                        results.append(f"Groupe '{groupe.nom}' activé")
                        successful_count += 1

                    elif action == 'deactivate':
                        groupe.is_active = False
                        groupe.save(update_fields=['is_active'])
                        results.append(f"Groupe '{groupe.nom}' désactivé")
                        successful_count += 1

                    elif action == 'delete':
                        nom = groupe.nom
                        groupe.delete()
                        results.append(f"Groupe '{nom}' supprimé")
                        successful_count += 1

                    elif action == 'sync_all':
                        if groupe.auto_populate and groupe.criteria_json:
                            added = groupe.apply_auto_criteria()
                            results.append(f"Groupe '{groupe.nom}': {added} candidats ajoutés")
                            successful_count += 1
                        else:
                            results.append(f"Groupe '{groupe.nom}': pas de critères automatiques")

                except Exception as e:
                    results.append(f"Erreur pour groupe '{groupe.nom}': {str(e)}")

            return Response({
                'success': True,
                'action': action,
                'processed': len(groupes),
                'successful': successful_count,
                'results': results
            })
        except Exception as e:
            logger.error(f"Error in bulk actions: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)









# ==========================================
# Endpoints Standalone Unifiés
# ==========================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_jobs_for_candidate(request, candidate_id):
    """Endpoint unifié pour trouver des jobs pour un candidat"""
    try:
        candidate = get_object_or_404(Candidate, id=candidate_id)

        # Créer une instance temporaire du viewset pour réutiliser la logique
        viewset = CandidateViewSet()
        viewset.request = request
        viewset.format_kwarg = None

        # Utiliser l'action existante
        response = viewset.find_matching_jobs(request, pk=candidate_id)
        return response

    except Exception as e:
        logger.error(f"Error in find_jobs_for_candidate: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def find_candidates_for_job(request, job_id):
    """Endpoint unifié pour trouver des candidats pour un job"""
    try:
        job_offer = get_object_or_404(JobOffer, id=job_id, created_by=request.user)

        # Créer une instance temporaire du viewset
        viewset = JobOfferViewSet()
        viewset.request = request
        viewset.format_kwarg = None

        # Utiliser l'action existante
        response = viewset.find_matching_candidates(request, pk=job_id)
        return response

    except Exception as e:
        logger.error(f"Error in find_candidates_for_job: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quick_match(request):
    """Matching rapide entre un candidat et un job - ENDPOINT UNIQUE"""
    start_time = time.time()

    try:
        candidate_id = request.data.get('candidate_id')
        job_id = request.data.get('job_id')

        if not candidate_id or not job_id:
            return Response({
                'success': False,
                'error': 'Both candidate_id and job_id are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        candidate = get_object_or_404(Candidate, id=candidate_id)
        job_offer = get_object_or_404(JobOffer, id=job_id)

        # Utiliser le service de matching unifié
        match_result = matching_service.quick_match(candidate_id, job_id)

        if not match_result:
            return Response({
                'success': False,
                'error': 'Unable to calculate match score'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Vérifier si candidature existante
        existing_application = Application.objects.filter(
            candidate=candidate, job_offer=job_offer
        ).first()

        processing_time = time.time() - start_time

        return Response({
            'success': True,
            'candidate': {
                'id': candidate.id,
                'name': candidate.full_name,
                'email': candidate.email,
                'experience_years': candidate.experience_years,
                'top_skills': (candidate.technical_skills or [])[:5]
            },
            'job': {
                'id': job_offer.id,
                'title': job_offer.title,
                'company': job_offer.company.name if job_offer.company else 'N/A',
                'experience_level': job_offer.experience_level,
                'contract_type': job_offer.contract_type
            },
            'matching': {
                'overall_score': round(match_result.overall_score * 100, 1),
                'recommendation': match_result.recommendation,
                'confidence_level': match_result.confidence_level,
                'breakdown': {
                    field_match.field_name: {
                        'score': round(field_match.similarity_score * 100, 1),
                        'confidence': field_match.confidence,
                        'candidate_value': str(field_match.candidate_value)[:100],
                        'job_requirement': str(field_match.job_value)[:100]
                    } for field_match in match_result.field_matches
                }
            },
            'application_status': {
                'already_applied': existing_application is not None,
                'application_id': existing_application.id if existing_application else None,
                'status': existing_application.status if existing_application else None,
                'applied_at': existing_application.applied_at.isoformat() if existing_application else None
            },
            'processing_time_ms': round(processing_time * 1000, 1),
            'generated_at': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in quick match: {e}")
        return Response({
            'success': False,
            'error': f'Quick match failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def batch_matching(request):
    """Matching par lot - ENDPOINT UNIQUE"""
    start_time = time.time()

    try:
        job_id = request.data.get('job_id')
        candidate_ids = request.data.get('candidate_ids', [])
        candidate_id = request.data.get('candidate_id')
        job_ids = request.data.get('job_ids', [])

        results = []
        errors = []
        successful_matches = 0

        if job_id and candidate_ids:
            # Multiple candidats vs une offre
            job_offer = get_object_or_404(JobOffer, id=job_id)

            for cand_id in candidate_ids:
                try:
                    match_result = matching_service.quick_match(cand_id, job_id)
                    if match_result:
                        candidate = Candidate.objects.get(id=cand_id)
                        results.append({
                            'candidate_id': cand_id,
                            'candidate_name': candidate.full_name,
                            'overall_score': round(match_result.overall_score * 100, 1),
                            'recommendation': match_result.recommendation,
                            'confidence': match_result.confidence_level
                        })
                        successful_matches += 1
                    else:
                        errors.append(f"Failed to match candidate {cand_id}")

                except Candidate.DoesNotExist:
                    errors.append(f"Candidate {cand_id} not found")
                except Exception as e:
                    errors.append(f"Error matching candidate {cand_id}: {str(e)}")

            # Trier par score
            results.sort(key=lambda x: x['overall_score'], reverse=True)

        elif candidate_id and job_ids:
            # Un candidat vs multiples offres
            candidate = get_object_or_404(Candidate, id=candidate_id)

            for j_id in job_ids:
                try:
                    match_result = matching_service.quick_match(candidate_id, j_id)
                    if match_result:
                        job = JobOffer.objects.get(id=j_id)
                        results.append({
                            'job_id': j_id,
                            'job_title': job.title,
                            'company_name': job.company.name if job.company else 'N/A',
                            'overall_score': round(match_result.overall_score * 100, 1),
                            'recommendation': match_result.recommendation,
                            'confidence': match_result.confidence_level
                        })
                        successful_matches += 1
                    else:
                        errors.append(f"Failed to match job {j_id}")

                except JobOffer.DoesNotExist:
                    errors.append(f"Job {j_id} not found")
                except Exception as e:
                    errors.append(f"Error matching job {j_id}: {str(e)}")

            # Trier par score
            results.sort(key=lambda x: x['overall_score'], reverse=True)

        else:
            return Response({
                'success': False,
                'error': 'Provide either (job_id + candidate_ids) or (candidate_id + job_ids)'
            }, status=status.HTTP_400_BAD_REQUEST)

        processing_time = time.time() - start_time

        return Response({
            'success': True,
            'total_processed': len(candidate_ids) + len(job_ids),
            'successful_matches': successful_matches,
            'failed_matches': len(errors),
            'processing_time_ms': round(processing_time * 1000, 1),
            'results': results,
            'errors': errors,
            'generated_at': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error in batch matching: {e}")
        return Response({
            'success': False,
            'error': f'Batch matching failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def matching_analytics(request):
    """Analytics unifiées de matching"""
    try:
        # Métriques générales
        total_candidates = Candidate.objects.count()
        active_jobs = JobOffer.objects.filter(
            created_by=request.user, status='active'
        ).count()
        total_applications = Application.objects.filter(
            job_offer__created_by=request.user
        ).count()

        # Cache de matching pour l'entreprise
        company_cache = MatchingCache.objects.filter(
            job_offer__created_by=request.user,
            is_valid=True
        )

        # Distribution des scores
        score_distribution = {
            'excellent': company_cache.filter(overall_score__gte=0.8).count(),
            'good': company_cache.filter(overall_score__gte=0.6, overall_score__lt=0.8).count(),
            'fair': company_cache.filter(overall_score__gte=0.4, overall_score__lt=0.6).count(),
            'poor': company_cache.filter(overall_score__lt=0.4).count()
        }

        # Score moyen
        avg_score_data = company_cache.aggregate(
            avg_score=Avg('overall_score'),
            total_matches=Count('id')
        )

        # Compétences les plus demandées
        job_requirements = JobOffer.objects.filter(
            created_by=request.user, status='active'
        ).values_list('requirements', flat=True)

        all_requirements_text = ' '.join(req for req in job_requirements if req)

        # Activité récente
        recent_activity = {
            'matches_last_7_days': company_cache.filter(
                calculated_at__gte=timezone.now() - timedelta(days=7)
            ).count(),
            'applications_last_7_days': Application.objects.filter(
                job_offer__created_by=request.user,
                applied_at__gte=timezone.now() - timedelta(days=7)
            ).count()
        }

        # Métriques de performance
        performance_metrics = {
            'cache_hit_ratio': round(
                (company_cache.count() / max(total_candidates * active_jobs, 1)) * 100, 1
            ),
            'avg_processing_time': 'N/A',  # Pourrait être calculé si on stockait les temps
            'total_cached_matches': company_cache.count()
        }

        return Response({
            'success': True,
            'analytics': {
                'overview': {
                    'total_candidates': total_candidates,
                    'active_jobs': active_jobs,
                    'total_applications': total_applications,
                    'matching_potential': total_candidates * active_jobs
                },
                'score_distribution': score_distribution,
                'average_score': round((avg_score_data['avg_score'] or 0) * 100, 1),
                'total_matches_analyzed': avg_score_data['total_matches'],
                'recent_activity': recent_activity,
                'performance_metrics': performance_metrics
            },
            'generated_at': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error calculating matching analytics: {e}")
        return Response({
            'success': False,
            'error': 'Error calculating analytics'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cache(request):
    """Vider le cache de matching - ENDPOINT UNIQUE"""
    try:
        candidate_id = request.data.get('candidate_id')
        job_id = request.data.get('job_id')

        invalidated_count = matching_service.invalidate_cache(
            candidate_id=candidate_id,
            job_id=job_id
        )

        return Response({
            'success': True,
            'message': f'Invalidated {invalidated_count} cache entries',
            'filters_applied': {
                'candidate_id': candidate_id,
                'job_id': job_id,
                'company': request.user.company.name
            },
            'cleared_at': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error clearing matching cache: {e}")
        return Response({
            'success': False,
            'error': 'Error clearing cache'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_search_filters(request):
    """Données pour les filtres de recherche"""
    try:
        # Compétences techniques les plus communes
        technical_skills_freq = Counter()
        for candidate in Candidate.objects.exclude(technical_skills=[]):
            technical_skills_freq.update(candidate.technical_skills or [])

        # Niveaux d'expérience
        experience_levels = list(
            JobOffer.objects.filter(created_by=request.user)
            .values_list('experience_level', flat=True)
            .distinct()
        )

        # Villes
        cities = list(
            Candidate.objects.exclude(city__isnull=True)
            .exclude(city='')
            .values_list('city', flat=True)
            .distinct()
        )

        return Response({
            'success': True,
            'filters': {
                'top_technical_skills': dict(technical_skills_freq.most_common(20)),
                'experience_levels': [level for level in experience_levels if level],
                'cities': sorted(cities),
                'education_levels': [
                    'Bac', 'BTS/DUT', 'Licence', 'Master', 'Ingénieur', 'Doctorat'
                ],
                'contract_types': [
                    'CDI', 'CDD', 'Stage', 'Freelance', 'Alternance'
                ]
            }
        })

    except Exception as e:
        logger.error(f"Error getting search filters: {e}")
        return Response({
            'success': False,
            'error': 'Error loading filters'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==========================================
# Vues HTML Simplifiées (Admin)
# ==========================================

@login_required
def admin_jobs_list(request):
    """Liste administrative des jobs"""
    jobs = JobOffer.objects.filter(created_by=request.user)
    return render(request, 'recruitment/admin_jobs.html', {'jobs': jobs})


@login_required
def admin_candidates_list(request):
    """Liste administrative des candidats"""
    candidates = Candidate.objects.all()
    return render(request, 'recruitment/admin_candidates.html', {'candidates': candidates})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def manage_candidat_groupes(request):
    """Gérer l'appartenance d'un candidat aux groupes"""
    try:
        serializer = CandidatGroupeMembershipSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        candidat_id = serializer.validated_data['candidat_id']
        groupe_ids = serializer.validated_data['groupe_ids']
        action = serializer.validated_data['action']

        candidat = Candidate.objects.get(id=candidat_id)
        groupes = GroupCandidate.objects.filter(
            id__in=groupe_ids,

        )

        # Effectuer l'action
        if action == 'add':
            for groupe in groupes:
                if not groupe.candidats.filter(id=candidat.id).exists():
                    groupe.add_candidat(candidat)
            message = f"Candidat ajouté à {len(groupes)} groupe(s)"

        elif action == 'remove':
            for groupe in groupes:
                if groupe.candidats.filter(id=candidat.id).exists():
                    groupe.remove_candidat(candidat)
            message = f"Candidat retiré de {len(groupes)} groupe(s)"

        elif action == 'replace':
            # Retirer de tous les groupes actuels
            current_groupes = candidat.groupes.filter(created_by=request.user)
            for groupe in current_groupes:
                groupe.remove_candidat(candidat)

            # Ajouter aux nouveaux groupes
            for groupe in groupes:
                groupe.add_candidat(candidat)
            message = f"Appartenance remplacée: {len(groupes)} groupe(s)"

        # Retourner l'état actuel
        current_groupes = candidat.groupes.filter(
            created_by=request.user
        ).values('id', 'nom', 'couleur', 'type_groupe')

        return Response({
            'success': True,
            'message': message,
            'candidat': {
                'id': candidat.id,
                'name': candidat.full_name,
                'current_groupes': list(current_groupes)
            }
        })

    except Candidate.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Candidat introuvable'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error managing candidat groupes: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def groupes_dashboard(request):
    """Dashboard des groupes de candidats"""
    try:
        company_groupes = GroupCandidate.objects.filter(
            created_by=request.user
        ).select_related('created_by').prefetch_related('candidats')

        # Statistiques générales
        total_groupes = company_groupes.count()
        active_groupes = company_groupes.filter(is_active=True).count()
        auto_groupes = company_groupes.filter(auto_populate=True).count()

        # Distribution par type
        type_distribution = dict(
            company_groupes.values('type_groupe')
            .annotate(count=models.Count('id'))
            .values_list('type_groupe', 'count')
        )

        # Groupes les plus peuplés
        top_groupes = company_groupes.annotate(
            candidats_count=models.Count('candidats')
        ).order_by('-candidats_count')[:5]

        top_groupes_data = [{
            'id': g.id,
            'nom': g.nom,
            'candidats_count': g.candidats_count,
            'couleur': g.couleur,
            'type_groupe': g.type_groupe,
            'is_active': g.is_active
        } for g in top_groupes]

        # Activité récente
        recent_activity = company_groupes.order_by('-updated_at')[:5]
        recent_activity_data = [{
            'id': g.id,
            'nom': g.nom,
            'action': 'updated',
            'updated_at': g.updated_at.isoformat(),
            'candidats_count': g.candidats.count()
        } for g in recent_activity]

        # Candidats sans groupe
        candidats_sans_groupe = Candidate.objects.annotate(
            groupes_count=models.Count('groupes')
        ).filter(groupes_count=0).count()

        return Response({
            'success': True,
            'dashboard': {
                'overview': {
                    'total_groupes': total_groupes,
                    'active_groupes': active_groupes,
                    'auto_groupes': auto_groupes,
                    'candidats_sans_groupe': candidats_sans_groupe
                },
                'type_distribution': type_distribution,
                'top_groupes': top_groupes_data,
                'recent_activity': recent_activity_data,
                'recommendations': [
                    f"{candidats_sans_groupe} candidats n'appartiennent à aucun groupe" if candidats_sans_groupe > 0 else None,
                    f"{auto_groupes} groupes avec population automatique" if auto_groupes > 0 else None,
                    "Considérez créer des groupes par compétences clés" if total_groupes < 3 else None
                ]
            },
            'generated_at': timezone.now().isoformat()
        })

    except Exception as e:
        logger.error(f"Error generating groupes dashboard: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def suggest_groupes_for_candidat(request, candidat_id):
    """Suggérer des groupes pour un candidat basé sur ses compétences"""
    try:
        candidat = get_object_or_404(Candidate, id=candidat_id)

        # Groupes existants de l'entreprise
        company_groupes = GroupCandidate.objects.filter(
            created_by=request.user,
            is_active=True
        ).prefetch_related('candidats')

        suggestions = []

        for groupe in company_groupes:
            # Éviter les groupes où le candidat est déjà
            if groupe.candidats.filter(id=candidat.id).exists():
                continue

            score = 0
            reasons = []

            # Analyse des compétences techniques
            if candidat.technical_skills and groupe.candidats.exists():
                groupe_skills = []
                for g_candidat in groupe.candidats.all():
                    groupe_skills.extend(g_candidat.technical_skills or [])

                common_skills = set(candidat.technical_skills) & set(groupe_skills)
                if common_skills:
                    score += len(common_skills) * 10
                    reasons.append(f"Compétences communes: {', '.join(list(common_skills)[:3])}")

            # Analyse de l'expérience
            if candidat.experience_years:
                groupe_exp = [
                    c.experience_years for c in groupe.candidats.all()
                    if c.experience_years
                ]
                if groupe_exp:
                    avg_exp = sum(groupe_exp) / len(groupe_exp)
                    exp_diff = abs(candidat.experience_years - avg_exp)
                    if exp_diff <= 2:  # Expérience similaire
                        score += 15
                        reasons.append(f"Niveau d'expérience similaire ({candidat.experience_years} ans)")

            # Analyse géographique
            if candidat.city:
                same_city_count = groupe.candidats.filter(city=candidat.city).count()
                if same_city_count > 0:
                    score += 5
                    reasons.append(f"Même zone géographique ({candidat.city})")

            # Critères automatiques du groupe
            if groupe.auto_populate and groupe.criteria_json:
                criteria_match = 0
                if 'technical_skills' in groupe.criteria_json:
                    required_skills = set(groupe.criteria_json['technical_skills'])
                    candidat_skills = set(candidat.technical_skills or [])
                    if required_skills & candidat_skills:
                        criteria_match += 20
                        reasons.append("Correspond aux critères automatiques")

                score += criteria_match

            if score > 0:
                suggestions.append({
                    'groupe_id': groupe.id,
                    'groupe_nom': groupe.nom,
                    'type_groupe': groupe.type_groupe,
                    'couleur': groupe.couleur,
                    'score': score,
                    'confidence': min(100, score),
                    'reasons': reasons,
                    'current_size': groupe.candidats.count()
                })

        # Trier par score
        suggestions.sort(key=lambda x: x['score'], reverse=True)

        return Response({
            'success': True,
            'candidat': {
                'id': candidat.id,
                'name': candidat.full_name,
                'technical_skills': candidat.technical_skills or [],
                'experience_years': candidat.experience_years,
                'city': candidat.city
            },
            'suggestions': suggestions[:10],  # Top 10
            'total_suggestions': len(suggestions)
        })

    except Exception as e:
        logger.error(f"Error suggesting groupes for candidat {candidat_id}: {e}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)