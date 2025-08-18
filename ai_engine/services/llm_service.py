# llm_service/gemma_client.py
# Client optimisé pour interaction avec Gemma3 via Ollama
# Support des prompts CV/Offre avec gestion d'erreurs robuste

from langchain_ollama import OllamaLLM
from typing import Optional, Dict, List, Any
import json
import time
import logging
import re
from dataclasses import dataclass
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

@dataclass
class LLMResponse:
    """Réponse structurée du LLM avec métadonnées"""
    content: str
    tokens_used: int
    execution_time: float
    model_used: str
    temperature: float
    success: bool
    error: Optional[str] = None
    retries_used: int = 0

class GemmaClient:
    """
    Client optimisé pour Gemma3 avec retry logic et validation
    Spécialement conçu pour parsing CV et offres d'emploi
    """
    
    def __init__(self, 
                 model_name: str = "gemma3:2b",
                 base_url: str = "http://localhost:11434",
                 temperature: float = 0.1,
                 max_retries: int = 3,
                 timeout: int = 120,
                 log_level: str = "INFO"):
        
        self.model_name = model_name
        self.base_url = base_url
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        
        self.setup_logging(log_level)
        self._initialize_client()
        
        # Métriques de performance
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "average_response_time": 0.0
        }
        
    def setup_logging(self, log_level: str):
        """Configuration du logging"""
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger('GemmaClient')
    
    def _initialize_client(self):
        """Initialisation du client Ollama avec validation"""
        try:
            self.llm = OllamaLLM(
                model=self.model_name,
                base_url=self.base_url,
                temperature=self.temperature,
                timeout=self.timeout
            )
            
            # Test de connexion
            self._test_connection()
            self.logger.info(f"Client Gemma3 initialisé: {self.model_name}")
            
        except Exception as e:
            self.logger.error(f"Erreur initialisation client: {str(e)}")
            raise Exception(f"Impossible d'initialiser le client Gemma3: {str(e)}")
    
    def _test_connection(self):
        """Test de connexion avec le modèle"""
        try:
            test_prompt = "Réponds simplement: OK"
            response = self.llm.invoke(test_prompt)
            
            if not response or len(response.strip()) == 0:
                raise Exception("Réponse vide du modèle")
                
            self.logger.info("Test de connexion réussi")
            
        except Exception as e:
            raise Exception(f"Test de connexion échoué: {str(e)}")
    
    def invoke(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Invocation robuste avec retry et métriques
        
        Args:
            prompt: Le prompt à envoyer
            **kwargs: Arguments supplémentaires (temperature, etc.)
            
        Returns:
            LLMResponse avec contenu et métadonnées
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        # Override des paramètres si fournis
        temp = kwargs.get('temperature', self.temperature)
        
        for attempt in range(self.max_retries):
            try:
                self.logger.info(f"Invocation tentative {attempt + 1}/{self.max_retries}")
                
                # Configuration temporaire si différente
                if temp != self.temperature:
                    original_temp = self.llm.temperature
                    self.llm.temperature = temp
                
                # Invocation
                response_content = self.llm.invoke(prompt)
                
                # Restauration température originale
                if temp != self.temperature:
                    self.llm.temperature = original_temp
                
                # Validation de la réponse
                if not response_content or len(response_content.strip()) == 0:
                    raise Exception("Réponse vide du modèle")
                
                execution_time = time.time() - start_time
                tokens_estimate = self._estimate_tokens(prompt + response_content)
                
                # Mise à jour des statistiques
                self.stats["successful_requests"] += 1
                self.stats["total_tokens"] += tokens_estimate
                self.stats["total_time"] += execution_time
                self.stats["average_response_time"] = (
                    self.stats["total_time"] / self.stats["successful_requests"]
                )
                
                self.logger.info(f"Réponse reçue: {len(response_content)} chars en {execution_time:.2f}s")
                
                return LLMResponse(
                    content=response_content,
                    tokens_used=tokens_estimate,
                    execution_time=execution_time,
                    model_used=self.model_name,
                    temperature=temp,
                    success=True,
                    retries_used=attempt
                )
                
            except Exception as e:
                self.logger.warning(f"Tentative {attempt + 1} échouée: {str(e)}")
                
                if attempt == self.max_retries - 1:
                    # Dernière tentative échouée
                    execution_time = time.time() - start_time
                    self.stats["failed_requests"] += 1
                    
                    return LLMResponse(
                        content="",
                        tokens_used=0,
                        execution_time=execution_time,
                        model_used=self.model_name,
                        temperature=temp,
                        success=False,
                        error=str(e),
                        retries_used=attempt + 1
                    )
                
                # Attente avant retry
                time.sleep(2 ** attempt)  # Backoff exponentiel
        
        # Ne devrait jamais arriver
        return LLMResponse(
            content="",
            tokens_used=0,
            execution_time=0,
            model_used=self.model_name,
            temperature=temp,
            success=False,
            error="Max retries exceeded"
        )
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimation approximative du nombre de tokens"""
        # Estimation simple: ~4 caractères par token pour le français
        return len(text) // 4
    
    def invoke_with_json_validation(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Invocation avec validation JSON intégrée
        Idéal pour parsing CV/offres
        """
        response = self.invoke(prompt, **kwargs)
        
        if response.success:
            # Tentative d'extraction et validation JSON
            json_content = self._extract_json_from_response(response.content)
            if json_content:
                response.content = json_content
                self.logger.info("JSON valide extrait de la réponse")
            else:
                response.success = False
                response.error = "Aucun JSON valide trouvé dans la réponse"
                self.logger.warning("Réponse ne contient pas de JSON valide")
        
        return response
    
    def _extract_json_from_response(self, text: str) -> Optional[str]:
        """Extrait et valide le JSON d'une réponse"""
        if not text:
            return None
        
        # Patterns pour trouver du JSON
        json_patterns = [
            r'```json\s*(\{.*?\})\s*```',  # Markdown code block
            r'```\s*(\{.*?\})\s*```',      # Code block sans 'json'
            r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',  # JSON simple
            r'(\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\])'  # Array JSON
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)
            for match in matches:
                try:
                    # Validation JSON
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue
        
        return None
    
    def create_cv_parsing_prompt(self, cv_text: str) -> str:
        """Génère un prompt optimisé pour parser un CV"""
        return f"""Tu es un expert en analyse de CV. Analyse le texte suivant et extrait toutes les informations dans un format JSON structuré.

TEXTE DU CV:
{cv_text}

INSTRUCTIONS:
1. Extrait TOUTES les informations disponibles
2. Respecte EXACTEMENT le format JSON ci-dessous
3. Si une information n'est pas disponible, utilise une liste vide [] ou une chaîne vide ""
4. Pour l'expérience, compte le nombre total d'années en additionnant toutes les expériences
5. Sois précis sur les compétences techniques et langues

FORMAT JSON REQUIS:
```json
{{
    "titre_candidat": "Titre ou poste recherché",
    "profil_resume": "Résumé professionnel ou objectif de carrière",
    "formations": [
        {{"diplome": "Nom du diplôme", "etablissement": "École/Université", "annee": 2020}}
    ],
    "experience_years": 5,
    "experience": [
        {{"poste": "Titre du poste", "entreprise": "Nom entreprise", "periode": "2020-2023", "missions": "Description des missions"}}
    ],
    "competences_techniques": ["Python", "Java", "React"],
    "competences_informatiques": ["Git", "Docker", "AWS"],
    "langues": [
        {{"langue": "français", "niveau": "C2"}},
        {{"langue": "anglais", "niveau": "B2"}}
    ],
    "certifications": ["Certification 1", "Certification 2"],
    "projets": [
        {{"nom": "Nom du projet", "description": "Description", "technologies": ["Tech1", "Tech2"]}}
    ],
    "soft_skills": ["Communication", "Leadership", "Travail en équipe"],
    "coordonnees": {{
        "email": "email@example.com",
        "telephone": "+33123456789",
        "localisation": "Ville, Pays"
    }}
}}
```

RÉPONDS UNIQUEMENT AVEC LE JSON, RIEN D'AUTRE."""
    
    def create_job_parsing_prompt(self, job_text: str) -> str:
        """Génère un prompt optimisé pour parser une offre d'emploi"""
        return f"""Tu es un expert en analyse d'offres d'emploi. Analyse le texte suivant et extrait toutes les informations dans un format JSON structuré.

TEXTE DE L'OFFRE:
{job_text}

INSTRUCTIONS:
1. Extrait TOUTES les informations disponibles
2. Respecte EXACTEMENT le format JSON ci-dessous
3. Si une information n'est pas disponible, utilise une liste vide [] ou une chaîne vide ""
4. Identifie clairement les compétences OBLIGATOIRES vs SOUHAITÉES
5. Sois précis sur les exigences de formation et d'expérience

FORMAT JSON REQUIS:
```json
{{
    "titre_poste": "Titre exact du poste",
    "entreprise": "Nom de l'entreprise",
    "localisation": "Ville, Région, Pays",
    "type_contrat": "CDI/CDD/Stage/Freelance",
    "salaire": "Fourchette salariale si mentionnée",
    "missions": "Description détaillée des missions et responsabilités",
    "environnement": "Description de l'environnement de travail",
    "exigences": {{
        "formation_requise": "Niveau de formation requis",
        "annees_experience": 3,
        "competences_obligatoires": ["Compétence 1 OBLIGATOIRE", "Compétence 2 REQUISE"],
        "competences_souhaitees": ["Compétence 1 souhaitée", "Compétence 2 appréciée"],
        "langues": ["français: C1", "anglais: B2"],
        "certifications": ["Certification requise 1", "Certification souhaitée 2"],
        "outils": ["Outil 1", "Logiciel 2", "Plateforme 3"],
        "qualites_humaines": ["Qualité 1", "Soft skill 2"]
    }},
    "avantages": ["Avantage 1", "Bénéfice 2"],
    "process_recrutement": "Description du processus si mentionné",
    "date_publication": "Date de publication si trouvée",
    "secteur": "Secteur d'activité"
}}
```

RÉPONDS UNIQUEMENT AVEC LE JSON, RIEN D'AUTRE."""
    
    def parse_cv_text(self, cv_text: str) -> Dict:
        """
        Parse un texte de CV et retourne un dictionnaire structuré
        
        Args:
            cv_text: Texte brut du CV
            
        Returns:
            Dict: CV structuré ou erreur
        """
        if not cv_text or len(cv_text.strip()) < 50:
            return {"error": "Texte de CV trop court ou vide"}
        
        prompt = self.create_cv_parsing_prompt(cv_text)
        response = self.invoke_with_json_validation(prompt, temperature=0.1)
        
        if not response.success:
            self.logger.error(f"Erreur parsing CV: {response.error}")
            return {"error": f"Échec du parsing: {response.error}"}
        
        try:
            cv_data = json.loads(response.content)
            cv_data["_metadata"] = {
                "parsing_time": response.execution_time,
                "tokens_used": response.tokens_used,
                "model_used": response.model_used,
                "confidence": self._calculate_parsing_confidence(cv_data)
            }
            return cv_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON invalide reçu: {str(e)}")
            return {"error": f"JSON invalide: {str(e)}"}
    
    def parse_job_text(self, job_text: str) -> Dict:
        """
        Parse un texte d'offre d'emploi et retourne un dictionnaire structuré
        
        Args:
            job_text: Texte brut de l'offre
            
        Returns:
            Dict: Offre structurée ou erreur
        """
        if not job_text or len(job_text.strip()) < 50:
            return {"error": "Texte d'offre trop court ou vide"}
        
        prompt = self.create_job_parsing_prompt(job_text)
        response = self.invoke_with_json_validation(prompt, temperature=0.1)
        
        if not response.success:
            self.logger.error(f"Erreur parsing offre: {response.error}")
            return {"error": f"Échec du parsing: {response.error}"}
        
        try:
            job_data = json.loads(response.content)
            job_data["_metadata"] = {
                "parsing_time": response.execution_time,
                "tokens_used": response.tokens_used,
                "model_used": response.model_used,
                "confidence": self._calculate_parsing_confidence(job_data)
            }
            return job_data
            
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON invalide reçu: {str(e)}")
            return {"error": f"JSON invalide: {str(e)}"}
    
    def _calculate_parsing_confidence(self, parsed_data: Dict) -> float:
        """Calcule un score de confiance du parsing (0-1)"""
        if not parsed_data or "error" in parsed_data:
            return 0.0
        
        confidence_factors = []
        
        # Vérification des champs obligatoires
        if "titre_poste" in parsed_data or "titre_candidat" in parsed_data:
            title = parsed_data.get("titre_poste", parsed_data.get("titre_candidat", ""))
            confidence_factors.append(1.0 if len(title.strip()) > 5 else 0.5)
        
        # Vérification de la richesse des données
        non_empty_fields = 0
        total_fields = 0
        
        for key, value in parsed_data.items():
            if key.startswith("_"):  # Skip metadata
                continue
                
            total_fields += 1
            if isinstance(value, str) and len(value.strip()) > 0:
                non_empty_fields += 1
            elif isinstance(value, list) and len(value) > 0:
                non_empty_fields += 1
            elif isinstance(value, dict) and any(v for v in value.values() if v):
                non_empty_fields += 1
            elif isinstance(value, (int, float)) and value > 0:
                non_empty_fields += 1
        
        completeness_score = non_empty_fields / total_fields if total_fields > 0 else 0
        confidence_factors.append(completeness_score)
        
        # Score final
        return sum(confidence_factors) / len(confidence_factors) if confidence_factors else 0.0
    
    def batch_parse_cvs(self, cv_texts: List[str]) -> List[Dict]:
        """Parse multiple CVs en lot"""
        results = []
        total = len(cv_texts)
        
        for i, cv_text in enumerate(cv_texts):
            self.logger.info(f"Parsing CV {i+1}/{total}")
            result = self.parse_cv_text(cv_text)
            result["_batch_index"] = i
            results.append(result)
            
            # Petite pause pour éviter la surcharge
            time.sleep(0.5)
        
        return results
    
    def batch_parse_jobs(self, job_texts: List[str]) -> List[Dict]:
        """Parse multiple offres en lot"""
        results = []
        total = len(job_texts)
        
        for i, job_text in enumerate(job_texts):
            self.logger.info(f"Parsing offre {i+1}/{total}")
            result = self.parse_job_text(job_text)
            result["_batch_index"] = i
            results.append(result)
            
            # Petite pause pour éviter la surcharge
            time.sleep(0.5)
        
        return results
    
    def get_stats(self) -> Dict:
        """Retourne les statistiques d'utilisation"""
        stats = self.stats.copy()
        stats["success_rate"] = (
            self.stats["successful_requests"] / self.stats["total_requests"] * 100
            if self.stats["total_requests"] > 0 else 0
        )
        stats["average_tokens_per_request"] = (
            self.stats["total_tokens"] / self.stats["successful_requests"]
            if self.stats["successful_requests"] > 0 else 0
        )
        return stats
    
    def reset_stats(self):
        """Remet à zéro les statistiques"""
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_time": 0.0,
            "average_response_time": 0.0
        }
    
    def health_check(self) -> Dict:
        """Vérifie l'état de santé du client"""
        try:
            start_time = time.time()
            test_response = self.invoke("Test de santé: réponds juste 'OK'")
            response_time = time.time() - start_time
            
            if test_response.success and "ok" in test_response.content.lower():
                return {
                    "status": "healthy",
                    "response_time": response_time,
                    "model": self.model_name,
                    "base_url": self.base_url
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": test_response.error or "Réponse inattendue",
                    "response_time": response_time
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "response_time": None
            }
    
    def update_temperature(self, new_temperature: float):
        """Met à jour la température du modèle"""
        if 0.0 <= new_temperature <= 2.0:
            self.temperature = new_temperature
            self.llm.temperature = new_temperature
            self.logger.info(f"Température mise à jour: {new_temperature}")
        else:
            raise ValueError("La température doit être entre 0.0 et 2.0")

