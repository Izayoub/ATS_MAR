#!/usr/bin/env python3
"""
Script simple pour tester un CV
Place ton fichier CV dans le même dossier et renomme-le 'test_cv.pdf' ou 'test_cv.txt'
"""
import sys
import os
from pathlib import Path


import django

# Add the project root to Python path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ATS_MA.settings')
django.setup()
def find_cv_file():
    """Cherche un fichier CV dans le répertoire courant"""
    current_dir = Path('.')

    # Chercher des fichiers CV courants
    cv_patterns = [
        'test_cv.pdf', 'test_cv.txt',
        'cv.pdf', 'cv.txt',
        'mon_cv.pdf', 'mon_cv.txt',
        'resume.pdf', 'resume.txt'
    ]

    for pattern in cv_patterns:
        cv_file = current_dir / pattern
        if cv_file.exists():
            return cv_file

    # Chercher tous les PDF et TXT
    pdf_files = list(current_dir.glob('*.pdf'))
    txt_files = list(current_dir.glob('*.txt'))

    all_files = pdf_files + txt_files

    if all_files:
        print("📁 Fichiers trouvés:")
        for i, file in enumerate(all_files, 1):
            print(f"  {i}. {file.name}")

        while True:
            try:
                choice = input(f"\nChoisissez un fichier (1-{len(all_files)}) ou 'q' pour quitter: ")
                if choice.lower() == 'q':
                    return None

                index = int(choice) - 1
                if 0 <= index < len(all_files):
                    return all_files[index]
                else:
                    print("❌ Numéro invalide")

            except ValueError:
                print("❌ Veuillez entrer un numéro valide")

    return None


def main():
    print("🔍 RECHERCHE DE FICHIER CV...")

    cv_file = find_cv_file()

    if not cv_file:
        print("\n❌ Aucun fichier CV trouvé!")
        print("\n💡 Pour utiliser ce script:")
        print("   1. Placez votre CV dans ce dossier")
        print("   2. Nommez-le 'test_cv.pdf' ou 'test_cv.txt'")
        print("   3. Ou relancez le script pour choisir parmi les fichiers disponibles")
        print("\n🔧 Ou utilisez le script complet avec:")
        print("   python real_cv_test.py chemin/vers/votre/cv.pdf")
        return

    print(f"✅ Fichier sélectionné: {cv_file.name}")

    # Import et utilisation du processeur principal
    try:
        # Import de la fonction de traitement du script principal
        from pathlib import Path
        import sys

        # Simulation de l'appel au script principal
        sys.argv = ['real_cv_test.py', str(cv_file)]

        # Import et exécution
        exec(open('real_cv_test.py').read())

    except FileNotFoundError:
        print("❌ Script principal 'real_cv_test.py' non trouvé")
        print("💡 Assurez-vous que les deux scripts sont dans le même dossier")
    except Exception as e:
        print(f"❌ Erreur: {e}")


if __name__ == "__main__":
    main()