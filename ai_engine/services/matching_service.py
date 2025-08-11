# matching_service_simplified.py
# Service de matching CV ↔ Offre d'emploi simplifié et adaptatif
# Optimisé pour entreprise tech avec CV multi-domaines

import numpy as np
from sentence_transformers import SentenceTransformer
from typing import Dict, List, Tuple, Optional
import re
import time
import logging
from functools import lru_cache

# Configuration du logging simple
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MatchingService')


# ================================
# 1. CONFIGURATION SIMPLIFIÉE ADAPTATIVE
# ================================

class AdaptiveConfig:
    """Configuration adaptative selon le domaine du CV et poste tech"""

    # Poids adaptés pour entreprise tech avec CV multi-domaines
    WEIGHTS = {
        "tech_to_tech": {
            "competences_techniques": 35,  # Priorité max pour tech→tech
            "projets": 15,
            "experience_annees": 15,
            "formation": 10,
            "soft_skills": 10,
            "certifications": 10,
            "langues": 5
        },
        "business_to_tech": {
            "soft_skills": 25,  # Soft skills importantes
            "competences_techniques": 20,  # Tech important même pour non-tech
            "experience_annees": 20,
            "formation": 15,
            "projets": 10,
            "langues": 5,
            "certifications": 5
        },
        "sales_to_tech": {
            "soft_skills": 30,  # Communication cruciale
            "langues": 20,  # Langues importantes pour sales
            "competences_techniques": 15,  # Base tech requise
            "experience_annees": 15,
            "formation": 10,
            "projets": 5,
            "certifications": 5
        },
        "other_to_tech": {
            "soft_skills": 25,
            "formation": 20,
            "competences_techniques": 20,
            "experience_annees": 15,
            "projets": 10,
            "langues": 5,
            "certifications": 5
        }
    }

    # Bonus pour transitions cross-domaine prometteuses
    CROSS_DOMAIN_BONUS = {
        ("business", "tech"): 0.15,  # +15% pour business vers tech
        ("sales", "tech"): 0.12,  # +12% pour sales vers tech
        ("other", "tech"): 0.08,  # +8% pour autres domaines
    }

    @classmethod
    def get_weights(cls, cv_domain: str) -> Dict:
        """Retourne les poids adaptés au domaine du CV"""
        config_key = f"{cv_domain}_to_tech"
        return cls.WEIGHTS.get(config_key, cls.WEIGHTS["other_to_tech"])

    @classmethod
    def get_bonus(cls, cv_domain: str) -> float:
        """Retourne le bonus cross-domaine"""
        if cv_domain == "tech":
            return 0.0  # Pas de bonus pour tech→tech
        return cls.CROSS_DOMAIN_BONUS.get((cv_domain, "tech"), 0.0)


# ================================
# 2. NORMALISATION SIMPLIFIÉE MULTI-DOMAINES
# ================================

class SkillNormalizerSimple:
    """Normalisation simplifiée pour tous domaines"""

    # Compétences techniques étendues
    TECH_SKILLS = {
        "python": ["python", "django", "flask", "fastapi"],
        "javascript": ["javascript", "js", "react", "vue", "angular", "node"],
        "java": ["java", "spring", "kotlin"],
        "data": ["sql", "postgresql", "mysql", "mongodb", "excel", "powerbi"],
        "cloud": ["aws", "azure", "gcp", "docker", "kubernetes"],
        "tools": ["git", "jira", "confluence", "slack"]
    }

    # Compétences business/product
    BUSINESS_SKILLS = {
        "management": ["management", "gestion", "leadership", "encadrement"],
        "product": ["product management", "product owner", "po", "roadmap"],
        "analysis": ["analyse", "business analysis", "requirements", "process"],
        "project": ["project management", "scrum", "agile", "planning"]
    }

    # Compétences sales/commercial
    SALES_SKILLS = {
        "sales": ["vente", "commercial", "négociation", "prospection"],
        "communication": ["communication", "présentation", "relationnel"],
        "crm": ["crm", "salesforce", "hubspot", "pipeline"]
    }

    # Soft skills universelles
    SOFT_SKILLS = {
        "leadership": ["leadership", "encadrement", "management"],
        "communication": ["communication", "relationnel", "présentation"],
        "teamwork": ["équipe", "collaboration", "coopération"],
        "problem_solving": ["résolution", "analyse", "diagnostic"],
        "adaptability": ["adaptabilité", "flexibilité", "apprentissage"]
    }

    def __init__(self):
        # Combine tous les mappings
        self.all_mappings = {
            **self.TECH_SKILLS,
            **self.BUSINESS_SKILLS,
            **self.SALES_SKILLS,
            **self.SOFT_SKILLS
        }

        # Création du mapping inverse
        self.reverse_map = {}
        for standard, variants in self.all_mappings.items():
            for variant in variants:
                self.reverse_map[variant.lower()] = standard

    def normalize(self, skill: str) -> str:
        """Normalise une compétence"""
        if not skill:
            return ""

        clean_skill = skill.lower().strip()

        # Recherche exacte
        if clean_skill in self.reverse_map:
            return self.reverse_map[clean_skill]

        # Recherche par sous-chaîne
        for variant, standard in self.reverse_map.items():
            if variant in clean_skill or clean_skill in variant:
                return standard

        return clean_skill

    def get_must_have(self, requirements: List[str]) -> List[str]:
        """Identifie les compétences obligatoires"""
        must_have = []
        critical_words = ["obligatoire", "requis", "indispensable", "mandatory", "required", "must"]

        for req in requirements:
            req_str = str(req).lower()
            if any(word in req_str for word in critical_words):
                # Nettoie et normalise
                clean_req = re.sub(r'\b(' + '|'.join(critical_words) + r')\b', '', req_str)
                clean_req = re.sub(r'[^\w\s]', ' ', clean_req).strip()
                clean_req = re.sub(r'\s+', ' ', clean_req)

                if clean_req:
                    must_have.append(self.normalize(clean_req))

        return must_have

    def detect_buzzwords(self, text: str) -> Dict:
        """Détection simplifiée des buzzwords"""
        if not text:
            return {"count": 0, "density": 0, "penalty": 0}

        buzzwords = [
            "disruptif", "révolutionnaire", "game-changer", "cutting-edge",
            "paradigme", "synergies", "excellence", "passion", "innovant",
            "thought leader", "transformational", "state-of-the-art"
        ]

        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)

        if total_words == 0:
            return {"count": 0, "density": 0, "penalty": 0}

        detected = [bw for bw in buzzwords if bw in text_lower]
        density = len(detected) / total_words

        # Pénalité progressive
        penalty = 0
        if density > 0.1:  # Plus de 10%
            penalty = 0.2
        elif density > 0.05:  # Plus de 5%
            penalty = 0.1

        return {
            "count": len(detected),
            "density": round(density * 100, 1),
            "penalty": penalty,
            "detected": detected[:5]
        }