# Fonction utilitaire pour usage simple
def quick_parse_cv(cv_text: str, model_name: str = "gemma2:9b") -> Dict:
    """Parse rapide d'un CV"""
    client = GemmaClient(model_name=model_name)
    return client.parse_cv_text(cv_text)

def quick_parse_job(job_text: str, model_name: str = "gemma2:9b") -> Dict:
    """Parse rapide d'une offre"""
    client = GemmaClient(model_name=model_name)
    return client.parse_job_text(job_text)

# Test de la classe
if __name__ == "__main__":
    print("🤖 Test du client Gemma3...")
    
    try:
        # Initialisation
        client = GemmaClient(model_name="gemma2:9b")
        
        # Test de santé
        health = client.health_check()
        print(f"📊 État de santé: {health['status']}")
        
        if health["status"] == "healthy":
            # Test simple
            print("\n🧪 Test d'invocation simple...")
            response = client.invoke("Explique en une phrase ce qu'est l'intelligence artificielle.")
            
            if response.success:
                print(f"✅ Réponse reçue: {response.content[:100]}...")
                print(f"⏱️  Temps: {response.execution_time:.2f}s")
                print(f"🔤 Tokens estimés: {response.tokens_used}")
            else:
                print(f"❌ Échec: {response.error}")
            
            # Test parsing CV
            print("\n📄 Test parsing CV...")
            cv_exemple = """
            Jean Dupont
            Développeur Full Stack Senior
            
            Expérience:
            - 2020-2023: Lead Developer chez TechCorp
            - 2018-2020: Développeur Python chez StartupXYZ
            
            Formation:
            - 2018: Master Informatique, Université Paris-Saclay
            
            Compétences: Python, JavaScript, React, Docker, AWS
            Langues: Français (natif), Anglais (courant)
            """
            
            cv_result = client.parse_cv_text(cv_exemple)
            
            if "error" not in cv_result:
                print("✅ CV parsé avec succès!")
                print(f"📋 Titre: {cv_result.get('titre_candidat', 'N/A')}")
                print(f"🎓 Formations: {len(cv_result.get('formations', []))}")
                print(f"💼 Expériences: {len(cv_result.get('experience', []))}")
                print(f"🛠️  Compétences techniques: {len(cv_result.get('competences_techniques', []))}")
                print(f"🎯 Confiance: {cv_result.get('_metadata', {}).get('confidence', 0):.2f}")
            else:
                print(f"❌ Erreur parsing CV: {cv_result['error']}")
            
            # Statistiques
            print(f"\n📊 Statistiques:")
            stats = client.get_stats()
            print(f"   Requêtes totales: {stats['total_requests']}")
            print(f"   Taux de succès: {stats['success_rate']:.1f}%")
            print(f"   Temps moyen: {stats['average_response_time']:.2f}s")
            
        else:
            print(f"❌ Problème de santé: {health.get('error', 'Inconnu')}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {str(e)}")
        print("💡 Vérifiez qu'Ollama est lancé et que Gemma2 est installé:")
        print("   ollama pull gemma2:9b")
        print("   ollama serve")