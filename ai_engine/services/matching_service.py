# matching_service_enhanced_optimized.py
# Service de matching CV ↔ Offre d'emploi optimisé avec re-ranking et analyse avancée
# Nouvelles optimisations : Cross-encoder, matching par phrase, multilingue, détection buzzwords

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder
from typing import Dict, List, Tuple, Any, Optional, Union, Set
import json
import logging
import hashlib
from functools import lru_cache
from datetime import datetime
import time
from pathlib import Path
import pickle
import re
from collections import defaultdict
import os
import nltk
from nltk.tokenize import sent_tokenize
import warnings
warnings.filterwarnings('ignore')

# Téléchargement des ressources NLTK (une seule fois)
# Téléchargement des ressources NLTK (une seule fois)
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt_tab')
# ==================== AJOUT POUR INTÉGRATION ====================
# Import du cv_parser pour l'intégration
try:
    from cv_parser import CVParser, ParsingResult
except ImportError:
    print("⚠️ CVParser non trouvé. Fonctionnalités de parsing PDF indisponibles.")
    CVParser = None
    ParsingResult = None

# Téléchargement des ressources NLTK (une seule fois)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

# ================================
# 1. DICTIONNAIRES DE NORMALISATION + BUZZWORDS
# ================================

class SkillNormalizer:
    """Normalisation avancée des compétences et certifications avec détection de buzzwords"""
    
    SKILL_MAPPINGS = {
        # Langages de programmation
        "python": ["python", "python3", "py", "django", "flask"],
        "javascript": ["javascript", "js", "node.js", "nodejs", "typescript", "ts"],
        "java": ["java", "java 8", "java 11", "java 17", "spring", "spring boot"],
        "csharp": ["c#", "csharp", "c sharp", ".net", "dotnet", "asp.net"],
        "php": ["php", "php7", "php8", "laravel", "symfony"],
        "go": ["go", "golang"],
        "rust": ["rust", "rustlang"],
        "scala": ["scala", "akka"],
        "kotlin": ["kotlin", "android"],
        
        # Frameworks web
        "react": ["react", "reactjs", "React.js", "nextjs", "next.js"],
        "vue": ["vue", "vuejs", "vue.js", "nuxt", "nuxtjs"],
        "angular": ["angular", "angularjs", "angular2", "angular4"],
        "svelte": ["svelte", "sveltekit"],
        
        # Bases de données
        "postgresql": ["postgresql", "postgres", "psql", "pg"],
        "mysql": ["mysql", "mariadb"],
        "mongodb": ["mongodb", "mongo", "nosql"],
        "redis": ["redis", "cache"],
        "elasticsearch": ["elasticsearch", "elastic", "elk"],
        
        # Cloud & DevOps
        "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
        "azure": ["azure", "microsoft azure"],
        "gcp": ["gcp", "google cloud", "google cloud platform"],
        "docker": ["docker", "containers", "containerization"],
        "kubernetes": ["kubernetes", "k8s", "orchestration"],
        "terraform": ["terraform", "iac", "infrastructure as code"],
        
        # Outils
        "git": ["git", "Github", "gitlab", "version control"],
        "jenkins": ["jenkins", "ci/cd", "continuous integration"],
        "linux": ["linux", "ubuntu", "centos", "unix"],
        "windows": ["windows", "windows server"],
        
        # Méthodologies
        "agile": ["agile", "scrum", "kanban", "sprint"],
        "devops": ["devops", "sre", "site reliability"],
        
        # IA/ML
        "machine_learning": ["machine learning", "ml", "tensorflow", "pytorch", "scikit-learn"],
        "data_science": ["data science", "data analysis", "pandas", "numpy"],
    }
    
    CERTIFICATION_MAPPINGS = {
        "aws_certified": [
            "aws certified", "aws certification", "aws developer", 
            "aws solutions architect", "aws sysops", "aws devops"
        ],
        "azure_certified": [
            "azure certified", "azure certification", "azure developer",
            "azure solutions architect", "azure administrator"
        ],
        "gcp_certified": [
            "gcp certified", "google cloud certified", "google certified",
            "cloud engineer", "cloud architect"
        ],
        "scrum_master": [
            "scrum master", "certified scrum master", "csm", "psm",
            "professional scrum master"
        ],
        "pmp": ["pmp", "project management professional", "pmbok"],
        "cissp": ["cissp", "certified information systems security professional"],
        "cisa": ["cisa", "certified information systems auditor"],
        "itil": ["itil", "it infrastructure library", "itil foundation"],
    }
    
    SOFT_SKILL_SYNONYMS = {
        "leadership": [
            "leadership", "encadrement", "management", "gestion d'équipe",
            "direction", "pilotage", "coordination", "animation d'équipe"
        ],
        "communication": [
            "communication", "relationnel", "expression", "présentation",
            "écoute", "négociation", "diplomatie", "pédagogie"
        ],
        "teamwork": [
            "travail en équipe", "collaboration", "coopération", "esprit d'équipe",
            "synergie", "collective", "partenariat", "entraide"
        ],
        "problem_solving": [
            "résolution de problèmes", "analyse", "diagnostic", "troubleshooting",
            "investigation", "débogage", "solution", "créativité"
        ],
        "adaptability": [
            "adaptabilité", "flexibilité", "polyvalence", "agilité",
            "ouverture", "apprentissage", "évolution", "changement"
        ],
        "autonomy": [
            "autonomie", "indépendance", "initiative", "prise de décision",
            "proactivité", "self-management", "débrouillardise"
        ]
    }
    
    # 🆕 NOUVEAU : Détection de buzzwords
    BUZZWORDS_FR = {
        "high_bullshit": [
            "disruptif", "disruptive", "game-changer", "révolutionnaire",
            "innovant à 360°", "leader d'opinion", "thought leader",
            "synergies transversales", "paradigme", "écosystème digital",
            "transformation digitale", "intelligence artificielle cognitive",
            "blockchain révolutionnaire", "deep learning avancé"
        ],
        "medium_bullshit": [
            "innovation", "synergie", "optimisation", "excellence",
            "performance", "efficacité", "qualité", "dynamique",
            "proactif", "créatif", "motivé",
            "orienté résultats", "force de proposition"
        ],
        "marketing_speak": [
            "roi", "kpi", "benchmark", "best practices",
            "win-win", "value-added", "cutting-edge", "state-of-the-art",
            "scalable", "agile mindset", "customer-centric"
        ]
    }
    
    BUZZWORDS_EN = {
        "high_bullshit": [
            "disruptive", "game-changer", "revolutionary", "paradigm shift",
            "thought leader", "synergistic", "holistic approach",
            "bleeding-edge", "next-generation", "world-class",
            "industry-leading", "transformational"
        ],
        "medium_bullshit": [
            "innovative", "dynamic", "proactive", "results-driven",
            "passionate", "motivated", "excellence", "optimization",
            "performance", "efficiency", "quality", "creative"
        ],
        "marketing_speak": [
            "leverage", "utilize", "synergy", "paradigm",
            "actionable insights", "value proposition", "competitive advantage",
            "customer-centric", "scalable solution"
        ]
    }
    
    def __init__(self):
        self.skill_reverse_map = self._build_reverse_map(self.SKILL_MAPPINGS)
        self.cert_reverse_map = self._build_reverse_map(self.CERTIFICATION_MAPPINGS)
        self.soft_reverse_map = self._build_reverse_map(self.SOFT_SKILL_SYNONYMS)
        
        # Compilation des buzzwords
        self.all_buzzwords = set()
        for category in [self.BUZZWORDS_FR, self.BUZZWORDS_EN]:
            for level, words in category.items():
                self.all_buzzwords.update([w.lower() for w in words])
    
    def _build_reverse_map(self, mappings: Dict[str, List[str]]) -> Dict[str, str]:
        """Construit un mapping inverse pour la recherche rapide"""
        reverse_map = {}
        for standard_term, variants in mappings.items():
            for variant in variants:
                reverse_map[variant.lower().strip()] = standard_term
        return reverse_map
    
    def normalize_skill(self, skill: str) -> str:
        """Normalise une compétence technique"""
        if not skill:
            return ""
        
        clean_skill = skill.lower().strip()
        return self.skill_reverse_map.get(clean_skill, clean_skill)
    
    def normalize_certification(self, cert: str) -> str:
        """Normalise une certification"""
        if not cert:
            return ""
        
        clean_cert = cert.lower().strip()
        # Recherche par sous-chaîne pour les certifications
        for standard, variants in self.CERTIFICATION_MAPPINGS.items():
            for variant in variants:
                if variant in clean_cert or clean_cert in variant:
                    return standard
        return clean_cert
    
    def enhance_soft_skills(self, skills: List[str]) -> Set[str]:
        """Enrichit la liste des soft skills avec les synonymes"""
        enhanced = set()
        
        for skill in skills:
            if not skill:
                continue
                
            clean_skill = skill.lower().strip()
            enhanced.add(clean_skill)
            
            # Recherche de synonymes
            for standard, synonyms in self.SOFT_SKILL_SYNONYMS.items():
                for synonym in synonyms:
                    if clean_skill in synonym or synonym in clean_skill:
                        enhanced.update(synonyms)
                        break
        
        return enhanced
    
    def get_must_have_skills(self, job_skills: List[str]) -> Set[str]:
        """Identifie les compétences critiques (must-have)"""
        must_have = set()
        critical_keywords = [
            "obligatoire", "requis", "indispensable", "essentiel",
            "mandatory", "required", "must", "critical"
        ]
        
        for skill in job_skills:
            if not skill:
                continue
                
            skill_str = str(skill).lower()
            has_critical_keyword = any(keyword in skill_str for keyword in critical_keywords)
            
            if has_critical_keyword:
                # Nettoie la compétence des mots-clés et parenthèses
                clean_skill = skill_str
                for keyword in critical_keywords:
                    clean_skill = clean_skill.replace(keyword, "").strip()
                
                # Supprime les parenthèses et leur contenu
                clean_skill = re.sub(r'\([^)]*\)', '', clean_skill).strip()
                
                # Supprime les caractères spéciaux restants
                clean_skill = re.sub(r'[^\w\s-]', '', clean_skill).strip()
                
                # Supprime les espaces multiples
                clean_skill = re.sub(r'\s+', ' ', clean_skill).strip()
                
                if clean_skill:  # Ajoute seulement si non vide
                    normalized_skill = self.normalize_skill(clean_skill)
                    if normalized_skill:  # Double vérification
                        must_have.add(normalized_skill)
        
        return must_have
    
    # 🆕 NOUVEAU : Analyse des buzzwords
    def analyze_buzzwords(self, text: str) -> Dict:
        """Analyse la densité de buzzwords dans un texte"""
        if not text:
            return {"score": 0, "density": 0, "detected": [], "confidence_penalty": 0}
        
        text_lower = text.lower()
        words = re.findall(r'\b\w+\b', text_lower)
        total_words = len(words)
        
        if total_words == 0:
            return {"score": 0, "density": 0, "detected": [], "confidence_penalty": 0}
        
        detected_buzzwords = []
        buzzword_score = 0
        
        # Détection des buzzwords
        for buzzword in self.all_buzzwords:
            if buzzword in text_lower:
                detected_buzzwords.append(buzzword)
                
                # Score selon le niveau de "bullshit"
                if any(buzzword in category for category in self.BUZZWORDS_FR["high_bullshit"] + self.BUZZWORDS_EN["high_bullshit"]):
                    buzzword_score += 3
                elif any(buzzword in category for category in self.BUZZWORDS_FR["medium_bullshit"] + self.BUZZWORDS_EN["medium_bullshit"]):
                    buzzword_score += 1.5
                else:
                    buzzword_score += 1
        
        density = len(detected_buzzwords) / total_words
        
        # Calcul de la pénalité de confiance
        confidence_penalty = 0
        if density > 0.15:  # Plus de 15% de buzzwords
            confidence_penalty = 0.3
        elif density > 0.10:  # Plus de 10%
            confidence_penalty = 0.2
        elif density > 0.05:  # Plus de 5%
            confidence_penalty = 0.1
        
        return {
            "score": buzzword_score,
            "density": round(density * 100, 2),
            "detected": detected_buzzwords[:10],  # Top 10
            "confidence_penalty": confidence_penalty
        }

