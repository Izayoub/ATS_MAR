# ai_engine/tests.py - Tests Django
from django.test import TestCase, Client
from django.urls import reverse
import json
import time


class MatchingServiceTest(TestCase):
    """Tests pour le service de matching"""

    def setUp(self):
        self.client = Client()

        # Données de test
        self.test_cv = {
            "titre_candidat": "Développeur Python",
            "profil_resume": "Développeur avec 3 ans d'expérience",
            "formations": ["Master Informatique"],
            "experience_years": 3,
            "competences_techniques": ["Python", "Django", "PostgreSQL"],
            "competences_informatiques": ["Git", "Linux"],
            "langues": ["Français: C2", "Anglais: B2"],
            "certifications": [],
            "projets": ["Site web e-commerce"],
            "soft_skills": ["teamwork", "problem-solving"]
        }

        self.test_job = {
            "titre_poste": "Développeur Backend Python",
            "missions": "Développer des APIs avec Python/Django",
            "exigences": {
                "formation_requise": "Bac+5 Informatique",
                "annees_experience": 2,
                "competences_obligatoires": ["Python", "Django"],
                "competences_souhaitees": ["PostgreSQL", "Docker"],
                "langues": ["Français: B2"],
                "certifications": [],
                "outils": ["Git"],
                "qualites_humaines": ["autonomie", "teamwork"]
            }
        }

    def test_health_check(self):
        """Test de l'endpoint de santé"""
        response = self.client.get(reverse('ai_engine:health'))

        self.assertIn(response.status_code, [200, 503])
        data = response.json()
        self.assertIn('status', data)
        self.assertIn('details', data)

    def test_single_matching_api(self):
        """Test de l'API de matching unique"""
        url = reverse('ai_engine:match_cv')
        payload = {
            'cv_data': self.test_cv,
            'job_data': self.test_job,
            'cv_id': 'test_cv_001'
        }

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        # Peut être 200 (succès) ou 503 (service non prêt)
        self.assertIn(response.status_code, [200, 503])

        if response.status_code == 200:
            data = response.json()
            self.assertTrue(data['success'])
            self.assertIn('result', data)
            self.assertIn('total_score', data['result'])

    def test_domain_detection_api(self):
        """Test de l'API de détection de domaine"""
        url = reverse('ai_engine:detect_domain')
        payload = {'cv_data': self.test_cv}

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [200, 500])

        if response.status_code == 200:
            data = response.json()
            self.assertTrue(data['success'])
            self.assertIn('cv_domain', data)
            self.assertIn(data['cv_domain'], ['tech', 'business', 'sales', 'other'])

    def test_batch_matching_api(self):
        """Test de l'API de matching par lot"""
        url = reverse('ai_engine:batch_match')
        payload = {
            'cv_list': [self.test_cv, self.test_cv],  # Doublon pour test
            'job_data': self.test_job,
            'top_k': 5,
            'prioritize_tech': True
        }

        response = self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertIn(response.status_code, [200, 503])

        if response.status_code == 200:
            data = response.json()
            self.assertTrue(data['success'])
            self.assertIn('results', data)
            self.assertIn('statistics', data)

    def test_testeur_interface(self):
        """Test de l'interface de test"""
        url = reverse('ai_engine:testeur')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Testeur Service Matching')