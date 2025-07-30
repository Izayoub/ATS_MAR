import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_MA.settings')
django.setup()


"""
Simple test script for CV Parser Service
"""
import sys
import time
import psutil
import threading
from datetime import datetime
import traceback

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))


def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def timeout_handler(timeout_seconds):
    """Handler for timeout"""
    time.sleep(timeout_seconds)
    print(f"\n⏰ TIMEOUT: Operation exceeded {timeout_seconds} seconds!")
    print(f"💾 Current memory usage: {get_memory_usage():.1f} MB")
    print("🔄 This might be normal for first-time model loading...")
    print("💡 Consider increasing timeout or checking system resources")
    return


class TimeoutTest:
    def __init__(self, timeout_seconds=300):  # 5 minutes default
        self.timeout_seconds = timeout_seconds
        self.completed = False

    def run_with_timeout(self, func, *args, **kwargs):
        """Run function with timeout monitoring"""
        # Start timeout thread
        timeout_thread = threading.Thread(target=timeout_handler, args=(self.timeout_seconds,))
        timeout_thread.daemon = True
        timeout_thread.start()

        start_time = time.time()
        start_memory = get_memory_usage()

        print(f"⏱️  Starting with {self.timeout_seconds}s timeout...")
        print(f"💾 Initial memory: {start_memory:.1f} MB")

        try:
            result = func(*args, **kwargs)
            self.completed = True

            end_time = time.time()
            end_memory = get_memory_usage()

            print(f"✅ Completed in {end_time - start_time:.2f} seconds")
            print(f"💾 Final memory: {end_memory:.1f} MB ({end_memory - start_memory:+.1f} MB)")

            return result

        except Exception as e:
            end_time = time.time()
            end_memory = get_memory_usage()

            print(f"❌ Failed after {end_time - start_time:.2f} seconds")
            print(f"💾 Memory at failure: {end_memory:.1f} MB")
            print(f"Error: {e}")
            raise


def test_model_loading_with_monitoring():
    """Test model loading with detailed monitoring"""
    print("=" * 60)
    print("🧪 TESTING MODEL LOADING WITH MONITORING")
    print("=" * 60)

    try:
        from ai_engine.services.llm_service import LLMService
        print("✅ LLMService imported successfully")

        print("\n📋 Creating LLM Service instance...")
        llm = LLMService()
        print(f"💾 Memory after LLMService init: {get_memory_usage():.1f} MB")

        def load_model_func():
            print("🔄 Starting model loading...")
            success = llm.load_model()
            print(f"📊 Model loading result: {success}")
            return success

        # Test with 5-minute timeout
        timeout_test = TimeoutTest(timeout_seconds=300)
        success = timeout_test.run_with_timeout(load_model_func)

        if timeout_test.completed:
            if success:
                print("✅ Model loaded successfully!")

                # Test basic functionality
                print("\n🧪 Testing basic text generation...")
                test_response = llm.generate_resume_summary("Test content", max_length=20)

                if test_response.get('success'):
                    print("✅ Basic generation works!")
                    return True
                else:
                    print(f"❌ Generation failed: {test_response.get('error')}")
                    return False
            else:
                print("❌ Model loading failed!")
                return False
        else:
            print("⏰ Model loading timed out!")
            return False

    except Exception as e:
        print(f"❌ Exception during model testing: {e}")
        traceback.print_exc()
        return False