# Instance globale du normalisateur
skill_normalizer = SkillNormalizer()

# ================================
# 2. SYSTÈME DE LOGGING (inchangé)
# ================================

class MatchingLogger:
    """Système de logging centralisé pour le matching"""
    
    def __init__(self, log_level: str = "INFO"):
        self.setup_logging(log_level)
        self.metrics = {
            "scores": [],
            "execution_times": [],
            "error_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "must_have_failures": 0,
            "over_qualified_count": 0,
            "cross_encoder_uses": 0,  # 🆕 Nouveau métrique
            "sentence_matches": 0      # 🆕 Nouveau métrique
        }
    
    def setup_logging(self, log_level: str):
        """Configure le système de logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configuration avec encodage UTF-8 explicite
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'matching.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('ATS_Matching_Enhanced_Optimized')
    
    def log_matching_event(self, cv_id: str, job_id: str, score: int, 
                          execution_time: float, details: Dict, error: str = None,
                          must_have_failed: bool = False, over_qualified: bool = False):
        """Log complet d'un événement de matching"""
        if error:
            self.logger.error(f"Matching failed for {cv_id} vs {job_id}: {error}")
            self.metrics["error_count"] += 1
        else:
            self.logger.info(f"Matching success: {cv_id} vs {job_id} = {score}/100")
            self.update_metrics(score, execution_time, must_have_failed, over_qualified)
    
    def update_metrics(self, score: int, execution_time: float, 
                      must_have_failed: bool = False, over_qualified: bool = False):
        """Met à jour les métriques de performance"""
        self.metrics["scores"].append(score)
        self.metrics["execution_times"].append(execution_time)
        
        if must_have_failed:
            self.metrics["must_have_failures"] += 1
        if over_qualified:
            self.metrics["over_qualified_count"] += 1
        
        # Garde seulement les 1000 dernières mesures
        for key in ["scores", "execution_times"]:
            if len(self.metrics[key]) > 1000:
                self.metrics[key] = self.metrics[key][-1000:]
    
    def get_performance_stats(self) -> Dict:
        """Statistiques de performance en temps réel"""
        if not self.metrics["scores"]:
            return {"message": "Pas de données disponibles"}
        
        scores = self.metrics["scores"]
        times = self.metrics["execution_times"]
        total_processed = len(scores) + self.metrics["error_count"]
        
        return {
            "score_stats": {
                "average": round(sum(scores) / len(scores), 2),
                "median": sorted(scores)[len(scores)//2],
                "min": min(scores),
                "max": max(scores),
                "total_processed": len(scores)
            },
            "performance_stats": {
                "avg_execution_time_ms": round((sum(times) / len(times)) * 1000, 2),
                "max_execution_time_ms": round(max(times) * 1000, 2),
                "min_execution_time_ms": round(min(times) * 1000, 2)
            },
            "cache_stats": {
                "hits": self.metrics["cache_hits"],
                "misses": self.metrics["cache_misses"],
                "hit_rate": round(self.metrics["cache_hits"] / 
                                (self.metrics["cache_hits"] + self.metrics["cache_misses"]) * 100, 2)
                if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0 else 0
            },
            "quality_stats": {
                "must_have_failures": self.metrics["must_have_failures"],
                "over_qualified_count": self.metrics["over_qualified_count"],
                "must_have_failure_rate": round(self.metrics["must_have_failures"] / total_processed * 100, 2)
                if total_processed > 0 else 0,
                "over_qualification_rate": round(self.metrics["over_qualified_count"] / total_processed * 100, 2)
                if total_processed > 0 else 0
            },
            "error_stats": {
                "total_errors": self.metrics["error_count"],
                "error_rate": round(self.metrics["error_count"] / total_processed * 100, 2)
                if total_processed > 0 else 0
            },
            # 🆕 Nouvelles métriques
            "optimization_stats": {
                "cross_encoder_uses": self.metrics["cross_encoder_uses"],
                "sentence_matches": self.metrics["sentence_matches"]
            }
        }

# Instance globale du logger
logger_instance = MatchingLogger()

# ================================
# 3. CACHE SIMPLIFIÉ (inchangé)
# ================================

class SimpleEmbeddingCache:
    """Cache simple en mémoire pour les embeddings"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
    
    def _get_key(self, text: str) -> str:
        """Génère une clé de cache basée sur le hash du texte"""
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """Récupère un embedding du cache"""
        if not text or not text.strip():
            return None
            
        key = self._get_key(text.strip())
        
        if key in self.cache:
            logger_instance.metrics["cache_hits"] += 1
            return self.cache[key]
        
        logger_instance.metrics["cache_misses"] += 1
        return None
    
    def set(self, text: str, embedding: np.ndarray):
        """Stocke un embedding dans le cache"""
        if not text or not text.strip():
            return
            
        key = self._get_key(text.strip())
        
        # Nettoyage du cache si nécessaire
        if len(self.cache) >= self.max_size:
            # Supprime le premier élément (FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = embedding
    
    def get_stats(self) -> Dict:
        """Statistiques du cache"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": round(logger_instance.metrics["cache_hits"] / 
                            (logger_instance.metrics["cache_hits"] + 
                             logger_instance.metrics["cache_misses"]) * 100, 2)
            if (logger_instance.metrics["cache_hits"] + logger_instance.metrics["cache_misses"]) > 0 else 0
        }

# Instance globale du cache
embedding_cache = SimpleEmbeddingCache()

# ================================
# 4. CONFIGURATION SIMPLIFIÉE (inchangé)
# ================================

class MatchingConfig:
    """Configuration simplifiée du matching"""
    
    DEFAULT_WEIGHTS = {
        "titre_poste": 10,
        "profil_resume": 10,
        "formation": 15,
        "experience_annees": 15,
        "competences_techniques": 20,
        "competences_informatiques": 5,
        "langues": 10,
        "certifications": 5,
        "projets": 5,
        "soft_skills": 5,
    }
    
    JOB_TYPE_ADJUSTMENTS = {
        "tech": {
            "competences_techniques": 25,
            "formation": 12,
            "projets": 8
        },
        "sales": {
            "soft_skills": 20,
            "experience_annees": 20,
            "langues": 15
        },
        "management": {
            "soft_skills": 18,
            "experience_annees": 25,
            "formation": 12
        }
    }
    
    def __init__(self, job_type: str = "default"):
        self.job_type = job_type.lower()
        self.weights = self._get_weights()
    
    def _get_weights(self) -> Dict:
        """Calcule les poids selon le type de poste"""
        weights = self.DEFAULT_WEIGHTS.copy()
        
        if self.job_type in self.JOB_TYPE_ADJUSTMENTS:
            adjustments = self.JOB_TYPE_ADJUSTMENTS[self.job_type]
            for field, weight in adjustments.items():
                weights[field] = weight
        
        return weights

# ================================
# 5. FONCTIONS UTILITAIRES ROBUSTES (inchangé)
# ================================

def safe_get_string(data: Dict, key: str, default: str = "") -> str:
    """Récupération sécurisée d'une chaîne"""
    try:
        value = data.get(key, default)
        if isinstance(value, str):
            return value.strip()
        elif isinstance(value, (list, dict)):
            return str(value)
        else:
            return str(value) if value is not None else default
    except Exception:
        return default

