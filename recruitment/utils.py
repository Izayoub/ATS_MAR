import os
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_cv_file(file):
    """Valider le fichier CV uploadé"""

    # Vérifier l'extension
    file_extension = os.path.splitext(file.name)[1].lower()
    if file_extension not in settings.ALLOWED_CV_FORMATS:
        raise ValidationError(
            f"Format de fichier non autorisé. Formats acceptés: {', '.join(settings.ALLOWED_CV_FORMATS)}"
        )

    # Vérifier la taille
    if file.size > settings.MAX_CV_FILE_SIZE:
        raise ValidationError(
            f"Fichier trop volumineux. Taille maximum: {settings.MAX_CV_FILE_SIZE / (1024 * 1024)}MB"
        )

    return True


def generate_cv_filename(instance, filename):
    """Générer un nom de fichier unique pour le CV"""
    file_extension = os.path.splitext(filename)[1].lower()
    timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
    return f"cvs/cv_{timestamp}_{instance.id}{file_extension}"