# ================================
# 3. DÉTECTION DE DOMAINE SIMPLIFIÉE
# ================================

def detect_cv_domain(cv_data: Dict) -> str:
    """Détecte le domaine du CV de manière simple et efficace"""
    try:
        titre = str(cv_data.get("titre_candidat", "")).lower()
        competences = " ".join(str(c) for c in cv_data.get("competences_techniques", [])).lower()
        experience = " ".join(str(e) for e in cv_data.get("experience", [])).lower()

        full_text = f"{titre} {competences} {experience}"

        # Mots-clés par domaine
        tech_keywords = [
            "développeur", "dev", "engineer", "ingénieur", "programmeur",
            "python", "java", "react", "javascript", "web", "software",
            "tech", "informatique", "système", "architecture"
        ]

        business_keywords = [
            "business", "product", "consultant", "analyst", "manager",
            "gestion", "strategy", "operations", "finance", "marketing",
            "project manager", "product owner", "ba", "business analyst"
        ]

        sales_keywords = [
            "commercial", "sales", "vente", "business development",
            "account", "client", "customer", "négociation", "prospection"
        ]

        # Comptage des occurrences
        tech_score = sum(1 for kw in tech_keywords if kw in full_text)
        business_score = sum(1 for kw in business_keywords if kw in full_text)
        sales_score = sum(1 for kw in sales_keywords if kw in full_text)

        # Décision simple
        max_score = max(tech_score, business_score, sales_score)

        if tech_score == max_score and tech_score > 0:
            return "tech"
        elif business_score == max_score and business_score > 0:
            return "business"
        elif sales_score == max_score and sales_score > 0:
            return "sales"
        else:
            return "other"

    except Exception as e:
        logger.warning(f"Erreur détection domaine: {e}")
        return "other"


# ================================
# 4. GESTIONNAIRE DE MODÈLE SIMPLIFIÉ
# ================================

class SimpleModelManager:
    """Gestionnaire de modèle simplifié avec BGE-M3"""

    def __init__(self):
        self.model = None
        self.cache = {}  # Cache simple en mémoire
        self._load_model()

    def _load_model(self):
        """Charge BGE-M3 une seule fois"""
        try:
            logger.info("Chargement de BGE-M3...")
            self.model = SentenceTransformer('BAAI/bge-m3')
            logger.info("BGE-M3 chargé avec succès")
        except Exception as e:
            logger.error(f"Erreur chargement modèle: {e}")
            raise

    @lru_cache(maxsize=500)
    def encode(self, text: str) -> Optional[np.ndarray]:
        """Encode avec cache LRU intégré"""
        if not text or not text.strip():
            return None

        try:
            return self.model.encode(text.strip(), normalize_embeddings=True)
        except Exception as e:
            logger.error(f"Erreur encodage: {e}")
            return None

    def is_ready(self) -> bool:
        return self.model is not None


# Instance globale
model_manager = SimpleModelManager()
skill_normalizer = SkillNormalizerSimple()


# ================================
# 5. FONCTIONS UTILITAIRES SIMPLIFIÉES
# ================================

def safe_get(data: Dict, key: str, default="", as_list=False):
    """Récupération sécurisée universelle"""
    try:
        value = data.get(key, default)

        if as_list:
            if isinstance(value, list):
                return [str(v) for v in value if v]
            elif value:
                return [str(value)]
            else:
                return []
        else:
            return str(value) if value else default
    except:
        return [] if as_list else default


def cosine_similarity(vec1, vec2) -> float:
    """Similarité cosinus simplifiée"""
    if vec1 is None or vec2 is None:
        return 0.0

    try:
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))
    except:
        return 0.0


def jaccard_similarity(list1: List[str], list2: List[str]) -> float:
    """Jaccard simplifié avec normalisation"""
    try:
        # Normalisation
        set1 = {skill_normalizer.normalize(str(item)) for item in list1 if item}
        set2 = {skill_normalizer.normalize(str(item)) for item in list2 if item}

        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0

        intersection = len(set1 & set2)
        union = len(set1 | set2)

        return intersection / union if union > 0 else 0.0
    except:
        return 0.0


# ================================
# 6. FONCTION PRINCIPALE SIMPLIFIÉE
# ================================