def safe_get_list(data: Dict, key: str, default: List = None) -> List:
    """Récupération sécurisée d'une liste"""
    if default is None:
        default = []
    
    try:
        value = data.get(key, default)
        if isinstance(value, list):
            return [str(item) for item in value if item is not None]
        elif isinstance(value, str):
            return [value] if value.strip() else default
        elif value is not None:
            return [str(value)]
        else:
            return default
    except Exception:
        return default

def safe_get_int(data: Dict, key: str, default: int = 0) -> int:
    """Récupération sécurisée d'un entier"""
    try:
        value = data.get(key, default)
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str):
            # Extraction des nombres de la chaîne
            numbers = re.findall(r'\d+', value)
            return int(numbers[0]) if numbers else default
        else:
            return default
    except Exception:
        return default

def safe_get_dict(data: Dict, key: str, default: Dict = None) -> Dict:
    """Récupération sécurisée d'un dictionnaire"""
    if default is None:
        default = {}
    
    try:
        value = data.get(key, default)
        return value if isinstance(value, dict) else default
    except Exception:
        return default

# ================================
# 6. GESTIONNAIRE DE MODÈLE OPTIMISÉ
# ================================

class OptimizedModelManager:
    """Gestionnaire optimisé avec bi-encoder + cross-encoder"""
    
    def __init__(self, 
                 bi_encoder_name: str = 'BAAI/bge-m3',
                 cross_encoder_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2'):
        self.bi_encoder_name = bi_encoder_name
        self.cross_encoder_name = cross_encoder_name
        self.bi_encoder = None
        self.cross_encoder = None
        self._load_models()
    
    def _load_models(self):
        """Charge les modèles avec gestion d'erreurs"""
        try:
            logger_instance.logger.info(f"Chargement du bi-encoder {self.bi_encoder_name}...")
            self.bi_encoder = SentenceTransformer(self.bi_encoder_name)
            logger_instance.logger.info("Bi-encoder chargé avec succès")
            
            logger_instance.logger.info(f"Chargement du cross-encoder {self.cross_encoder_name}...")
            self.cross_encoder = CrossEncoder(self.cross_encoder_name)
            logger_instance.logger.info("Cross-encoder chargé avec succès")
            
        except Exception as e:
            logger_instance.logger.error(f"Erreur lors du chargement des modèles: {str(e)}")
            raise RuntimeError(f"Impossible de charger les modèles: {str(e)}")
    
    def encode(self, text: str) -> Optional[np.ndarray]:
        """Encode un texte avec le bi-encoder"""
        if not self.bi_encoder:
            raise RuntimeError("Bi-encoder non chargé")
        
        if not text or not text.strip():
            return None
        
        try:
            return self.bi_encoder.encode(text.strip(), normalize_embeddings=True)
        except Exception as e:
            logger_instance.logger.error(f"Erreur lors de l'encodage: {str(e)}")
            return None
    
    def cross_encode(self, text_pairs: List[Tuple[str, str]]) -> List[float]:
        """Re-ranking avec cross-encoder pour précision fine"""
        if not self.cross_encoder:
            logger_instance.logger.warning("Cross-encoder non disponible, utilisation des scores bi-encoder")
            return [0.5] * len(text_pairs)
        
        if not text_pairs:
            return []
        
        try:
            logger_instance.metrics["cross_encoder_uses"] += 1
            scores = self.cross_encoder.predict(text_pairs)
            return scores.tolist() if hasattr(scores, 'tolist') else scores
        except Exception as e:
            logger_instance.logger.error(f"Erreur cross-encoder: {str(e)}")
            return [0.5] * len(text_pairs)
    
    # 🆕 NOUVEAU : Matching par phrase
    def sentence_level_matching(self, cv_text: str, job_text: str, top_k: int = 5) -> Dict:
        """Matching au niveau des phrases pour une précision maximale"""
        try:
            # Découpage en phrases
            cv_sentences = sent_tokenize(cv_text, language='french')
            job_sentences = sent_tokenize(job_text, language='french')
            
            if not cv_sentences or not job_sentences:
                return {"score": 0.0, "matches": [], "coverage": 0.0}
            
            # Encodage des phrases
            cv_embeddings = []
            job_embeddings = []
            
            for sentence in cv_sentences:
                if len(sentence.strip()) > 10:  # Filtre les phrases trop courtes
                    emb = self.encode(sentence)
                    if emb is not None:
                        cv_embeddings.append((sentence, emb))
            
            for sentence in job_sentences:
                if len(sentence.strip()) > 10:
                    emb = self.encode(sentence)
                    if emb is not None:
                        job_embeddings.append((sentence, emb))
            
            if not cv_embeddings or not job_embeddings:
                return {"score": 0.0, "matches": [], "coverage": 0.0}
            
            # Calcul des similarités phrase par phrase
            best_matches = []
            
            for job_sentence, job_emb in job_embeddings:
                best_score = 0.0
                best_cv_sentence = ""
                
                for cv_sentence, cv_emb in cv_embeddings:
                    similarity = cosine_similarity_safe(cv_emb, job_emb)
                    if similarity > best_score:
                        best_score = similarity
                        best_cv_sentence = cv_sentence
                
                if best_score > 0.3:  # Seuil de pertinence
                    best_matches.append({
                        "job_sentence": job_sentence[:100] + "..." if len(job_sentence) > 100 else job_sentence,
                        "cv_sentence": best_cv_sentence[:100] + "..." if len(best_cv_sentence) > 100 else best_cv_sentence,
                        "similarity": best_score
                    })
            
            # Tri par score décroissant et limitation au top-k
            best_matches.sort(key=lambda x: x["similarity"], reverse=True)
            top_matches = best_matches[:top_k]
            
            # Score global basé sur les meilleures correspondances
            if top_matches:
                avg_score = sum(match["similarity"] for match in top_matches) / len(top_matches)
                coverage = len(top_matches) / len(job_embeddings)
            else:
                avg_score = 0.0
                coverage = 0.0
            
            logger_instance.metrics["sentence_matches"] += len(top_matches)
            
            return {
                "score": avg_score,
                "matches": top_matches,
                "coverage": coverage,
                "cv_sentences_analyzed": len(cv_embeddings),
                "job_sentences_analyzed": len(job_embeddings)
            }
            
        except Exception as e:
            logger_instance.logger.error(f"Erreur sentence-level matching: {str(e)}")
            return {"score": 0.0, "matches": [], "coverage": 0.0}
    
    def is_ready(self) -> bool:
        """Vérifie si les modèles sont prêts"""
        return self.bi_encoder is not None

# Instance globale du gestionnaire de modèle optimisé
model_manager = OptimizedModelManager()

# ================================
# 7. FONCTIONS D'EMBEDDING ET SIMILARITÉ (mise à jour)
# ================================

def embed_with_cache(text: str) -> Optional[np.ndarray]:
    """Encode un texte avec cache intelligent"""
    if not text or not text.strip():
        return None
    
    # Vérification du cache
    cached_embedding = embedding_cache.get(text)
    if cached_embedding is not None:
        return cached_embedding
    
    # Génération de l'embedding
    embedding = model_manager.encode(text)
    if embedding is not None:
        embedding_cache.set(text, embedding)
    
    return embedding

def cosine_similarity_safe(vec1: Optional[np.ndarray], vec2: Optional[np.ndarray]) -> float:
    """Similarité cosinus sécurisée"""
    if vec1 is None or vec2 is None:
        return 0.0
    
    try:
        if len(vec1) == 0 or len(vec2) == 0:
            return 0.0
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    except Exception as e:
        logger_instance.logger.error(f"Erreur similarité cosinus: {str(e)}")
        return 0.0

def jaccard_similarity_safe(list1: List[str], list2: List[str]) -> float:
    """Similarité Jaccard sécurisée avec normalisation"""
    try:
        # Conversion en sets avec normalisation
        set1 = {skill_normalizer.normalize_skill(str(item).lower()) for item in list1 if item}
        set2 = {skill_normalizer.normalize_skill(str(item).lower()) for item in list2 if item}
        
        if not set1 and not set2:
            return 1.0
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    except Exception as e:
        logger_instance.logger.error(f"Erreur Jaccard: {str(e)}")
        return 0.0

def check_must_have_requirements(cv_skills: List[str], job_requirements: List[str]) -> Tuple[bool, List[str]]:
    """Vérifie si toutes les compétences obligatoires sont présentes"""
    try:
        must_have_skills = skill_normalizer.get_must_have_skills(job_requirements)
        
        if not must_have_skills:
            return True, []
        
        # Normalisation des compétences CV
        normalized_cv_skills = set()
        for skill in cv_skills:
            if skill:
                normalized_cv_skills.add(skill_normalizer.normalize_skill(str(skill).lower().strip()))
        
        # Vérification des compétences manquantes
        missing_skills = must_have_skills - normalized_cv_skills
        
        return len(missing_skills) == 0, list(missing_skills)
    except Exception as e:
        logger_instance.logger.error(f"Erreur vérification must-have: {str(e)}")
        return True, []  # En cas d'erreur, on ne bloque pas

def calculate_education_score(cv_formations: List, job_formation_req: str) -> float:
    """Calcule le score de formation de manière sécurisée"""
    try:
        # Mapping des niveaux de formation
        niveau_mapping = {
            "bac+2": 2, "bac+3": 3, "bac+4": 4, "bac+5": 5, 
            "master": 5, "doctorat": 8, "phd": 8,
            "ingénieur": 5, "ingenieur": 5, "licence": 3, "dut": 2, "bts": 2
        }
        
        # Niveau requis
        job_formation_lower = str(job_formation_req).lower()
        required_level = 0
        for key, val in niveau_mapping.items():
            if key in job_formation_lower:
                required_level = max(required_level, val)
        
        # Niveau candidat
        candidate_level = 0
        for formation in cv_formations:
            if isinstance(formation, dict):
                diplome = safe_get_string(formation, "diplome").lower()
            else:
                diplome = str(formation).lower()
            
            for key, val in niveau_mapping.items():
                if key in diplome:
                    candidate_level = max(candidate_level, val)
        
        # Calcul du score
        if required_level == 0:
            return 1.0  # Pas d'exigence spécifique
        
        if candidate_level >= required_level:
            return 1.0
        elif candidate_level >= required_level - 1:
            return 0.8
        else:
            return max(0.0, candidate_level / required_level)
    
    except Exception as e:
        logger_instance.logger.error(f"Erreur calcul formation: {str(e)}")
        return 0.5  # Score neutre en cas d'erreur

def calculate_language_score(cv_langues: List, job_langues: List) -> float:
    """Calcule le score des langues de manière sécurisée"""
    try:
        if not job_langues:
            return 1.0
        
        cecr_mapping = {
            "a1": 1, "a2": 2, "b1": 3, 
            "b2": 4, "c1": 5, "c2": 6
        }
        
        matched_languages = 0
        total_required = len(job_langues)
        
        for lang_req in job_langues:
            lang_req_str = str(lang_req)
            if ":" in lang_req_str:
                lang_name, required_level = lang_req_str.split(":", 1)
            else:
                lang_name, required_level = lang_req_str, "A1"
            
            lang_name = lang_name.strip().lower()
            req_level_score = cecr_mapping.get(required_level.strip().lower(), 1)
            
            # Recherche dans les langues du CV
            for cv_lang in cv_langues:
                if isinstance(cv_lang, dict):
                    cv_lang_name = safe_get_string(cv_lang, "langue").lower()
                    cv_level = safe_get_string(cv_lang, "niveau").lower()
                    cv_level_score = cecr_mapping.get(cv_level, 1)
                    
                    if cv_lang_name == lang_name and cv_level_score >= req_level_score:
                        matched_languages += 1
                        break
                else:
                    cv_lang_str = str(cv_lang).lower()
                    if lang_name in cv_lang_str:
                        matched_languages += 1
                        break
        
        return matched_languages / total_required if total_required > 0 else 1.0
    
    except Exception as e:
        logger_instance.logger.error(f"Erreur calcul langues: {str(e)}")
        return 0.5  # Score neutre en cas d'erreur

# 🆕 NOUVELLE FONCTION : Re-ranking avec cross-encoder
def rerank_candidates_with_cross_encoder(candidates: List[Dict], job_text: str, top_k: int = 5) -> List[Dict]:
    """Re-ranking précis des top candidats avec cross-encoder"""
    if len(candidates) <= 1 or not model_manager.cross_encoder:
        return candidates
    
    try:
        # Préparation des paires pour le cross-encoder
        text_pairs = []
        candidate_data = []
        
        for candidate in candidates[:top_k * 2]:  # Prend plus de candidats pour le re-ranking
            cv_text = candidate.get("cv_text", "")
            if cv_text:
                text_pairs.append((cv_text, job_text))
                candidate_data.append(candidate)
        
        if not text_pairs:
            return candidates
        
        # Scores du cross-encoder
        cross_scores = model_manager.cross_encode(text_pairs)
        
        # Combinaison des scores (70% cross-encoder, 30% score original)
        for i, candidate in enumerate(candidate_data):
            if i < len(cross_scores):
                original_score = candidate.get("score", 0)
                cross_score = cross_scores[i] * 100  # Normalisation à 0-100
                
                # Score hybride
                hybrid_score = 0.7 * cross_score + 0.3 * original_score
                candidate["reranked_score"] = round(hybrid_score, 2)
                candidate["cross_encoder_score"] = round(cross_score, 2)
                candidate["used_reranking"] = True
        
        # Tri par score hybride
        candidate_data.sort(key=lambda x: x.get("reranked_score", x.get("score", 0)), reverse=True)
        
        # Ajout des candidats non re-rankés
        remaining_candidates = candidates[len(candidate_data):]
        for candidate in remaining_candidates:
            candidate["used_reranking"] = False
        
        return candidate_data + remaining_candidates
        
    except Exception as e:
        logger_instance.logger.error(f"Erreur re-ranking: {str(e)}")
        return candidates

# ================================
# 8. FONCTION PRINCIPALE OPTIMISÉE
# ================================

def calculate_match_score_enhanced(
    cv_json: Dict, 
    job_json: Dict, 
    cv_id: str = "unknown", 
    job_id: str = "unknown",
    config: Optional[MatchingConfig] = None,
    use_sentence_matching: bool = True,  # 🆕 Nouveau paramètre
    analyze_buzzwords: bool = True        # 🆕 Nouveau paramètre
) -> Dict:
    """
    Version optimisée du calcul de matching CV-Offre avec nouvelles fonctionnalités
    """
    start_time = time.time()
    error_msg = None
    must_have_failed = False
    
    try:
        # Validation des entrées
        if not isinstance(cv_json, dict) or not isinstance(job_json, dict):
            raise ValueError("Les données CV et offre doivent être des dictionnaires")
        
        if not model_manager.is_ready():
            raise RuntimeError("Le modèle d'embeddings n'est pas prêt")
        
        # Configuration automatique si non fournie
        if config is None:
            job_title = safe_get_string(job_json, "titre_poste").lower()
            if any(word in job_title for word in ["développeur", "dev", "tech", "ingénieur"]):
                job_type = "tech"
            elif any(word in job_title for word in ["commercial", "vente", "sales"]):
                job_type = "sales"
            elif any(word in job_title for word in ["manager", "chef", "directeur", "responsable"]):
                job_type = "management"
            else:
                job_type = "default"
            
            config = MatchingConfig(job_type)
        
        # Extraction sécurisée des données
        cv_data = {
            "titre_candidat": safe_get_string(cv_json, "titre_candidat"),
            "profil_resume": safe_get_string(cv_json, "profil_resume"),
            "formations": safe_get_list(cv_json, "formations"),
            "experience_years": safe_get_int(cv_json, "experience_years"),
            "competences_techniques": safe_get_list(cv_json, "competences_techniques"),
            "competences_informatiques": safe_get_list(cv_json, "competences_informatiques"),
            "langues": safe_get_list(cv_json, "langues"),
            "certifications": safe_get_list(cv_json, "certifications"),
            "projets": safe_get_list(cv_json, "projets"),
            "soft_skills": safe_get_list(cv_json, "soft_skills"),
            "experience": safe_get_list(cv_json, "experience"),
        }
        
        job_exigences = safe_get_dict(job_json, "exigences")
        job_data = {
            "titre_poste": safe_get_string(job_json, "titre_poste"),
            "missions": safe_get_string(job_json, "missions"),
            "formation_requise": safe_get_string(job_exigences, "formation_requise"),
            "annees_experience": safe_get_int(job_exigences, "annees_experience"),
            "competences_obligatoires": safe_get_list(job_exigences, "competences_obligatoires"),
            "competences_souhaitees": safe_get_list(job_exigences, "competences_souhaitees"),
            "langues": safe_get_list(job_exigences, "langues"),
            "certifications": safe_get_list(job_exigences, "certifications"),
            "outils": safe_get_list(job_exigences, "outils"),
            "qualites_humaines": safe_get_list(job_exigences, "qualites_humaines"),
        }
        
        # ================================
        # 🆕 ANALYSE DES BUZZWORDS
        # ================================
        
        buzzword_analysis = {"cv": {}, "job": {}, "confidence_penalty": 0}
        
        if analyze_buzzwords:
            # Analyse du CV
            cv_full_text = f"{cv_data['titre_candidat']} {cv_data['profil_resume']} " + \
                          " ".join([str(exp) for exp in cv_data['experience']])
            
            buzzword_analysis["cv"] = skill_normalizer.analyze_buzzwords(cv_full_text)
            
            # Analyse de l'offre
            job_full_text = f"{job_data['titre_poste']} {job_data['missions']}"
            buzzword_analysis["job"] = skill_normalizer.analyze_buzzwords(job_full_text)
            
            # Pénalité de confiance si trop de buzzwords dans le CV
            buzzword_analysis["confidence_penalty"] = buzzword_analysis["cv"].get("confidence_penalty", 0)
        
        # ================================
        # VÉRIFICATION DES CRITÈRES MUST-HAVE
        # ================================
        
        cv_all_skills = cv_data["competences_techniques"] + cv_data["competences_informatiques"]
        job_requirements = job_data["competences_obligatoires"] + job_data["competences_souhaitees"]
        
        has_must_have, missing_must_have = check_must_have_requirements(cv_all_skills, job_requirements)
        
        if not has_must_have:
            must_have_failed = True
            logger_instance.logger.warning(f"Compétences obligatoires manquantes: {missing_must_have}")
            
            # Retour immédiat avec score 0 si must-have manquantes
            execution_time = time.time() - start_time
            logger_instance.log_matching_event(
                cv_id, job_id, 0, execution_time, {}, 
                must_have_failed=True, over_qualified=False
            )
            
            return {
                "total_score": 0,
                "confidence": 0,
                "interpretation": {
                    "level": "rejected",
                    "message": "Candidature rejetée - Compétences obligatoires manquantes",
                    "action": "REJETÉ - Compétences critiques absentes"
                },
                "recommendations": [{
                    "type": "critical_rejection",
                    "message": f"Candidature rejetée - Compétences obligatoires manquantes: {', '.join(missing_must_have)}",
                    "priority": "critical"
                }],
                "must_have_failed": True,
                "missing_must_have": missing_must_have,
                "execution_time_ms": round(execution_time * 1000, 2),
                "details": {},
                "buzzword_analysis": buzzword_analysis,
                "sentence_matching": {},
                "error": None
            }
        
        # ================================
        # 🆕 MATCHING AU NIVEAU DES PHRASES
        # ================================
        
        sentence_matching_results = {}
        
        if use_sentence_matching:
            # Construction des textes complets
            cv_full_text = f"{cv_data['titre_candidat']}. {cv_data['profil_resume']}. "
            for exp in cv_data['experience']:
                if isinstance(exp, dict):
                    cv_full_text += f"{safe_get_string(exp, 'poste')} {safe_get_string(exp, 'missions')}. "
                else:
                    cv_full_text += f"{str(exp)}. "
            
            job_full_text = f"{job_data['titre_poste']}. {job_data['missions']}. "
            
            sentence_matching_results = model_manager.sentence_level_matching(
                cv_full_text, job_full_text, top_k=3
            )
        
        # ================================
        # CALCULS DE MATCHING PAR CHAMP (inchangé)
        # ================================
        
        results = {}
        weights = config.weights
        
        # 1. Titre du poste
        cv_title = cv_data["titre_candidat"]
        job_title = job_data["titre_poste"]
        sim_title = cosine_similarity_safe(
            embed_with_cache(cv_title), 
            embed_with_cache(job_title)
        )
        results["titre_poste"] = {
            "score": sim_title,
            "weight": weights["titre_poste"],
            "cv_text": cv_title,
            "job_text": job_title
        }
        
        # 2. Profil / Résumé professionnel
        cv_resume = cv_data["profil_resume"]
        job_missions = job_data["missions"]
        sim_resume = cosine_similarity_safe(
            embed_with_cache(cv_resume), 
            embed_with_cache(job_missions)
        )
        results["profil_resume"] = {
            "score": sim_resume,
            "weight": weights["profil_resume"],
            "cv_text": cv_resume,
            "job_text": job_missions
        }
        
        # 3. Formation
        score_formation = calculate_education_score(cv_data["formations"], job_data["formation_requise"])
        results["formation"] = {
            "score": score_formation,
            "weight": weights["formation"],
            "cv_text": f"{len(cv_data['formations'])} formation(s)",
            "job_text": job_data["formation_requise"]
        }
        
        # 4. Expérience
        exp_candidate = cv_data["experience_years"]
        exp_required = job_data["annees_experience"]
        
        if exp_required == 0:
            score_exp = 1.0
        else:
            score_exp = min(1.0, exp_candidate / exp_required)
        
        results["experience_annees"] = {
            "score": score_exp,
            "weight": weights["experience_annees"],
            "cv_text": f"{exp_candidate} ans d'expérience",
            "job_text": f"{exp_required} ans requis"
        }
        
        # 5. Compétences techniques
        cv_skills_tech = cv_data["competences_techniques"]
        job_skills_tech = job_data["competences_obligatoires"] + job_data["competences_souhaitees"]
        
        # Jaccard avec normalisation
        jaccard_tech = jaccard_similarity_safe(cv_skills_tech, job_skills_tech)
        
        # Similarité sémantique
        text_cv_tech = " ".join(cv_skills_tech)
        text_job_tech = " ".join(job_skills_tech)
        semantic_tech = cosine_similarity_safe(
            embed_with_cache(text_cv_tech), 
            embed_with_cache(text_job_tech)
        )
        
        # 🆕 Boost avec sentence matching si disponible
        sentence_boost = 0
        if sentence_matching_results.get("score", 0) > 0.7:
            sentence_boost = 0.1  # Bonus de 10% si excellent matching par phrase
        
        # Combinaison pondérée (60% sémantique, 40% Jaccard + bonus)
        score_tech = 0.4 * jaccard_tech + 0.6 * semantic_tech + sentence_boost
        score_tech = min(1.0, score_tech)  # Cap à 1.0
        
        results["competences_techniques"] = {
            "score": score_tech,
            "weight": weights["competences_techniques"],
            "cv_text": ", ".join(cv_skills_tech[:5]) + ("..." if len(cv_skills_tech) > 5 else ""),
            "job_text": ", ".join(job_skills_tech[:5]) + ("..." if len(job_skills_tech) > 5 else "")
        }
        
        # 6. Compétences informatiques
        cv_skills_info = cv_data["competences_informatiques"]
        job_tools = job_data["outils"]
        score_info = jaccard_similarity_safe(cv_skills_info, job_tools)
        
        results["competences_informatiques"] = {
            "score": score_info,
            "weight": weights["competences_informatiques"],
            "cv_text": ", ".join(cv_skills_info),
            "job_text": ", ".join(job_tools)
        }
        
        # 7. Langues
        cv_langues = cv_data["langues"]
        job_langues = job_data["langues"]
        score_langues = calculate_language_score(cv_langues, job_langues)
        
        cv_langues_text = []
        for lang in cv_langues:
            if isinstance(lang, dict):
                langue = safe_get_string(lang, "langue")
                niveau = safe_get_string(lang, "niveau")
                cv_langues_text.append(f"{langue}:{niveau}")
            else:
                cv_langues_text.append(str(lang))
        
        results["langues"] = {
            "score": score_langues,
            "weight": weights["langues"],
            "cv_text": ", ".join(cv_langues_text),
            "job_text": ", ".join(job_langues)
        }
        
        # 8. Certifications
        cv_certifications = cv_data["certifications"]
        job_certifications = job_data["certifications"]
        
        if not job_certifications:
            score_certifications = 1.0
        else:
            # Normalisation des certifications
            normalized_cv_certs = {skill_normalizer.normalize_certification(str(c)) for c in cv_certifications}
            normalized_job_certs = {skill_normalizer.normalize_certification(str(c)) for c in job_certifications}
            
            matches = len(normalized_cv_certs & normalized_job_certs)
            score_certifications = matches / len(normalized_job_certs)
        
        results["certifications"] = {
            "score": score_certifications,
            "weight": weights["certifications"],
            "cv_text": ", ".join(cv_certifications),
            "job_text": ", ".join(job_certifications)
        }
        
        # 9. Projets
        cv_projets = cv_data["projets"]
        projets_descriptions = []
        for projet in cv_projets:
            if isinstance(projet, dict):
                desc = safe_get_string(projet, "description")
                nom = safe_get_string(projet, "nom")
                projets_descriptions.append(f"{nom} {desc}".strip())
            else:
                projets_descriptions.append(str(projet))
        
        cv_projets_text = " ".join(projets_descriptions)
        job_missions_text = job_data["missions"]
        
        sim_projets = cosine_similarity_safe(
            embed_with_cache(cv_projets_text), 
            embed_with_cache(job_missions_text)
        )
        
        results["projets"] = {
            "score": sim_projets,
            "weight": weights["projets"],
            "cv_text": cv_projets_text[:100] + "..." if len(cv_projets_text) > 100 else cv_projets_text,
            "job_text": job_missions_text[:100] + "..." if len(job_missions_text) > 100 else job_missions_text
        }
        
        # 10. Soft skills
        cv_soft_skills = cv_data["soft_skills"]
        job_soft_skills = job_data["qualites_humaines"]
        
        # Jaccard avec enrichissement des synonymes
        enhanced_cv_soft = skill_normalizer.enhance_soft_skills(cv_soft_skills)
        enhanced_job_soft = skill_normalizer.enhance_soft_skills(job_soft_skills)
        
        if not enhanced_job_soft:
            score_soft = 1.0
        else:
            matches = len(enhanced_cv_soft & enhanced_job_soft)
            union = len(enhanced_cv_soft | enhanced_job_soft)
            score_soft = matches / union if union > 0 else 0.0
        
        results["soft_skills"] = {
            "score": score_soft,
            "weight": weights["soft_skills"],
            "cv_text": ", ".join(cv_soft_skills),
            "job_text": ", ".join(job_soft_skills)
        }
        
        # ================================
        # CALCUL DU SCORE GLOBAL
        # ================================
        
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for field, data in results.items():
            weight = data["weight"]
            score = data["score"]
            total_weighted_score += score * weight
            total_weight += weight
        
        final_score = (total_weighted_score / total_weight) * 100 if total_weight > 0 else 0
        
        # 🆕 Application de la pénalité buzzwords
        buzzword_penalty = buzzword_analysis.get("confidence_penalty", 0)
        if buzzword_penalty > 0:
            final_score = final_score * (1 - buzzword_penalty)
        
        final_score = max(0, min(100, int(final_score)))
        
        # ================================
        # GÉNÉRATION DES MÉTADONNÉES
        # ================================
        
        # Calcul de la confiance basé sur la complétude des données
        confidence_factors = []
        for field, data in results.items():
            cv_text_length = len(data["cv_text"])
            job_text_length = len(data["job_text"])
            
            if cv_text_length > 0 and job_text_length > 0:
                confidence_factors.append(1.0)
            elif cv_text_length > 0 or job_text_length > 0:
                confidence_factors.append(0.5)
            else:
                confidence_factors.append(0.0)
        
        base_confidence = sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
        
        # 🆕 Ajustement de confiance avec buzzwords et sentence matching
        adjusted_confidence = base_confidence * (1 - buzzword_penalty)
        if sentence_matching_results.get("coverage", 0) > 0.5:
            adjusted_confidence = min(1.0, adjusted_confidence + 0.1)  # Bonus confiance
        
        # Interprétation du score
        if final_score >= 85:
            interpretation = {
                "level": "excellent",
                "message": "Candidat excellemment aligné avec le poste",
                "action": "Programmer un entretien en priorité"
            }
        elif final_score >= 70:
            interpretation = {
                "level": "very_good",
                "message": "Très bon profil avec correspondance élevée",
                "action": "Candidat fortement recommandé"
            }
        elif final_score >= 55:
            interpretation = {
                "level": "good",
                "message": "Bon potentiel avec quelques écarts mineurs",
                "action": "À considérer selon priorités de recrutement"
            }
        elif final_score >= 40:
            interpretation = {
                "level": "fair",
                "message": "Profil partiellement aligné, gaps significatifs",
                "action": "Formation ou développement nécessaire"
            }
        else:
            interpretation = {
                "level": "poor",
                "message": "Profil peu adapté au poste requis",
                "action": "Non recommandé pour ce poste"
            }
        
        # 🆕 Ajustement de l'interprétation avec buzzwords
        if buzzword_penalty > 0.2:
            interpretation["message"] += " (Attention: CV avec buzzwords excessifs)"
        
        # Recommandations avancées
        recommendations = []
        for field, data in results.items():
            score = data["score"]
            if score < 0.6:  # Seuil d'amélioration
                if field == "competences_techniques":
                    recommendations.append({
                        "type": "skill_gap",
                        "field": field,
                        "message": f"Améliorer les compétences techniques requises",
                        "priority": "high"
                    })
                elif field == "experience_annees":
                    recommendations.append({
                        "type": "experience_gap",
                        "field": field,
                        "message": f"Acquérir plus d'expérience professionnelle",
                        "priority": "medium"
                    })
        
        # 🆕 Recommandations spécifiques aux buzzwords
        if buzzword_penalty > 0.1:
            recommendations.append({
                "type": "content_quality",
                "message": f"Réduire l'usage de buzzwords dans le CV ({len(buzzword_analysis['cv'].get('detected', []))} détectés)",
                "priority": "medium"
            })
        
        # 🆕 Recommandations basées sur sentence matching
        if sentence_matching_results.get("coverage", 0) < 0.3:
            recommendations.append({
                "type": "content_alignment",
                "message": "Mieux aligner les descriptions d'expérience avec les missions du poste",
                "priority": "medium"
            })
        
        execution_time = time.time() - start_time
        
        # Résultat final optimisé
        final_result = {
            "total_score": final_score,
            "confidence": round(adjusted_confidence * 100, 1),
            "interpretation": interpretation,
            "recommendations": recommendations,
            "must_have_failed": must_have_failed,
            "execution_time_ms": round(execution_time * 1000, 2),
            "details": {
                field: {
                    "score": int(data["score"] * 100),
                    "weight": data["weight"],
                    "cv_text": data["cv_text"] or "[VIDE]",
                    "job_text": data["job_text"] or "[VIDE]"
                }
                for field, data in results.items()
            },
            # 🆕 Nouvelles métriques
            "buzzword_analysis": buzzword_analysis,
            "sentence_matching": sentence_matching_results,
            "cache_stats": embedding_cache.get_stats(),
            "config_used": config.job_type,
            "optimizations_used": {
                "sentence_matching": use_sentence_matching and bool(sentence_matching_results),
                "buzzword_detection": analyze_buzzwords and bool(buzzword_analysis["cv"]),
                "multilingue_support": True  # BGE-M3 supporte nativement
            },
            "error": None
        }
        
        # Log de l'événement
        logger_instance.log_matching_event(
            cv_id, job_id, final_score, execution_time, results,
            must_have_failed=must_have_failed, over_qualified=False
        )
        
        return final_result
        
    except Exception as e:
        execution_time = time.time() - start_time
        error_msg = str(e)
        
        logger_instance.log_matching_event(
            cv_id, job_id, 0, execution_time, {}, error_msg,
            must_have_failed=must_have_failed, over_qualified=False
        )
        
        return {
            "error": error_msg,
            "total_score": 0,
            "confidence": 0,
            "interpretation": {
                "level": "error",
                "message": "Erreur lors du calcul de matching",
                "action": "Vérifier les données d'entrée"
            },
            "recommendations": [],
            "execution_time_ms": round(execution_time * 1000, 2),
            "details": {},
            "buzzword_analysis": {},
            "sentence_matching": {},
            "debug_info": {
                "cv_keys": list(cv_json.keys()) if isinstance(cv_json, dict) else "invalid",
                "job_keys": list(job_json.keys()) if isinstance(job_json, dict) else "invalid",
                "model_ready": model_manager.is_ready()
            }
        }

# ================================
# 9. FONCTIONS D'AFFICHAGE OPTIMISÉES
# ================================

def display_results_enhanced(result: Dict):
    """Affichage amélioré des résultats avec nouvelles métriques"""
    print("\n" + "="*80)
    print("🎯 RÉSULTATS DU MATCHING CV ↔ OFFRE D'EMPLOI (VERSION OPTIMISÉE)")
    print("="*80)
    
    # Score global
    score = result["total_score"]
    confidence = result.get("confidence", 0)
    interpretation = result.get("interpretation", {})
    
    print(f"\n📊 SCORE GLOBAL : {score}/100")
    print(f"🎯 NIVEAU : {interpretation.get('level', 'unknown').upper()}")
    print(f"💡 INTERPRÉTATION : {interpretation.get('message', 'Non disponible')}")
    print(f"🎬 ACTION RECOMMANDÉE : {interpretation.get('action', 'Non disponible')}")
    print(f"🔒 CONFIANCE : {confidence}%")
    
    # Alertes spéciales
    if result.get("must_have_failed", False):
        print(f"🚨 ALERTE CRITIQUE : Compétences obligatoires manquantes")
        missing = result.get("missing_must_have", [])
        if missing:
            print(f"   Manquantes : {', '.join(missing)}")
    
    # 🆕 Analyse des buzzwords
    buzzword_analysis = result.get("buzzword_analysis", {})
    if buzzword_analysis.get("cv", {}).get("detected"):
        cv_buzzwords = buzzword_analysis["cv"]
        print(f"⚠️  BUZZWORDS DÉTECTÉS : {cv_buzzwords.get('density', 0)}% du CV")
        print(f"   Exemples : {', '.join(cv_buzzwords.get('detected', [])[:3])}")
        if cv_buzzwords.get("confidence_penalty", 0) > 0:
            print(f"   Pénalité appliquée : -{cv_buzzwords.get('confidence_penalty', 0)*100:.1f}%")
    
    # 🆕 Résultats du sentence matching
    sentence_matching = result.get("sentence_matching", {})
    if sentence_matching.get("matches"):
        print(f"\n🔍 MATCHING PAR PHRASES (Score: {sentence_matching.get('score', 0):.2f}):")
        print(f"   Couverture : {sentence_matching.get('coverage', 0)*100:.1f}%")
        for i, match in enumerate(sentence_matching.get("matches", [])[:2], 1):
            print(f"   {i}. Similarité {match.get('similarity', 0):.2f}")
            print(f"      CV : {match.get('cv_sentence', '')[:80]}...")
            print(f"      Job: {match.get('job_sentence', '')[:80]}...")
    
    # Barre de progression
    bar_length = 50
    filled_length = int(bar_length * score / 100)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    color_indicator = "🟢" if score >= 70 else "🟡" if score >= 50 else "🔴"
    print(f"📈 {color_indicator} [{bar}] {score}%")
    
    # Détails par catégorie (inchangé)
    print(f"\n📋 DÉTAIL PAR CATÉGORIE:")
    print("-" * 80)
    
    for field, data in result.get("details", {}).items():
        field_score = data["score"]
        weight = data["weight"]
        
        if field_score >= 80:
            indicator = "🟢"
            status = "EXCELLENT"
        elif field_score >= 60:
            indicator = "🟡"
            status = "BON"
        elif field_score >= 40:
            indicator = "🟠"
            status = "MOYEN"
        else:
            indicator = "🔴"
            status = "FAIBLE"
        
        print(f"\n{indicator} {field.upper().replace('_', ' ')} - {status}")
        print(f"   Score : {field_score}/100 (Poids: {weight})")
        
        # Mini barre
        mini_bar_length = 20
        mini_filled = int(mini_bar_length * field_score / 100)
        mini_bar = "█" * mini_filled + "░" * (mini_bar_length - mini_filled)
        print(f"   [{mini_bar}]")
        
        print(f"   📝 CV : {data['cv_text'][:60]}{'...' if len(data['cv_text']) > 60 else ''}")
        print(f"   📄 Offre : {data['job_text'][:60]}{'...' if len(data['job_text']) > 60 else ''}")
    
    # Recommandations
    recommendations = result.get("recommendations", [])
    if recommendations:
        print(f"\n💡 RECOMMANDATIONS D'AMÉLIORATION:")
        print("-" * 80)
        
        for i, rec in enumerate(recommendations, 1):
            priority = rec.get("priority", "medium")
            if priority == "critical":
                priority_icon = "🚨"
            elif priority == "high":
                priority_icon = "🔴"
            elif priority == "medium":
                priority_icon = "🟡"
            else:
                priority_icon = "🔵"
            
            print(f"{i}. {priority_icon} {rec['message']}")
    
    # Statistiques techniques optimisées
    exec_time = result.get("execution_time_ms", 0)
    cache_stats = result.get("cache_stats", {})
    optimizations = result.get("optimizations_used", {})
    
    print(f"\n⚡ STATISTIQUES TECHNIQUES:")
    print("-" * 80)
    print(f"⏱️  Temps d'exécution : {exec_time}ms")
    print(f"🎛️  Configuration : {result.get('config_used', 'default')}")
    print(f"💾 Cache - Taille: {cache_stats.get('size', 0)}, Hit rate: {cache_stats.get('hit_rate', 0)}%")
    
    # 🆕 Nouvelles statistiques
    print(f"\n🚀 OPTIMISATIONS UTILISÉES:")
    opt_icons = {"sentence_matching": "📝", "buzzword_detection": "⚠️", "multilingue_support": "🌍"}
    for opt, used in optimizations.items():
        status = "✅ Activé" if used else "❌ Désactivé"
        icon = opt_icons.get(opt, "🔧")
        print(f"   {icon} {opt.replace('_', ' ').title()}: {status}")
    
    if result.get("error"):
        print(f"\n❌ ERREUR : {result['error']}")
    
    print("="*80)

# ================================
# 10. FONCTIONS UTILITAIRES AVANCÉES
# ================================

def get_system_stats() -> Dict:
    """Récupère les statistiques globales du système optimisé"""
    return {
        "model_status": {
            "ready": model_manager.is_ready(),
            "bi_encoder": model_manager.bi_encoder_name,
            "cross_encoder": model_manager.cross_encoder_name,
            "cross_encoder_ready": model_manager.cross_encoder is not None
        },
        "cache_stats": embedding_cache.get_stats(),
        "performance_stats": logger_instance.get_performance_stats(),
        "normalizer_stats": {
            "skills_mapped": len(skill_normalizer.skill_reverse_map),
            "certifications_mapped": len(skill_normalizer.cert_reverse_map),
            "soft_skills_mapped": len(skill_normalizer.soft_reverse_map),
            "buzzwords_tracked": len(skill_normalizer.all_buzzwords)
        }
    }

def batch_matching_enhanced_optimized(cv_list: List[Dict], job_data: Dict, 
                                    config: MatchingConfig = None,
                                    filter_must_have: bool = True,
                                    use_reranking: bool = True,
                                    top_k_rerank: int = 10) -> List[Dict]:
    """Traitement par lot optimisé avec re-ranking"""
    if not cv_list:
        return []
    
    results = []
    start_time = time.time()
    must_have_rejected = 0
    
    logger_instance.logger.info(f"Début du traitement par lot optimisé: {len(cv_list)} CV")
    
    # Phase 1: Calcul des scores initiaux
    for i, cv_data in enumerate(cv_list):
        try:
            cv_id = cv_data.get("id", f"cv_{i}")
            job_id = job_data.get("id", "job_unknown")
            
            result = calculate_match_score_enhanced(
                cv_data, job_data, cv_id, job_id, config,
                use_sentence_matching=True, analyze_buzzwords=True
            )
            
            # Filtrage optionnel des candidats sans must-have
            if filter_must_have and result.get("must_have_failed", False):
                must_have_rejected += 1
                continue
            
            # Préparation du texte CV pour le re-ranking
            cv_text = f"{cv_data.get('titre_candidat', '')} {cv_data.get('profil_resume', '')}"
            
            results.append({
                "cv_id": cv_id,
                "result": result,
                "cv_text": cv_text,
                "score": result.get("total_score", 0),
                "rank": len(results) + 1
            })
            
        except Exception as e:
            logger_instance.logger.error(f"Erreur CV {i}: {str(e)}")
            results.append({
                "cv_id": cv_data.get("id", f"cv_{i}"),
                "result": {"error": str(e), "total_score": 0},
                "cv_text": "",
                "score": 0,
                "rank": -1
            })
    
    # Tri par score décroissant
    results.sort(key=lambda x: x["score"], reverse=True)
    
    # Phase 2: Re-ranking avec cross-encoder pour les meilleurs candidats
    if use_reranking and len(results) > 1:
        job_text = f"{job_data.get('titre_poste', '')} {job_data.get('missions', '')}"
        results = rerank_candidates_with_cross_encoder(results, job_text, top_k_rerank)
    
    # Mise à jour des rangs finaux
    for i, result in enumerate(results):
        result["rank"] = i + 1
    
    total_time = time.time() - start_time
    logger_instance.logger.info(
        f"Traitement par lot optimisé terminé: {len(results)} résultats "
        f"(dont {must_have_rejected} rejetés) en {total_time:.2f}s"
    )
    
    return results

def quick_match_optimized(cv_data: Dict, job_data: Dict, job_type: str = "auto") -> int:
    """Matching rapide optimisé retournant juste le score"""
    try:
        config = MatchingConfig(job_type) if job_type != "auto" else None
        result = calculate_match_score_enhanced(
            cv_data, job_data, config=config,
            use_sentence_matching=False,  # Plus rapide sans sentence matching
            analyze_buzzwords=False       # Plus rapide sans analyse buzzwords
        )
        return result.get("total_score", 0)
    except:
        return 0

# ================================
# 11. FONCTIONS D'ANALYSE AVANCÉE
# ================================

def analyze_skill_gaps_advanced(cv_data: Dict, job_data: Dict) -> Dict:
    """Analyse détaillée des écarts de compétences avec détection multilingue"""
    try:
        cv_skills = set()
        cv_skills.update(safe_get_list(cv_data, "competences_techniques"))
        cv_skills.update(safe_get_list(cv_data, "competences_informatiques"))
        
        job_exigences = safe_get_dict(job_data, "exigences")
        job_skills = set()
        job_skills.update(safe_get_list(job_exigences, "competences_obligatoires"))
        job_skills.update(safe_get_list(job_exigences, "competences_souhaitees"))
        
        # Normalisation avec support multilingue
        normalized_cv = set()
        normalized_job = set()
        
        for skill in cv_skills:
            if skill:
                # Normalisation standard + détection langue
                normalized_skill = skill_normalizer.normalize_skill(str(skill).lower())
                normalized_cv.add(normalized_skill)
        
        for skill in job_skills:
            if skill:
                normalized_skill = skill_normalizer.normalize_skill(str(skill).lower())
                normalized_job.add(normalized_skill)
        
        # Analyse des écarts
        matching_skills = normalized_cv & normalized_job
        missing_skills = normalized_job - normalized_cv
        extra_skills = normalized_cv - normalized_job
        
        # Identification des must-have manquantes
        must_have_skills = skill_normalizer.get_must_have_skills(
            safe_get_list(job_exigences, "competences_obligatoires")
        )
        critical_missing = must_have_skills - normalized_cv
        
        # 🆕 Analyse sémantique des compétences manquantes
        semantic_matches = []
        if missing_skills and extra_skills:
            for missing in list(missing_skills)[:5]:  # Top 5 manquantes
                missing_emb = embed_with_cache(missing)
                if missing_emb is not None:
                    best_match = ""
                    best_score = 0.0
                    
                    for extra in extra_skills:
                        extra_emb = embed_with_cache(extra)
                        if extra_emb is not None:
                            similarity = cosine_similarity_safe(missing_emb, extra_emb)
                            if similarity > best_score and similarity > 0.6:  # Seuil de proximité
                                best_score = similarity
                                best_match = extra
                    
                    if best_match:
                        semantic_matches.append({
                            "missing": missing,
                            "closest_cv_skill": best_match,
                            "similarity": round(best_score, 3)
                        })
        
        return {
            "matching_skills": list(matching_skills),
            "missing_skills": list(missing_skills),
            "extra_skills": list(extra_skills),
            "critical_missing": list(critical_missing),
            "semantic_matches": semantic_matches,  # 🆕 Nouveau
            "coverage_rate": len(matching_skills) / len(normalized_job) if normalized_job else 1.0,
            "skill_match_count": len(matching_skills),
            "total_job_skills": len(normalized_job),
            "has_critical_gaps": bool(critical_missing),
            "transferable_skills": len(semantic_matches)  # 🆕 Nouveau
        }
    except Exception as e:
        logger_instance.logger.error(f"Erreur analyse skill gaps avancée: {str(e)}")
        return {"error": str(e)}

def detect_language_mixing(text: str) -> Dict:
    """Détecte le mélange français-anglais dans un texte"""
    try:
        # Mots indicateurs de français
        french_indicators = [
            "développeur", "ingénieur", "expérience", "compétences", "formation",
            "projets", "équipe", "gestion", "développement", "système"
        ]
        
        # Mots indicateurs d'anglais
        english_indicators = [
            "developer", "engineer", "experience", "skills", "training",
            "projects", "team", "management", "development", "system"
        ]
        
        text_lower = text.lower()
        french_count = sum(1 for word in french_indicators if word in text_lower)
        english_count = sum(1 for word in english_indicators if word in text_lower)
        
        total_indicators = french_count + english_count
        
        if total_indicators == 0:
            return {"primary_language": "unknown", "mixing_detected": False, "confidence": 0}
        
        french_ratio = french_count / total_indicators
        mixing_detected = min(french_ratio, 1 - french_ratio) > 0.2  # Plus de 20% de l'autre langue
        
        return {
            "primary_language": "french" if french_ratio > 0.5 else "english",
            "mixing_detected": mixing_detected,
            "french_ratio": round(french_ratio, 2),
            "english_ratio": round(1 - french_ratio, 2),
            "confidence": round(max(french_ratio, 1 - french_ratio), 2)
        }
        
    except Exception as e:
        logger_instance.logger.error(f"Erreur détection langue: {str(e)}")
        return {"primary_language": "unknown", "mixing_detected": False, "confidence": 0}





# ================================
# 14. FONCTIONS EXPORT OPTIMISÉES
# ================================

def export_matching_report(results: List[Dict], job_data: Dict, filepath: str) -> bool:
    """Exporte un rapport de matching optimisé avec toutes les métriques"""
    try:
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "job_title": safe_get_string(job_data, "titre_poste"),
                "total_candidates": len(results),
                "system_version": "optimized_v2.0"
            },
            "job_requirements": {
                "title": safe_get_string(job_data, "titre_poste"),
                "missions": safe_get_string(job_data, "missions"),
                "exigences": safe_get_dict(job_data, "exigences")
            },
            "candidates": [],
            "statistics": {
                "scores": [r.get("result", {}).get("total_score", 0) for r in results],
                "avg_score": 0,
                "optimizations_usage": {
                    "sentence_matching_used": 0,
                    "buzzword_detection_used": 0,
                    "reranking_used": 0
                }
            }
        }
        
        # Traitement des candidats
        for candidate in results:
            result = candidate.get("result", {})
            
            candidate_data = {
                "cv_id": candidate.get("cv_id"),
                "rank": candidate.get("rank"),
                "score": result.get("total_score", 0),
                "confidence": result.get("confidence", 0),
                "interpretation": result.get("interpretation", {}),
                "details": result.get("details", {}),
                "buzzword_analysis": result.get("buzzword_analysis", {}),
                "sentence_matching": result.get("sentence_matching", {}),
                "recommendations": result.get("recommendations", []),
                "optimizations_used": result.get("optimizations_used", {}),
                "execution_time_ms": result.get("execution_time_ms", 0)
            }
            
            report["candidates"].append(candidate_data)
            
            # Mise à jour des statistiques d'usage
            opt_used = result.get("optimizations_used", {})
            if opt_used.get("sentence_matching"):
                report["statistics"]["optimizations_usage"]["sentence_matching_used"] += 1
            if opt_used.get("buzzword_detection"):
                report["statistics"]["optimizations_usage"]["buzzword_detection_used"] += 1
            if candidate.get("used_reranking"):
                report["statistics"]["optimizations_usage"]["reranking_used"] += 1
        
        # Calcul des statistiques finales
        scores = report["statistics"]["scores"]
        if scores:
            report["statistics"]["avg_score"] = sum(scores) / len(scores)
            report["statistics"]["min_score"] = min(scores)
            report["statistics"]["max_score"] = max(scores)
        
        # Export en JSON
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        logger_instance.logger.info(f"Rapport optimisé exporté vers {filepath}")
        return True
        
    except Exception as e:
        logger_instance.logger.error(f"Erreur export rapport optimisé: {str(e)}")
        return False

