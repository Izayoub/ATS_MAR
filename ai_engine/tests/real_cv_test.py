"""
Simple test script for CV Parser Service
"""
import sys
import os
import traceback
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from ai_engine.services.cv_parser import CVParserService

    print("✅ Successfully imported CVParserService")
except ImportError as e:
    print(f"❌ Failed to import CVParserService: {e}")
    sys.exit(1)


def test_cv_parser():
    """Test basic CV parsing functionality"""
    print("\n" + "=" * 50)
    print("🧪 TESTING CV PARSER SERVICE")
    print("=" * 50)

    # Sample CV text
    sample_cv = """
    Jean Dupont
    Développeur Full Stack
    Email: jean.dupont@email.com
    Téléphone: +212 6 12 34 56 78
    LinkedIn: linkedin.com/in/jean-dupont

    EXPÉRIENCE PROFESSIONNELLE
    2020-2023: Développeur Full Stack chez TechCorp
    - Développement d'applications web avec Python et Django
    - Création d'interfaces utilisateur avec React et JavaScript
    - Gestion de bases de données MySQL et PostgreSQL

    2018-2020: Développeur Junior chez WebStart
    - Développement de sites web avec PHP et Laravel
    - Maintenance et optimisation de code existant

    COMPÉTENCES
    Langages: Python, JavaScript, PHP, Java
    Frameworks: Django, React, Laravel, Spring Boot
    Bases de données: MySQL, PostgreSQL, MongoDB
    Outils: Git, Docker, AWS

    FORMATION
    2018: Master en Informatique - ENSIAS Rabat
    2016: Licence en Informatique - FST Fès

    LANGUES
    Français: Natif
    Anglais: Courant
    Arabe: Natif
    """

    try:
        print("📋 Initializing CV Parser...")
        parser = CVParserService()
        print("✅ CV Parser initialized successfully")

        print("\n📊 Processing sample CV...")
        start_time = datetime.now()

        result = parser.process(sample_cv)

        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        print(f"⏱️  Processing completed in {processing_time:.2f} seconds")

        if result.get('success'):
            print("\n✅ CV parsing successful!")

            # Display contact information
            contact = result.get('contact', {})
            if contact:
                print("\n📞 CONTACT INFORMATION:")
                for key, value in contact.items():
                    print(f"  {key}: {value}")

            # Display skills
            skills = result.get('skills', {})
            if skills:
                print("\n🛠️  SKILLS:")
                tech_skills = skills.get('technical_skills', [])
                if tech_skills:
                    print(f"  Technical Skills: {', '.join(tech_skills[:5])}")

                languages = skills.get('languages', [])
                if languages:
                    print("  Languages:")
                    for lang in languages:
                        print(f"    - {lang.get('language', 'N/A')}: {lang.get('level', 'N/A')}")

            # Display experience
            experience = result.get('experience', {})
            if experience:
                print("\n💼 EXPERIENCE:")
                total_years = experience.get('total_experience_years', 0)
                print(f"  Total Experience: {total_years} years")

                experiences = experience.get('experience', [])
                if experiences:
                    print("  Positions:")
                    for exp in experiences[:3]:  # Show first 3
                        title = exp.get('title', 'N/A')
                        company = exp.get('company', 'N/A')
                        duration = exp.get('duration', 'N/A')
                        print(f"    - {title} at {company} ({duration})")

            # Display AI summary
            summary = result.get('ai_summary', '')
            if summary:
                print(f"\n🤖 AI SUMMARY:")
                print(f"  {summary}")

            # Display metadata
            metadata = result.get('metadata', {})
            if metadata:
                print(f"\n📈 METADATA:")
                print(f"  Text length: {metadata.get('text_length', 0)} characters")
                print(f"  Word count: {metadata.get('word_count', 0)} words")
                print(f"  LLM used: {metadata.get('llm_used', 'Unknown')}")

                sections = metadata.get('sections_found', {})
                found_sections = [k for k, v in sections.items() if v]
                print(f"  Sections found: {', '.join(found_sections)}")

        else:
            print("❌ CV parsing failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during testing: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()
        return False

    return True


def test_model_loading():
    """Test if the LLM model loads correctly"""
    print("\n" + "=" * 50)
    print("🧪 TESTING MODEL LOADING")
    print("=" * 50)

    try:
        from ai_engine.services.llm_service import LLMService

        print("📋 Initializing LLM Service...")
        llm = LLMService()

        print("🔄 Loading model...")
        success = llm.load_model()

        if success:
            print("✅ Model loaded successfully!")

            # Test basic generation
            print("🧪 Testing basic text generation...")
            test_response = llm.generate_resume_summary("Test CV content", max_length=50)

            if test_response.get('success'):
                print("✅ Text generation working!")
                print(f"Generated text: {test_response.get('summary', 'N/A')}")
            else:
                print("❌ Text generation failed!")
                print(f"Error: {test_response.get('error', 'Unknown')}")
                return False
        else:
            print("❌ Model loading failed!")
            return False

    except Exception as e:
        print(f"❌ Exception during model testing: {e}")
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("🚀 Starting CV Parser Tests...")
    print(f"📅 Test started at: {datetime.now()}")

    # Test model loading first
    model_test_passed = test_model_loading()

    # Test CV parsing
    cv_test_passed = test_cv_parser()

    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Model Loading: {'✅ PASSED' if model_test_passed else '❌ FAILED'}")
    print(f"CV Parsing: {'✅ PASSED' if cv_test_passed else '❌ FAILED'}")
    print(f"Overall: {'✅ ALL TESTS PASSED' if (model_test_passed and cv_test_passed) else '❌ SOME TESTS FAILED'}")
    print(f"📅 Test completed at: {datetime.now()}")

    if not (model_test_passed and cv_test_passed):
        sys.exit(1)