def calculate_adaptive_match_score(cv_json: Dict, job_json: Dict, cv_id: str = "unknown") -> Dict:
    """
    Calcul de matching simplifié et adaptatif pour entreprise tech
    """
    start_time = time.time()

    try:
        # 1. Détection automatique du domaine CV
        cv_domain = detect_cv_domain(cv_json)

        # 2. Configuration adaptée
        weights = AdaptiveConfig.get_weights(cv_domain)
        cross_domain_bonus = AdaptiveConfig.get_bonus(cv_domain)

        # 3. Extraction sécurisée des données
        cv_data = {
            "titre": safe_get(cv_json, "titre_candidat"),
            "profil": safe_get(cv_json, "profil_resume"),
            "formations": safe_get(cv_json, "formations", as_list=True),
            "experience_years": int(re.search(r'\d+', str(cv_json.get("experience_years", "0"))).group() or 0),
            "competences_tech": safe_get(cv_json, "competences_techniques", as_list=True),
            "competences_info": safe_get(cv_json, "competences_informatiques", as_list=True),
            "langues": safe_get(cv_json, "langues", as_list=True),
            "certifications": safe_get(cv_json, "certifications", as_list=True),
            "projets": safe_get(cv_json, "projets", as_list=True),
            "soft_skills": safe_get(cv_json, "soft_skills", as_list=True),
        }

        job_exigences = job_json.get("exigences", {})
        job_data = {
            "titre": safe_get(job_json, "titre_poste"),
            "missions": safe_get(job_json, "missions"),
            "formation_req": safe_get(job_exigences, "formation_requise"),
            "experience_req": int(re.search(r'\d+', str(job_exigences.get("annees_experience", "0"))).group() or 0),
            "comp_obligatoires": safe_get(job_exigences, "competences_obligatoires", as_list=True),
            "comp_souhaitees": safe_get(job_exigences, "competences_souhaitees", as_list=True),
            "langues": safe_get(job_exigences, "langues", as_list=True),
            "certifications": safe_get(job_exigences, "certifications", as_list=True),
            "outils": safe_get(job_exigences, "outils", as_list=True),
            "soft_skills": safe_get(job_exigences, "qualites_humaines", as_list=True),
        }

        # 4. Vérification des must-have
        all_job_requirements = job_data["comp_obligatoires"] + job_data["comp_souhaitees"]
        must_have_skills = skill_normalizer.get_must_have(all_job_requirements)

        cv_all_skills = cv_data["competences_tech"] + cv_data["competences_info"]
        cv_normalized_skills = {skill_normalizer.normalize(skill) for skill in cv_all_skills}

        missing_must_have = [skill for skill in must_have_skills
                             if skill not in cv_normalized_skills]

        if missing_must_have:
            # Échec sur must-have = score 0
            return {
                "total_score": 0,
                "confidence": 0,
                "cv_domain": cv_domain,
                "must_have_failed": True,
                "missing_must_have": missing_must_have,
                "interpretation": {
                    "level": "rejected",
                    "message": f"Compétences obligatoires manquantes: {', '.join(missing_must_have)}",
                    "action": "REJETÉ"
                },
                "execution_time_ms": round((time.time() - start_time) * 1000, 2)
            }

        # 5. Calculs de matching par champ
        scores = {}

        # Titre
        scores["titre"] = cosine_similarity(
            model_manager.encode(cv_data["titre"]),
            model_manager.encode(job_data["titre"])
        )

        # Profil/Missions
        scores["profil"] = cosine_similarity(
            model_manager.encode(cv_data["profil"]),
            model_manager.encode(job_data["missions"])
        )

        # Formation (score simple basé sur niveau)
        cv_formation_level = 0
        for formation in cv_data["formations"]:
            form_str = str(formation).lower()
            if "master" in form_str or "bac+5" in form_str:
                cv_formation_level = max(cv_formation_level, 5)
            elif "licence" in form_str or "bac+3" in form_str:
                cv_formation_level = max(cv_formation_level, 3)
            elif "bts" in form_str or "dut" in form_str or "bac+2" in form_str:
                cv_formation_level = max(cv_formation_level, 2)

        job_formation_level = 5 if "bac+5" in job_data["formation_req"].lower() else 3
        scores["formation"] = min(1.0, cv_formation_level / job_formation_level) if job_formation_level > 0 else 1.0

        # Expérience
        scores["experience_annees"] = min(1.0, cv_data["experience_years"] / job_data["experience_req"]) if job_data[
                                                                                                                "experience_req"] > 0 else 1.0

        # Compétences techniques (Jaccard + sémantique)
        cv_tech = cv_data["competences_tech"]
        job_tech = job_data["comp_obligatoires"] + job_data["comp_souhaitees"]

        jaccard_tech = jaccard_similarity(cv_tech, job_tech)
        semantic_tech = cosine_similarity(
            model_manager.encode(" ".join(cv_tech)),
            model_manager.encode(" ".join(job_tech))
        )

        # Combinaison 50/50 Jaccard et sémantique
        scores["competences_techniques"] = (jaccard_tech + semantic_tech) / 2

        # Compétences informatiques
        scores["competences_informatiques"] = jaccard_similarity(cv_data["competences_info"], job_data["outils"])

        # Langues (score simplifié)
        if not job_data["langues"]:
            scores["langues"] = 1.0
        else:
            cv_langues_text = " ".join(cv_data["langues"])
            job_langues_text = " ".join(job_data["langues"])
            scores["langues"] = cosine_similarity(
                model_manager.encode(cv_langues_text),
                model_manager.encode(job_langues_text)
            )

        # Certifications
        scores["certifications"] = jaccard_similarity(cv_data["certifications"], job_data["certifications"])

        # Projets
        cv_projets_text = " ".join(str(p) for p in cv_data["projets"])
        scores["projets"] = cosine_similarity(
            model_manager.encode(cv_projets_text),
            model_manager.encode(job_data["missions"])
        )

        # Soft skills avec enrichissement
        scores["soft_skills"] = jaccard_similarity(cv_data["soft_skills"], job_data["soft_skills"])

        # 6. Calcul du score global pondéré
        total_weighted_score = 0.0
        total_weight = 0.0

        for field, score in scores.items():
            if field in weights:
                weight = weights[field]
                total_weighted_score += score * weight
                total_weight += weight

        base_score = (total_weighted_score / total_weight) * 100 if total_weight > 0 else 0

        # 7. Application du bonus cross-domaine
        final_score = base_score * (1 + cross_domain_bonus)

        # 8. Analyse des buzzwords et pénalité
        cv_full_text = f"{cv_data['titre']} {cv_data['profil']}"
        buzzword_analysis = skill_normalizer.detect_buzzwords(cv_full_text)

        if buzzword_analysis["penalty"] > 0:
            final_score *= (1 - buzzword_analysis["penalty"])

        final_score = max(0, min(100, int(final_score)))

        # 9. Confiance et interprétation
        confidence = 85 if cv_domain == "tech" else 70  # Plus de confiance pour profils tech
        confidence -= buzzword_analysis["penalty"] * 30  # Pénalité confiance buzzwords
        confidence = max(0, min(100, confidence))

        # Interprétation adaptée au domaine
        if final_score >= 80:
            level, message, action = "excellent", "Candidat très bien aligné", "PRIORISER"
        elif final_score >= 65:
            level, message, action = "good", "Bon profil avec potentiel", "RECOMMANDÉ"
        elif final_score >= 50:
            level, message, action = "fair", "Profil intéressant à développer", "À CONSIDÉRER"
        else:
            level, message, action = "poor", "Profil peu adapté", "NON RECOMMANDÉ"

        # Ajustement du message selon le domaine
        if cv_domain != "tech" and final_score >= 50:
            message += f" (Transition {cv_domain}→tech possible)"
            if cross_domain_bonus > 0:
                message += f" [Bonus +{cross_domain_bonus * 100:.0f}% appliqué]"

        # 10. Recommandations intelligentes
        recommendations = []

        # Recommandations selon le domaine et les scores
        if cv_domain != "tech":
            if scores.get("competences_techniques", 0) < 0.5:
                recommendations.append({
                    "type": "skill_development",
                    "message": f"Renforcer les compétences techniques pour transition {cv_domain}→tech",
                    "priority": "high"
                })

        if buzzword_analysis["count"] > 3:
            recommendations.append({
                "type": "content_quality",
                "message": f"Réduire les buzzwords dans le CV ({buzzword_analysis['count']} détectés)",
                "priority": "medium"
            })

        if scores.get("soft_skills", 0) < 0.4:
            recommendations.append({
                "type": "soft_skills",
                "message": "Développer et mettre en avant les soft skills",
                "priority": "medium"
            })

        # Résultat final simplifié
        result = {
            "total_score": final_score,
            "confidence": round(confidence, 1),
            "cv_domain": cv_domain,
            "interpretation": {
                "level": level,
                "message": message,
                "action": action
            },
            "scores_detail": {field: round(score * 100) for field, score in scores.items()},
            "weights_used": weights,
            "cross_domain_bonus": cross_domain_bonus,
            "buzzword_analysis": buzzword_analysis,
            "recommendations": recommendations,
            "must_have_failed": False,
            "execution_time_ms": round((time.time() - start_time) * 1000, 2)
        }

        return result

    except Exception as e:
        execution_time = (time.time() - start_time) * 1000
        logger.error(f"Erreur matching: {e}")

        return {
            "total_score": 0,
            "confidence": 0,
            "cv_domain": "unknown",
            "interpretation": {
                "level": "error",
                "message": f"Erreur lors du calcul: {str(e)[:50]}",
                "action": "ERREUR"
            },
            "error": str(e),
            "execution_time_ms": round(execution_time, 2)
        }


