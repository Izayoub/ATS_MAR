# ai_engine/services/llm_service.py
import torch
import logging
from .base import BaseAIService, model_manager

logger = logging.getLogger(__name__)


class LLMService(BaseAIService):
    """Service pour la génération de texte avec TinyLLaMA"""

    def __init__(self):
        super().__init__()
        self.model_manager = model_manager
        self.model = None
        self.tokenizer = None
        self.is_loaded = False

    def load_model(self):
        """
        Implémentation requise de la méthode abstraite load_model
        Charge le modèle TinyLLaMA
        """
        try:
            if not self.is_loaded:
                self.model, self.tokenizer = self.model_manager.load_tinyllama()
                self.is_loaded = True
                logger.info("Modèle TinyLLaMA chargé avec succès")
                return True
        except Exception as e:
            logger.error(f"Erreur lors du chargement du modèle: {e}")
            self.is_loaded = False
            return False
        return self.is_loaded

    def process(self, text, task_type="summary", **kwargs):
        """
        Implémentation requise de la méthode abstraite process
        Traite le texte selon le type de tâche demandé
        """
        if not self.is_loaded:
            if not self.load_model():
                return {
                    'success': False,
                    'error': 'Modèle non disponible'
                }

        if task_type == "summary":
            return self.generate_resume_summary(text, kwargs.get('max_length', 200))
        elif task_type == "job_match":
            return self.generate_job_match_analysis(
                text,
                kwargs.get('job_description', ''),
                kwargs.get('similarity_score')
            )
        elif task_type == "interview_questions":
            return self.generate_interview_questions(
                text,
                kwargs.get('job_description', ''),
                kwargs.get('num_questions', 5)
            )
        elif task_type == "rejection_feedback":
            return self.generate_rejection_feedback(
                text,
                kwargs.get('job_description', ''),
                kwargs.get('reason')
            )
        else:
            return {
                'success': False,
                'error': f'Type de tâche non supporté: {task_type}'
            }

    def generate_resume_summary(self, resume_text, max_length=200):
        """
        Génère un résumé professionnel du CV

        Args:
            resume_text (str): Texte du CV
            max_length (int): Longueur maximale du résumé

        Returns:
            dict: Résumé généré avec métadonnées
        """
        try:
            if not self.is_loaded:
                if not self.load_model():
                    return {
                        'success': False,
                        'summary': '',
                        'error': 'Modèle non disponible'
                    }

            # Prompt pour générer un résumé
            prompt = f"""Résume ce CV en français de manière professionnelle et concise:

            {resume_text[:1000]}

            Résumé professionnel:"""

            # Tokenisation
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024,
                padding=True
            )

            # Génération
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1,
                    no_repeat_ngram_size=3
                )

            # Décodage et nettoyage
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            summary = generated_text.replace(prompt, "").strip()

            return {
                'success': True,
                'summary': summary,
                'length': len(summary),
                'model_used': 'TinyLLaMA'
            }

        except Exception as e:
            logger.error(f"Erreur lors de la génération du résumé: {e}")
            return {
                'success': False,
                'summary': '',
                'error': str(e)
            }

    def generate_job_match_analysis(self, resume_text, job_description, similarity_score=None):
        """
        Génère une analyse de correspondance CV/Poste

        Args:
            resume_text (str): Texte du CV
            job_description (str): Description du poste
            similarity_score (float): Score de similarité calculé

        Returns:
            dict: Analyse de correspondance
        """
        try:
            if not self.is_loaded:
                if not self.load_model():
                    return {
                        'success': False,
                        'analysis': '',
                        'error': 'Modèle non disponible'
                    }

            # Construction du prompt
            score_text = f"Score de similarité: {similarity_score:.2f}" if similarity_score else ""

            prompt = f"""Analyse la correspondance entre ce CV et cette offre d'emploi:

            CV (extrait): {resume_text[:500]}...

            Offre d'emploi: {job_description[:500]}...

            {score_text}

            Analyse en français:
            1. Points forts du candidat:
            2. Compétences manquantes:
            3. Recommandations:

            Analyse:"""

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=300,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )

            analysis = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            analysis = analysis.replace(prompt, "").strip()

            # Détermination du niveau de correspondance
            match_level = self._determine_match_level(similarity_score)

            return {
                'success': True,
                'analysis': analysis,
                'match_level': match_level,
                'similarity_score': similarity_score,
                'model_used': 'TinyLLaMA'
            }

        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de correspondance: {e}")
            return {
                'success': False,
                'analysis': '',
                'error': str(e)
            }

    def generate_interview_questions(self, resume_text, job_description, num_questions=5):
        """
        Génère des questions d'entretien basées sur le CV et le poste

        Args:
            resume_text (str): Texte du CV
            job_description (str): Description du poste
            num_questions (int): Nombre de questions à générer

        Returns:
            dict: Questions d'entretien générées
        """
        try:
            if not self.is_loaded:
                if not self.load_model():
                    return {
                        'success': False,
                        'questions': [],
                        'error': 'Modèle non disponible'
                    }

            prompt = f"""Génère {num_questions} questions d'entretien pertinentes basées sur ce CV et ce poste:

            CV: {resume_text[:400]}...

            Poste: {job_description[:400]}...

            Questions d'entretien en français:"""

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=250,
                    temperature=0.8,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.2
                )

            questions_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            questions_text = questions_text.replace(prompt, "").strip()

            # Extraction des questions individuelles
            questions = self._extract_questions(questions_text)

            return {
                'success': True,
                'questions': questions,
                'raw_text': questions_text,
                'model_used': 'TinyLLaMA'
            }

        except Exception as e:
            logger.error(f"Erreur lors de la génération des questions: {e}")
            return {
                'success': False,
                'questions': [],
                'error': str(e)
            }

    def generate_rejection_feedback(self, resume_text, job_description, reason=None):
        """
        Génère un feedback constructif pour un candidat rejeté

        Args:
            resume_text (str): Texte du CV
            job_description (str): Description du poste
            reason (str): Raison du rejet (optionnel)

        Returns:
            dict: Feedback généré
        """
        try:
            if not self.is_loaded:
                if not self.load_model():
                    return {
                        'success': False,
                        'feedback': '',
                        'error': 'Modèle non disponible'
                    }

            reason_text = f"Raison du rejet: {reason}" if reason else ""

            prompt = f"""Rédige un feedback constructif et bienveillant pour ce candidat:

            CV: {resume_text[:400]}...

            Poste: {job_description[:300]}...

            {reason_text}

            Feedback constructif en français:"""

            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=1024
            )

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=200,
                    temperature=0.6,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    repetition_penalty=1.1
                )

            feedback = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            feedback = feedback.replace(prompt, "").strip()

            return {
                'success': True,
                'feedback': feedback,
                'model_used': 'TinyLLaMA'
            }

        except Exception as e:
            logger.error(f"Erreur lors de la génération du feedback: {e}")
            return {
                'success': False,
                'feedback': '',
                'error': str(e)
            }

    def _determine_match_level(self, similarity_score):
        """Détermine le niveau de correspondance basé sur le score"""
        if similarity_score is None:
            return 'Non évalué'

        if similarity_score >= 0.8:
            return 'Excellent'
        elif similarity_score >= 0.65:
            return 'Très bon'
        elif similarity_score >= 0.5:
            return 'Bon'
        elif similarity_score >= 0.35:
            return 'Moyen'
        else:
            return 'Faible'

    def _extract_questions(self, questions_text):
        """Extrait les questions individuelles du texte généré"""
        import re

        # Patterns pour identifier les questions
        question_patterns = [
            r'\d+\.\s*(.+\?)',  # "1. Question?"
            r'-\s*(.+\?)',  # "- Question?"
            r'•\s*(.+\?)',  # "• Question?"
            r'(.+\?)'  # "Question?"
        ]

        questions = []
        lines = questions_text.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            for pattern in question_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    clean_question = match.strip()
                    if len(clean_question) > 10 and clean_question not in questions:
                        questions.append(clean_question)

        return questions[:10]  # Limite à 10 questions max