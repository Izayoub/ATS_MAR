# test_parser.py
import json
from dataclasses import asdict
from ai_engine.services.cv_parser import CVParser
import os
# 1. Crée une instance
try:
    parser = CVParser()
except Exception as e:
    print(f"❌ Échec de création du parser : {e}")
    exit()

# 2. Chemins vers les PDF
cv_pdf_path = "C:/Users/honor/ATS/ATS_MA/ai_engine/tests/AYOUB_IZEM_CV.pdf"
job_pdf_path = "C:/Users/honor/ATS/ATS_MA/ai_engine/tests/4WklO7AsEe.pdf"

# Vérifie que les fichiers existent

if not os.path.exists(cv_pdf_path):
    print(f"❌ Fichier CV non trouvé : {cv_pdf_path}")
    exit()
if not os.path.exists(job_pdf_path):
    print(f"❌ Fichier offre non trouvé : {job_pdf_path}")
    exit()

# 3. Test : CV → JSON
print("📄 Parsing du CV...")
try:
    cv_result = parser.parse_cv_from_pdf(cv_pdf_path)

    # ✅ Ici : cv_result est un objet ParsingResult, pas un dict
    if hasattr(cv_result, 'success') and cv_result.success:
        print("✅ CV parsé avec succès !")
        # ✅ Convertir en dict si c'est une dataclass
        data_to_print = asdict(cv_result.data) if hasattr(cv_result.data, "__dataclass_fields__") else cv_result.data
        print(json.dumps(data_to_print, indent=2, ensure_ascii=False))
    else:
        error_msg = getattr(cv_result, 'error', 'Inconnu')
        print(f"❌ Échec du parsing CV : {error_msg}")
        if hasattr(cv_result, 'errors') and cv_result.errors:
            print(f"Erreurs : {cv_result.errors}")
except Exception as e:
    print(f"❌ Erreur critique : {e}")

# 4. Test : Offre → JSON
print("\n📋 Parsing de l'offre...")
try:
    job_result = parser.parse_job_from_pdf(job_pdf_path)

    if hasattr(job_result, 'success') and job_result.success:
        print("✅ Offre parsée avec succès !")
        data_to_print = asdict(job_result.data) if hasattr(job_result.data, "__dataclass_fields__") else job_result.data
        print(json.dumps(data_to_print, indent=2, ensure_ascii=False))
    else:
        error_msg = getattr(job_result, 'error', 'Inconnu')
        print(f"❌ Échec du parsing offre : {error_msg}")
        if hasattr(job_result, 'errors') and job_result.errors:
            print(f"Erreurs : {job_result.errors}")
except Exception as e:
    print(f"❌ Erreur critique : {e}")