# ================================
# 7. MATCHING PAR LOT SIMPLIFIÉ
# ================================

def batch_matching_simple(cv_list: List[Dict], job_data: Dict, top_k: int = 10) -> List[Dict]:
    """Traitement par lot simplifié avec ranking adaptatif"""

    if not cv_list:
        return []

    results = []
    start_time = time.time()

    logger.info(f"Traitement par lot: {len(cv_list)} CV")

    # Phase 1: Calcul des scores
    for i, cv_data in enumerate(cv_list):
        cv_id = cv_data.get("id", f"cv_{i}")

        result = calculate_adaptive_match_score(cv_data, job_data, cv_id)

        # Filtre les échecs must-have
        if not result.get("must_have_failed", False):
            results.append({
                "cv_id": cv_id,
                "score": result["total_score"],
                "cv_domain": result["cv_domain"],
                "result": result,
                "rank": 0  # Sera mis à jour après tri
            })

    # Phase 2: Tri adaptatif
    # Priorise tech > business > sales > other à score égal
    domain_priority = {"tech": 4, "business": 3, "sales": 2, "other": 1}

    results.sort(key=lambda x: (
        x["score"],  # Score principal
        domain_priority.get(x["cv_domain"], 0),  # Priorité domaine
        -x["result"].get("execution_time_ms", 0)  # Tie-breaker par temps
    ), reverse=True)

    # Mise à jour des rangs
    for i, result in enumerate(results):
        result["rank"] = i + 1

    total_time = time.time() - start_time
    logger.info(f"Traitement terminé: {len(results)} candidats en {total_time:.2f}s")

    return results[:top_k]


# ================================
# 8. AFFICHAGE SIMPLIFIÉ
# ================================

def display_simple_results(result: Dict):
    """Affichage simplifié et clair"""
    print("\n" + "=" * 60)
    print("🎯 RÉSULTAT DU MATCHING CV ↔ OFFRE")
    print("=" * 60)

    score = result["total_score"]
    confidence = result["confidence"]
    cv_domain = result["cv_domain"]
    interpretation = result["interpretation"]

    # Score avec indicateur visuel
    if score >= 80:
        indicator = "🟢 EXCELLENT"
    elif score >= 65:
        indicator = "🟡 BON"
    elif score >= 50:
        indicator = "🟠 MOYEN"
    else:
        indicator = "🔴 FAIBLE"

    print(f"\n📊 SCORE: {score}/100 {indicator}")
    print(f"🎯 DOMAINE CV: {cv_domain.upper()}")
    print(f"🔒 CONFIANCE: {confidence}%")
    print(f"💡 {interpretation.get('message', '')}")
    print(f"🎬 ACTION: {interpretation.get('action', '')}")

    # Bonus cross-domaine si applicable
    bonus = result.get("cross_domain_bonus", 0)
    if bonus > 0:
        print(f"🚀 BONUS CROSS-DOMAINE: +{bonus * 100:.0f}%")

    # Buzzwords si détectés
    buzzwords = result.get("buzzword_analysis", {})
    if buzzwords.get("count", 0) > 0:
        print(f"⚠️  BUZZWORDS: {buzzwords['count']} détectés ({buzzwords['density']}%)")

    # Top 3 scores détaillés
    scores_detail = result.get("scores_detail", {})
    if scores_detail:
        print(f"\n📋 TOP 3 CRITÈRES:")
        top_scores = sorted(scores_detail.items(), key=lambda x: x[1], reverse=True)[:3]
        for field, score in top_scores:
            print(f"   • {field.replace('_', ' ').title()}: {score}/100")

    # Recommandations
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n💡 RECOMMANDATIONS:")
        for rec in recommendations[:3]:  # Top 3
            priority = "🔴" if rec.get("priority") == "high" else "🟡"
            print(f"   {priority} {rec.get('message', '')}")

    print(f"\n⏱️  Temps: {result.get('execution_time_ms', 0)}ms")
    print("=" * 60)