def test_cv_parser_fallback():
    """Test CV parser with LLM disabled (fallback mode)"""
    print("\n" + "=" * 60)
    print("🧪 TESTING CV PARSER (FALLBACK MODE)")
    print("=" * 60)

    try:
        from ai_engine.services.cv_parser import CVParserService

        print("📋 Creating CV Parser (fallback mode)...")
        parser = CVParserService()

        # Force fallback mode by not loading the model
        parser.is_loaded = False

        sample_cv = """
        Jean Dupont
        Développeur Python
        Email: jean@email.com
        Téléphone: +212612345678

        EXPÉRIENCE: 3 ans d'expérience en Python, Django, JavaScript

        COMPÉTENCES: Python, JavaScript, Django, MySQL, Git

        LANGUES: Français, Anglais
        """

        print("🔄 Processing CV in fallback mode...")
        start_time = time.time()
        result = parser.process(sample_cv)
        process_time = time.time() - start_time

        print(f"⏱️  Processing completed in {process_time:.2f} seconds")

        if result.get('success'):
            print("✅ Fallback processing successful!")

            # Show results
            contact = result.get('contact', {})
            skills = result.get('skills', {})

            print(f"📞 Contact info found: {len(contact)} fields")
            print(f"🛠️  Technical skills: {len(skills.get('technical_skills', []))}")
            print(f"🗣️  Languages: {len(skills.get('languages', []))}")

            return True
        else:
            print(f"❌ Fallback processing failed: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ Exception during fallback testing: {e}")
        traceback.print_exc()
        return False


def check_system_resources():
    """Check if system has enough resources for model loading"""
    print("=" * 60)
    print("🔍 SYSTEM RESOURCE CHECK")
    print("=" * 60)

    # Memory check
    memory = psutil.virtual_memory()
    memory_gb = memory.total / (1024 ** 3)
    available_gb = memory.available / (1024 ** 3)

    print(f"💾 Total RAM: {memory_gb:.1f} GB")
    print(f"💾 Available RAM: {available_gb:.1f} GB")
    print(f"💾 Used RAM: {memory.percent:.1f}%")

    # Disk space check
    disk = psutil.disk_usage('/')
    disk_free_gb = disk.free / (1024 ** 3)

    print(f"💿 Free disk space: {disk_free_gb:.1f} GB")

    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if available_gb < 4:
        print("⚠️  Low available RAM. Model loading may be slow or fail.")
        print("   Consider closing other applications.")
    else:
        print("✅ Sufficient RAM available.")

    if disk_free_gb < 5:
        print("⚠️  Low disk space. May affect model caching.")
    else:
        print("✅ Sufficient disk space available.")

    return available_gb >= 3  # Minimum 3GB recommended


if __name__ == "__main__":
    print("🚀 CV Parser Diagnostic Test")
    print(f"📅 Started at: {datetime.now()}")
    print(f"🐍 Python version: {sys.version}")

    # Check system resources
    sufficient_resources = check_system_resources()

    if not sufficient_resources:
        print("\n⚠️  System resources may be insufficient for model loading.")
        print("🔄 Proceeding with fallback testing only...")

        # Test fallback mode only
        fallback_passed = test_cv_parser_fallback()

        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC RESULTS")
        print("=" * 60)
        print(f"System Resources: {'⚠️  INSUFFICIENT' if not sufficient_resources else '✅ SUFFICIENT'}")
        print(f"Fallback Mode: {'✅ WORKING' if fallback_passed else '❌ FAILED'}")
        print("\n💡 Your CV parser can work in fallback mode (regex-based) even without the LLM model.")

    else:
        print("\n✅ System resources look good. Testing full functionality...")

        # Test model loading
        model_passed = test_model_loading_with_monitoring()

        # Test fallback as backup
        fallback_passed = test_cv_parser_fallback()

        print("\n" + "=" * 60)
        print("📊 DIAGNOSTIC RESULTS")
        print("=" * 60)
        print(f"System Resources: {'✅ SUFFICIENT' if sufficient_resources else '⚠️  INSUFFICIENT'}")
        print(f"Model Loading: {'✅ WORKING' if model_passed else '❌ FAILED/TIMEOUT'}")
        print(f"Fallback Mode: {'✅ WORKING' if fallback_passed else '❌ FAILED'}")

        if not model_passed and fallback_passed:
            print("\n💡 Model loading failed/timed out, but fallback mode works.")
            print("   Your CV parser will use regex-based extraction instead of AI.")

    print(f"\n📅 Completed at: {datetime.now()}")