# Point d'entrée principal
# File: ATS_MAR/ai_engine/services/matching_service_enhanced_optimized.py
# ... (le reste de votre code reste inchangé jusqu'à la fonction main) ...

# Point d'entrée principal
if __name__ == "__main__":
    import argparse
    import sys
    from pathlib import Path

    # Importation du CVParser (déjà présent, mais pour clarté)
    try:
        # Assurez-vous que le chemin d'importation est correct pour votre structure de projet
        # Si cv_parser.py est dans un dossier parent ou un dossier frère, ajustez sys.path si nécessaire.
        # Dans votre contexte, il semble que 'cv_parser' soit un module directement importable.
        from cv_parser import CVParser, ParsingResult
    except ImportError:
        print("❌ Erreur d'import: cv_parser non trouvé.")
        print("💡 Assurez-vous que 'cv_parser.py' est accessible dans le PYTHONPATH ou le même répertoire.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Service de Matching CV ↔ Offre d'emploi")
    parser.add_argument("command", 
                       choices=["match", "batch-match", "stats"], 
                       help="Type d'opération à effectuer")
    parser.add_argument("--cv-path", "-cv", 
                       help="Chemin vers le fichier PDF du CV (pour 'match')")
    parser.add_argument("--job-path", "-job", 
                       help="Chemin vers le fichier PDF de l'offre d'emploi (pour 'match')")
    parser.add_argument("--cv-dir", 
                       help="Chemin vers le dossier contenant les CVs PDF (pour 'batch-match')")
    parser.add_argument("--job-file", 
                       help="Chemin vers le fichier PDF de l'offre d'emploi unique (pour 'batch-match')")
    parser.add_argument("--output", "-o", 
                       help="Fichier ou dossier de sortie pour les résultats")
    parser.add_argument("--gemma-model", default="gemma3:4b", 
                       help="Modèle Gemma à utiliser pour le parsing (ex: gemma3:4b)")
    parser.add_argument("--ollama-url", default="http://localhost:11434", 
                       help="URL du serveur Ollama pour le parsing")
    parser.add_argument("--pdf-extraction-method", default="auto", 
                       choices=["auto", "pypdf", "pdfplumber", "ocr"],
                       help="Méthode d'extraction PDF pour le parsing")
    parser.add_argument("--llm-temperature", type=float, default=0.1, 
                       help="Température LLM pour le parsing")
    parser.add_argument("--validation-strict", action="store_true", 
                       help="Validation stricte pour le parsing")
    parser.add_argument("--log-level", default="INFO", 
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Niveau de log")
    
    args = parser.parse_args()

    try:
        # Initialisation du CVParser
        print("Initialisation du CVParser...")
        cv_parser_instance = CVParser(
            gemma_model=args.gemma_model,
            ollama_url=args.ollama_url,
            pdf_extraction_method=args.pdf_extraction_method,
            llm_temperature=args.llm_temperature,
            validation_strict=args.validation_strict,
            log_level=args.log_level
        )
        print("CVParser initialisé.")

        # Assurez-vous que les modèles de matching sont chargés
        print("Chargement des modèles de matching (bi-encoder, cross-encoder)...")
        # L'instance globale 'model_manager' est créée lors de l'importation du module.
        # Nous pouvons juste vérifier qu'elle est prête.
        if not model_manager.is_ready():
            raise RuntimeError("Les modèles de matching n'ont pas pu être chargés.")
        print("Modèles de matching chargés.")

        if args.command == "match":
            if not args.cv_path or not args.job_path:
                print("❌ Les commandes 'match' nécessitent --cv-path et --job-path.")
                sys.exit(1)
            
            print(f"\n--- Démarrage du parsing et matching avancé ---")
            
            # 1. Parsing du CV
            print(f"Parsing du CV depuis : {args.cv_path}")
            cv_parsing_result = cv_parser_instance.parse_cv_from_pdf(args.cv_path)
            if not cv_parsing_result.success:
                print(f"❌ Échec du parsing du CV : {cv_parsing_result.errors}")
                sys.exit(1)
            print(f"✅ CV parsé avec succès. Confiance : {cv_parsing_result.confidence:.2f}")

            # 2. Parsing de l'offre d'emploi
            print(f"Parsing de l'offre d'emploi depuis : {args.job_path}")
            job_parsing_result = cv_parser_instance.parse_job_from_pdf(args.job_path)
            if not job_parsing_result.success:
                print(f"❌ Échec du parsing de l'offre : {job_parsing_result.errors}")
                sys.exit(1)
            print(f"✅ Offre parsée avec succès. Confiance : {job_parsing_result.confidence:.2f}")
            
            # 3. Exécution du matching avancé
            print("\n--- Exécution du matching avancé CV ↔ Offre ---")
            match_result = calculate_match_score_enhanced(
                cv_json=cv_parsing_result.data,
                job_json=job_parsing_result.data,
                cv_id=Path(args.cv_path).stem,
                job_id=Path(args.job_path).stem,
                use_sentence_matching=True,
                analyze_buzzwords=True
            )
            
            # Affichage des résultats
            display_results_enhanced(match_result)

            if args.output:
                export_matching_report(
                    [{"cv_id": Path(args.cv_path).stem, "result": match_result}], 
                    job_parsing_result.data, 
                    args.output
                )
                print(f"✅ Rapport de matching exporté vers {args.output}")

        elif args.command == "batch-match":
            if not args.cv_dir or not args.job_file:
                print("❌ Les commandes 'batch-match' nécessitent --cv-dir et --job-file.")
                sys.exit(1)
            
            print(f"\n--- Démarrage du traitement par lot ---")
            
            # 1. Parsing de l'offre d'emploi unique pour le lot
            print(f"Parsing de l'offre d'emploi pour le lot : {args.job_file}")
            job_parsing_result = cv_parser_instance.parse_job_from_pdf(args.job_file)
            if not job_parsing_result.success:
                print(f"❌ Échec du parsing de l'offre pour le lot : {job_parsing_result.errors}")
                sys.exit(1)
            job_data_for_batch = job_parsing_result.data
            print(f"✅ Offre parsée avec succès pour le lot. Confiance : {job_parsing_result.confidence:.2f}")

            # 2. Collecte et parsing des CVs du répertoire
            cv_files = list(Path(args.cv_dir).glob("*.pdf"))
            if not cv_files:
                print(f"⚠️ Aucun fichier PDF trouvé dans le répertoire des CVs : {args.cv_dir}")
                sys.exit(0)
            
            cv_data_list = []
            print(f"Parsing de {len(cv_files)} CVs depuis : {args.cv_dir}")
            for cv_file in cv_files:
                print(f"  Parsing CV : {cv_file.name}")
                cv_res = cv_parser_instance.parse_cv_from_pdf(str(cv_file))
                if cv_res.success:
                    cv_data_list.append({"id": cv_file.stem, "data": cv_res.data})
                else:
                    print(f"  ❌ Échec du parsing de {cv_file.name}: {cv_res.errors}")
            
            if not cv_data_list:
                print("❌ Aucun CV n'a pu être parsé avec succès pour le traitement par lot.")
                sys.exit(1)

            # 3. Exécution du matching par lot
            print(f"\n--- Exécution du matching par lot pour {len(cv_data_list)} CVs ---")
            # batch_matching_enhanced_optimized attend une liste de dictionnaires avec 'id' et les données du CV
            # Nous devons adapter la structure de cv_data_list pour correspondre à l'attente de batch_matching_enhanced_optimized
            # La fonction batch_matching_enhanced_optimized attend une liste de dict où chaque dict est un CV JSON complet
            # et non un dict avec 'id' et 'data'.
            # Nous allons donc créer une liste de CVs JSON directement.
            
            # Adapter la liste des CVs pour batch_matching_enhanced_optimized
            cv_json_list_for_batch = []
            for cv_item in cv_data_list:
                cv_json_data = cv_item["data"]
                cv_json_data["id"] = cv_item["id"] # Ajouter l'ID directement dans les données du CV si nécessaire pour le logging interne
                cv_json_list_for_batch.append(cv_json_data)

            batch_results = batch_matching_enhanced_optimized(
                cv_list=cv_json_list_for_batch,
                job_data=job_data_for_batch,
                use_reranking=True,
                top_k_rerank=10
            )
            
            print("\n--- Résultats du traitement par lot ---")
            for res in batch_results:
                score = res.get("result", {}).get("total_score", 0)
                print(f"CV: {res['cv_id']} - Score: {score}/100 - Rang: {res['rank']}")
            
            if args.output:
                export_matching_report(batch_results, job_data_for_batch, args.output)
                print(f"✅ Rapport de lot exporté vers {args.output}")

        elif args.command == "stats":
            print("\n--- Statistiques du système de matching ---")
            stats = get_system_stats()
            print(json.dumps(stats, indent=2, ensure_ascii=False))
            
    except Exception as e:
        print(f"\n\n❌ Erreur critique: {str(e)}")
        logger_instance.logger.error(f"Erreur critique dans main: {str(e)}")
    finally:
        print("\n👋 Fin du programme")