# ================================
# 9. ANALYSE DE GAPS SIMPLIFIÉE
# ================================

def analyze_skill_gaps_simple(cv_data: Dict, job_data: Dict) -> Dict:
    """Analyse simplifiée des écarts de compétences"""
    try:
        # Extraction des compétences
        cv_skills = set()
        cv_skills.update(safe_get(cv_data, "competences_techniques", as_list=True))
        cv_skills.update(safe_get(cv_data, "competences_informatiques", as_list=True))

        job_exigences = job_data.get("exigences", {})
        job_skills = set()
        job_skills.update(safe_get(job_exigences, "competences_obligatoires", as_list=True))
        job_skills.update(safe_get(job_exigences, "competences_souhaitees", as_list=True))

        # Normalisation
        cv_normalized = {skill_normalizer.normalize(skill) for skill in cv_skills if skill}
        job_normalized = {skill_normalizer.normalize(skill) for skill in job_skills if skill}

        # Analyse des gaps
        matching = cv_normalized & job_normalized
        missing = job_normalized - cv_normalized
        extra = cv_normalized - job_normalized

        # Analyse sémantique des compétences proches
        transferable_skills = []
        if missing and extra:
            for missing_skill in list(missing)[:3]:  # Top 3 manquantes
                missing_emb = model_manager.encode(missing_skill)
                if missing_emb is not None:
                    best_match = ""
                    best_score = 0.0

                    for extra_skill in extra:
                        extra_emb = model_manager.encode(extra_skill)
                        if extra_emb is not None:
                            similarity = cosine_similarity(missing_emb, extra_emb)
                            if similarity > best_score and similarity > 0.6:
                                best_score = similarity
                                best_match = extra_skill

                    if best_match:
                        transferable_skills.append({
                            "missing": missing_skill,
                            "closest": best_match,
                            "similarity": round(best_score, 2)
                        })

        return {
            "matching_count": len(matching),
            "missing_count": len(missing),
            "extra_count": len(extra),
            "coverage_rate": len(matching) / len(job_normalized) if job_normalized else 1.0,
            "transferable_skills": transferable_skills,
            "missing_skills": list(missing)[:5],  # Top 5
            "extra_skills": list(extra)[:5]  # Top 5
        }

    except Exception as e:
        logger.error(f"Erreur analyse gaps: {e}")
        return {"error": str(e)}


# ================================
# 10. FONCTIONS DE BATCH OPTIMISÉES
# ================================

def rank_candidates_for_tech_company(cv_list: List[Dict], job_data: Dict,
                                     prioritize_tech: bool = True) -> List[Dict]:
    """Ranking spécialisé pour entreprise tech"""

    results = batch_matching_simple(cv_list, job_data, top_k=len(cv_list))

    if not prioritize_tech:
        return results

    # Re-ranking avec priorité aux profils tech à score proche
    tech_prioritized = []
    non_tech = []

    for result in results:
        if result["cv_domain"] == "tech":
            tech_prioritized.append(result)
        else:
            non_tech.append(result)

    # Mélange intelligent : tech d'abord, puis non-tech avec scores élevés
    final_ranking = []
    tech_idx = 0
    non_tech_idx = 0

    while tech_idx < len(tech_prioritized) or non_tech_idx < len(non_tech):
        # Ajoute tech en priorité
        if tech_idx < len(tech_prioritized):
            final_ranking.append(tech_prioritized[tech_idx])
            tech_idx += 1

        # Ajoute non-tech avec score élevé (>70)
        if (non_tech_idx < len(non_tech) and
                non_tech[non_tech_idx]["score"] >= 70):
            final_ranking.append(non_tech[non_tech_idx])
            non_tech_idx += 1

        # Ajoute tech puis non-tech restants alternativement
        if tech_idx < len(tech_prioritized):
            final_ranking.append(tech_prioritized[tech_idx])
            tech_idx += 1

        if non_tech_idx < len(non_tech):
            final_ranking.append(non_tech[non_tech_idx])
            non_tech_idx += 1

    # Mise à jour des rangs
    for i, result in enumerate(final_ranking):
        result["rank"] = i + 1

    return final_ranking


# ================================
# 11. FONCTIONS D'ANALYSE AVANCÉE SIMPLIFIÉES
# ================================

def get_domain_distribution(results: List[Dict]) -> Dict:
    """Analyse de la distribution des domaines des candidats"""
    domain_counts = {"tech": 0, "business": 0, "sales": 0, "other": 0}
    domain_scores = {"tech": [], "business": [], "sales": [], "other": []}

    for result in results:
        domain = result.get("cv_domain", "other")
        score = result.get("score", 0)

        domain_counts[domain] += 1
        domain_scores[domain].append(score)

    # Calcul des moyennes
    domain_averages = {}
    for domain, scores in domain_scores.items():
        domain_averages[domain] = round(sum(scores) / len(scores), 1) if scores else 0

    return {
        "counts": domain_counts,
        "averages": domain_averages,
        "total": len(results)
    }


