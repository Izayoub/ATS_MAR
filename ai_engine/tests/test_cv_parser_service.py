import pytest
from unittest.mock import patch, MagicMock
from ai_engine.services.cv_parser import CVParserService
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_MA.settings')  # ou le chemin exact vers ton fichier settings.py

import django
django.setup()
@pytest.fixture
def parser():
    return CVParserService()

def test_extract_contact_info_email_and_phone(parser):
    cv_text = "Nom: John Doe\nEmail: john.doe@example.com\nTéléphone: +212612345678"
    result = parser.extract_contact_info(cv_text)
    assert result['email'] == "john.doe@example.com"
    assert result['phone'] == "+212612345678"

def test_extract_contact_info_linkedin(parser):
    cv_text = "Mon profil LinkedIn: linkedin.com/in/john-doe-123456"
    result = parser.extract_contact_info(cv_text)
    assert result['linkedin'] == "https://linkedin.com/in/john-doe-123456"

@patch('ai_engine.services.cv_parser.LLMService')
def test_extract_skills_with_llm(mock_llm, parser):
    dummy_response = '''
    {
        "technical_skills": ["Python", "Django"],
        "soft_skills": ["Communication"],
        "languages": [{"language": "Français", "level": "Natif"}]
    }
    '''
    mock_llm_instance = mock_llm.return_value
    mock_llm_instance.generate_text.return_value = dummy_response
    parser.llm_service = mock_llm_instance

    text = "Expérience avec Python, Django. Bon communicateur. Langues: Français natif."
    result = parser.extract_skills_with_llm(text)

    assert "Python" in result['technical_skills']
    assert "Communication" in result['soft_skills']

@patch('ai_engine.services.cv_parser.LLMService')
def test_extract_experience_with_llm(mock_llm, parser):
    dummy_response = '''
    {
        "experience": [{
            "title": "Développeur Full Stack",
            "company": "TechCorp",
            "duration": "2021-2023",
            "description": "Développement applications web"
        }],
        "education": [{
            "degree": "Master en Informatique",
            "institution": "ENSIAS",
            "year": "2020"
        }],
        "total_experience_years": 3
    }
    '''
    mock_llm_instance = mock_llm.return_value
    mock_llm_instance.generate_text.return_value = dummy_response
    parser.llm_service = mock_llm_instance

    result = parser.extract_experience_with_llm("...")
    assert result['total_experience_years'] == 3
    assert result['experience'][0]['company'] == "TechCorp"

@patch('ai_engine.services.cv_parser.LLMService')
def test_generate_candidate_summary(mock_llm, parser):
    mock_llm_instance = mock_llm.return_value
    mock_llm_instance.generate_text.return_value = "Développeur full-stack avec 3 ans d'expérience..."
    parser.llm_service = mock_llm_instance

    data = {
        "skills": {"technical_skills": ["Python"]},
        "experience": {"total_experience_years": 3, "experience": [{"title": "Développeur"}]}
    }

    summary = parser.generate_candidate_summary(data)
    assert "3 ans" in summary

@patch('ai_engine.services.cv_parser.LLMService')
def test_process_full_pipeline(mock_llm, parser):
    mock_llm_instance = mock_llm.return_value
    mock_llm_instance.generate_text.side_effect = [
        '''
        {
            "technical_skills": ["Python"],
            "soft_skills": ["Autonomie"],
            "languages": [{"language": "Français", "level": "Natif"}]
        }
        ''',
        '''
        {
            "experience": [{"title": "Dev"}],
            "education": [{"degree": "Licence"}],
            "total_experience_years": 2
        }
        ''',
        "Résumé professionnel généré."
    ]
    parser.llm_service = mock_llm_instance

    result = parser.process("CV fictif de test")
    assert result['contact'] is not None
    assert result['skills']['technical_skills']
    assert result['experience']['total_experience_years'] == 2
    assert "Résumé" in result['ai_summary']