def suggest_training_paths(cv_data: Dict, job_data: Dict) -> List[Dict]:
    """Suggère des parcours de formation pour transition vers tech"""

    cv_domain = detect_cv_domain(cv_data)
    if cv_domain == "tech":
        return []  # Pas de formation nécessaire

    suggestions = []

    # Analyse des gaps
    gap_analysis = analyze_skill_gaps_simple(cv_data, job_data)
    missing_skills = gap_analysis.get("missing_skills", [])

    # Suggestions selon le domaine d'origine
    if cv_domain == "business":
        suggestions.extend([
            {
                "type": "technical_foundation",
                "title": "Formation Développement Web",
                "skills": ["Python", "JavaScript", "SQL", "Git"],
                "duration": "3-6 mois",
                "priority": "high"
            },
            {
                "type": "methodology",
                "title": "Méthodologies Agiles + DevOps",
                "skills": ["Scrum", "CI/CD", "Docker"],
                "duration": "1-2 mois",
                "priority": "medium"
            }
        ])

    elif cv_domain == "sales":
        suggestions.extend([
            {
                "type": "technical_basics",
                "title": "Bases Techniques + Product Management",
                "skills": ["SQL", "Analytics", "Product Management"],
                "duration": "2-4 mois",
                "priority": "high"
            },
            {
                "type": "customer_tech",
                "title": "Customer Success Tech",
                "skills": ["CRM Tech", "API basics", "Technical Sales"],
                "duration": "1-3 mois",
                "priority": "medium"
            }
        ])

    # Ajout des compétences manquantes spécifiques
    if missing_skills:
        suggestions.append({
            "type": "specific_gaps",
            "title": "Compétences Spécifiques Manquantes",
            "skills": missing_skills[:5],
            "duration": "Variable",
            "priority": "high"
        })

    return suggestions


# ================================
# 12. TESTS SIMPLIFIÉS
# ================================

def run_simplified_tests():
    """Tests simplifiés pour validation"""

    print("🧪 TESTS DU SYSTÈME SIMPLIFIÉ")
    print("=" * 50)

    # Données d'exemple simplifiées
    cv_tech = {
        "titre_candidat": "Développeur Full Stack",
        "profil_resume": "Développeur avec 3 ans d'expérience en Python et React",
        "formations": ["Master Informatique"],
        "experience_years": 3,
        "competences_techniques": ["Python", "React", "PostgreSQL", "Docker"],
        "competences_informatiques": ["Git", "Linux", "AWS"],
        "langues": ["Français: C2", "Anglais: B2"],
        "certifications": ["AWS Developer"],
        "projets": ["Application web e-commerce avec Django et React"],
        "soft_skills": ["teamwork", "problem-solving"]
    }

    cv_business = {
        "titre_candidat": "Product Manager",
        "profil_resume": "Product Manager avec 4 ans d'expérience, passionné par la tech et l'innovation disruptive",
        "formations": ["Master Business"],
        "experience_years": 4,
        "competences_techniques": ["SQL", "Analytics", "Jira"],
        "competences_informatiques": ["Excel", "PowerBI", "Slack"],
        "langues": ["Français: C2", "Anglais: C1"],
        "certifications": ["Scrum Master"],
        "projets": ["Lancement produit SaaS"],
        "soft_skills": ["leadership", "communication", "strategic thinking"]
    }

    cv_sales = {
        "titre_candidat": "Business Development Manager",
        "profil_resume": "Commercial senior avec excellentes skills en négociation",
        "formations": ["Master Commerce"],
        "experience_years": 5,
        "competences_techniques": ["CRM", "Analytics"],
        "competences_informatiques": ["Salesforce", "Excel"],
        "langues": ["Français: C2", "Anglais: C1", "Espagnol: B1"],
        "certifications": [],
        "projets": ["Expansion marché européen"],
        "soft_skills": ["negotiation", "relationship building"]
    }

    job_tech = {
        "titre_poste": "Développeur Backend Senior Python",
        "missions": "Développer des APIs REST performantes avec Python/Django. Collaborer avec l'équipe produit.",
        "exigences": {
            "formation_requise": "Bac+5 Informatique",
            "annees_experience": 3,
            "competences_obligatoires": ["Python OBLIGATOIRE", "PostgreSQL REQUIS"],
            "competences_souhaitees": ["Docker", "AWS", "React"],
            "langues": ["Français: B2", "Anglais: B2"],
            "certifications": ["AWS"],
            "outils": ["Git", "Docker", "Linux"],
            "qualites_humaines": ["autonomie", "teamwork"]
        }
    }

    # Test 1: Profil tech parfait
    print("\n1️⃣ TEST: Profil Tech → Poste Tech")
    result1 = calculate_adaptive_match_score(cv_tech, job_tech, "cv_tech")
    display_simple_results(result1)

    # Test 2: Profil business vers tech
    print("\n2️⃣ TEST: Profil Business → Poste Tech")
    result2 = calculate_adaptive_match_score(cv_business, job_tech, "cv_business")
    display_simple_results(result2)

    # Test 3: Profil sales vers tech
    print("\n3️⃣ TEST: Profil Sales → Poste Tech")
    result3 = calculate_adaptive_match_score(cv_sales, job_tech, "cv_sales")
    display_simple_results(result3)

    # Test 4: Batch avec ranking adaptatif
    print("\n4️⃣ TEST: Ranking Adaptatif pour Entreprise Tech")
    print("-" * 50)

    cv_list = [
        {"id": "cv_001", **cv_tech},
        {"id": "cv_002", **cv_business},
        {"id": "cv_003", **cv_sales}
    ]

    batch_results = rank_candidates_for_tech_company(cv_list, job_tech)

    for result in batch_results:
        cv_id = result["cv_id"]
        score = result["score"]
        domain = result["cv_domain"]
        rank = result["rank"]

        domain_icon = {"tech": "💻", "business": "📊", "sales": "💼", "other": "❓"}

        print(f"#{rank} {domain_icon.get(domain, '❓')} {cv_id}: {score}/100 ({domain.upper()})")

        # Bonus affiché si applicable
        bonus = result["result"].get("cross_domain_bonus", 0)
        if bonus > 0:
            print(f"    🚀 Bonus cross-domaine: +{bonus * 100:.0f}%")

    # Test 5: Distribution des domaines
    print("\n5️⃣ ANALYSE: Distribution des Domaines")
    print("-" * 50)

    distribution = get_domain_distribution(batch_results)

    for domain, count in distribution["counts"].items():
        avg_score = distribution["averages"][domain]
        if count > 0:
            print(f"{domain.upper()}: {count} candidat(s), score moyen: {avg_score}/100")

    # Test 6: Suggestions de formation
    print("\n6️⃣ SUGGESTIONS: Parcours de Formation")
    print("-" * 50)

    training_suggestions = suggest_training_paths(cv_business, job_tech)

    for i, suggestion in enumerate(training_suggestions, 1):
        priority = "🔴" if suggestion.get("priority") == "high" else "🟡"
        print(f"{i}. {priority} {suggestion.get('title', '')}")
        print(f"   Compétences: {', '.join(suggestion.get('skills', []))}")
        print(f"   Durée: {suggestion.get('duration', 'N/A')}")


# ================================
# 13. INTERFACE SIMPLE
# ================================

def quick_match(cv_data: Dict, job_data: Dict) -> Tuple[int, str, str]:
    """Matching ultra-rapide retournant score, domaine et action"""
    try:
        result = calculate_adaptive_match_score(cv_data, job_data)
        return (
            result["total_score"],
            result["cv_domain"],
            result["interpretation"]["action"]
        )
    except:
        return (0, "unknown", "ERREUR")


def display_batch_summary(results: List[Dict]):
    """Affichage résumé pour traitement par lot"""
    if not results:
        print("Aucun résultat à afficher")
        return

    print(f"\n📊 RÉSUMÉ TRAITEMENT PAR LOT ({len(results)} candidats)")
    print("=" * 60)

    # Statistiques globales
    scores = [r["score"] for r in results]
    domains = [r["cv_domain"] for r in results]

    print(f"📈 Score moyen: {sum(scores) / len(scores):.1f}/100")
    print(f"🏆 Meilleur score: {max(scores)}/100")
    print(f"📉 Score minimum: {min(scores)}/100")

    # Distribution par domaine
    domain_counts = {}
    for domain in domains:
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    print(f"\n🎯 Distribution des domaines:")
    for domain, count in domain_counts.items():
        percentage = (count / len(results)) * 100
        print(f"   {domain.upper()}: {count} ({percentage:.1f}%)")

    # Top 5 candidats
    print(f"\n🏅 TOP 5 CANDIDATS:")
    for result in results[:5]:
        cv_id = result["cv_id"]
        score = result["score"]
        domain = result["cv_domain"]
        rank = result["rank"]

        status = "✅" if score >= 70 else "⚠️" if score >= 50 else "❌"
        print(f"   #{rank} {status} {cv_id}: {score}/100 ({domain})")


# ================================
# 14. UTILITAIRES DE PERFORMANCE
# ================================

def benchmark_simplified_vs_original(cv_data: Dict, job_data: Dict, runs: int = 5):
    """Compare performance version simplifiée vs originale"""

    print(f"\n⚡ BENCHMARK PERFORMANCE ({runs} runs)")
    print("=" * 50)

    # Test version simplifiée
    times_simple = []
    for _ in range(runs):
        start = time.time()
        result_simple = calculate_adaptive_match_score(cv_data, job_data)
        times_simple.append((time.time() - start) * 1000)

    avg_time_simple = sum(times_simple) / len(times_simple)
    score_simple = result_simple["total_score"]

    print(f"🚀 Version Simplifiée:")
    print(f"   Temps moyen: {avg_time_simple:.1f}ms")
    print(f"   Score: {score_simple}/100")
    print(f"   Domaine détecté: {result_simple['cv_domain']}")

    # Analyse de la charge mémoire (approximation)
    import sys
    memory_usage = sys.getsizeof(result_simple)
    print(f"   Mémoire résultat: {memory_usage} bytes")

    return {
        "avg_time_ms": avg_time_simple,
        "score": score_simple,
        "memory_bytes": memory_usage
    }


# ================================
# 15. FONCTION PRINCIPALE SIMPLIFIÉE
# ================================

def main_simplified():
    """Fonction principale pour tests simplifiés"""

    print("🎯 SERVICE DE MATCHING CV SIMPLIFIÉ")
    print("Adapté pour: Entreprise Tech + CV Multi-Domaines")
    print("Modèle: BGE-M3 (Multilingue)")
    print("=" * 60)

    # Vérification du modèle
    if not model_manager.is_ready():
        print("❌ Erreur: Modèle BGE-M3 non disponible")
        return

    print("✅ Modèle BGE-M3 prêt")

    # Exécution des tests
    run_simplified_tests()

    # Statistiques finales
    print(f"\n📊 STATISTIQUES SYSTÈME:")
    print(
        f"   Cache taille: {len(model_manager.encode.__wrapped__.cache_info().currsize if hasattr(model_manager.encode, '__wrapped__') else 'N/A')}")
    print(f"   Domaines supportés: Tech, Business, Sales, Other")
    print(f"   Bonus cross-domaine: Activé")
    print(f"   Détection buzzwords: Activé")


# ================================
# 16. INTERFACE CLI SIMPLIFIÉE
# ================================

def cli_simple():
    """Interface CLI simplifiée"""

    print("🎯 Interface Matching CV - Version Simplifiée")
    print("=" * 50)

    while True:
        print("\nOptions:")
        print("1. Test avec exemples")
        print("2. Benchmark de performance")
        print("3. Analyser un domaine CV")
        print("4. Quitter")

        choice = input("\nChoix (1-4): ").strip()

        if choice == "1":
            main_simplified()
        elif choice == "2":
            # Données d'exemple pour benchmark
            cv_example = {
                "titre_candidat": "Développeur Python",
                "profil_resume": "Développeur avec expérience en web development",
                "formations": ["Master"],
                "experience_years": 3,
                "competences_techniques": ["Python", "React"],
                "competences_informatiques": ["Git"],
                "langues": ["Français"],
                "certifications": [],
                "projets": ["Web app"],
                "soft_skills": ["teamwork"]
            }

            job_example = {
                "titre_poste": "Développeur Backend",
                "missions": "Développement API Python",
                "exigences": {
                    "formation_requise": "Bac+5",
                    "annees_experience": 2,
                    "competences_obligatoires": ["Python"],
                    "competences_souhaitees": ["Docker"],
                    "langues": ["Français"],
                    "certifications": [],
                    "outils": ["Git"],
                    "qualites_humaines": ["autonomie"]
                }
            }

            benchmark_simplified_vs_original(cv_example, job_example)

        elif choice == "3":
            text = input("Texte CV à analyser: ").strip()
            if text:
                mock_cv = {"titre_candidat": text, "competences_techniques": []}
                domain = detect_cv_domain(mock_cv)
                print(f"Domaine détecté: {domain.upper()}")

        elif choice == "4":
            print("👋 Au revoir!")
            break
        else:
            print("❌ Choix invalide")


# ================================
# 17. FONCTIONS D'EXPORT SIMPLIFIÉES
# ================================

def export_simple_report(results: List[Dict], job_title: str, filepath: str) -> bool:
    """Export simplifié en JSON"""
    try:
        report = {
            "job_title": job_title,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_candidates": len(results),
            "candidates": []
        }

        for result in results:
            candidate = {
                "cv_id": result["cv_id"],
                "rank": result["rank"],
                "score": result["score"],
                "domain": result["cv_domain"],
                "action": result["result"]["interpretation"]["action"],
                "recommendations": len(result["result"].get("recommendations", []))
            }
            report["candidates"].append(candidate)

        import json
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"✅ Rapport exporté: {filepath}")
        return True

    except Exception as e:
        print(f"❌ Erreur export: {e}")
        return False


# ================================
# 18. UTILITAIRES RAPIDES
# ================================

def filter_candidates_by_score(results: List[Dict], min_score: int = 50) -> List[Dict]:
    """Filtre les candidats par score minimum"""
    return [r for r in results if r["score"] >= min_score]


def get_top_candidates_by_domain(results: List[Dict], top_per_domain: int = 2) -> List[Dict]:
    """Récupère le top N par domaine"""
    by_domain = {}

    for result in results:
        domain = result["cv_domain"]
        if domain not in by_domain:
            by_domain[domain] = []
        by_domain[domain].append(result)

    # Tri par score dans chaque domaine
    for domain in by_domain:
        by_domain[domain].sort(key=lambda x: x["score"], reverse=True)
        by_domain[domain] = by_domain[domain][:top_per_domain]

    # Combine et re-trie
    combined = []
    for domain_results in by_domain.values():
        combined.extend(domain_results)

    combined.sort(key=lambda x: x["score"], reverse=True)

    # Mise à jour des rangs
    for i, result in enumerate(combined):
        result["rank"] = i + 1

    return combined


# ================================
# 19. VALIDATION ET MÉTRIQUES
# ================================

def validate_configuration():
    """Valide la configuration du système"""
    checks = []

    # Vérification modèle
    try:
        model_manager.is_ready()
        checks.append(("Modèle BGE-M3", "✅"))
    except:
        checks.append(("Modèle BGE-M3", "❌"))

    # Vérification configuration
    try:
        weights = AdaptiveConfig.get_weights("tech")
        total_weight = sum(weights.values())
        checks.append((f"Poids total tech: {total_weight}", "✅" if total_weight == 100 else "⚠️"))
    except:
        checks.append(("Configuration poids", "❌"))

    # Vérification normalisation
    try:
        test_skill = skill_normalizer.normalize("python")
        checks.append(("Normalisation", "✅" if test_skill else "❌"))
    except:
        checks.append(("Normalisation", "❌"))

    print("\n🔍 VALIDATION SYSTÈME:")
    print("-" * 30)
    for check, status in checks:
        print(f"{status} {check}")

    return all(status == "✅" for _, status in checks)


# ================================
# 20. POINT D'ENTRÉE
# ================================

if __name__ == "__main__":
    print("🚀 Démarrage du service de matching simplifié...")

    # Validation
    if validate_configuration():
        print("✅ Système validé - Prêt pour utilisation")

        try:
            # Tests automatiques
            main_simplified()

            # Interface optionnelle
            print("\n" + "=" * 60)
            print("Tests terminés avec succès!")
            print("Pour interface interactive, appelez cli_simple()")

        except KeyboardInterrupt:
            print("\n⏹️ Arrêt demandé par l'utilisateur")
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            logger.error(f"Erreur principale: {e}")
    else:
        print("❌ Échec de validation - Vérifiez la configuration")

# ================================
# EXEMPLES D'UTILISATION RAPIDE
# ================================

"""
# Utilisation simple :

# 1. Matching rapide
score, domain, action = quick_match(cv_data, job_data)
print(f"Score: {score}, Domaine: {domain}, Action: {action}")

# 2. Matching complet
result = calculate_adaptive_match_score(cv_data, job_data)
display_simple_results(result)

# 3. Traitement par lot
results = rank_candidates_for_tech_company(cv_list, job_data)
display_batch_summary(results)

# 4. Filtrage
qualified = filter_candidates_by_score(results, min_score=60)
top_by_domain = get_top_candidates_by_domain(results, top_per_domain=3)

# 5. Export
export_simple_report(results, "Développeur Python", "rapport.json")
"""