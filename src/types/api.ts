// Types pour l'authentification
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  role_display: string
  company?: Company
  phone: string
  avatar?: string
}

export interface Company {
  id: number
  name: string
  description: string
  website: string
  logo?: string
  city: string
}

export interface AuthResponse {
  token: string
  user: User
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  first_name: string
  last_name: string
  email: string
  role: string
  company_name: string
  password: string
  confirm_password: string
  accept_terms: boolean
}
export interface MatchingWeights {
  technical_skills: number
  soft_skills: number
  experience: number
  education: number
}

// Configuration de matching par défaut
export const DEFAULT_MATCHING_WEIGHTS: MatchingWeights = {
  technical_skills: 0.35,
  soft_skills: 0.15,
  experience: 0.30,
  education: 0.20
}

// Types pour les offres d'emploi
export interface JobOffer {
  id: number
  title: string
  description: string
  requirements: string
  benefits: string
  status: "draft" | "active" | "paused" | "closed"
  experience_level: "junior" | "middle" | "senior"
  remote_allowed: boolean
  contract_type: string
  company: Company
  created_at: string
  updated_at: string
  deadline?: string
  applications_count: number
  ai_generated: boolean
  seo_optimized: boolean
  bias_checked: boolean
  
  // Nouveaux champs pour le matching personnalisé
  matching_weights?: MatchingWeights
  system_prompt?: string
  effective_matching_weights?: MatchingWeights
  effective_system_prompt?: string
  has_custom_matching?: boolean
}

export interface JobOfferCreate {
  title: string
  description: string
  requirements: string
  benefits: string
  status: "draft" | "active" | "paused" | "closed"
  experience_level: "junior" | "middle" | "senior"
  remote_allowed: boolean
  contract_type: string
  deadline: string | null
  
  // Nouveaux champs optionnels
  matching_weights?: MatchingWeights
  system_prompt?: string
}
export interface JobMatchingConfig {
  id: number
  title: string
  matching_weights?: MatchingWeights
  system_prompt?: string
  effective_weights: MatchingWeights
  weights_customized: boolean
  prompt_customized: boolean
}
export interface MatchingConfigResponse {
  success: boolean
  config: JobMatchingConfig
  default_weights: MatchingWeights
  message?: string
}

// Types pour les candidats
export interface Candidate {
  id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  gender: "M" | "F" | "N/A"
  birth_date: string | null
  address: string
  city: string
  linkedin_url: string
  cv_file: string | null
  cv_file_path: string // NOUVEAU CHAMP
  cv_text: string
  cv_parsed_data: Record<string, any>

  technical_skills: string[]
  soft_skills: string[]
  skills_extracted?: Record<string, any>

  experience_years: number | null
  education_level: string
  languages: string[]
  ai_summary: string
  status: "new" | "pending_extraction" | "reviewed" | "interviewed" | "hired" | "rejected" // Nouveau statut
  global_match_score: number | null
  last_matching_date: string | null
  
  // Nouveaux champs pour tracking extraction
  is_extracted: boolean
  extraction_date: string | null
  
  created_at: string
  updated_at: string
  full_name: string
  current_position: string
  skills_summary: {
    technical_count: number
    soft_count: number
    top_technical: string[]
  }
  experience_summary: {
    years: number
    level: string
  }
  application_count: number
}

export interface PendingCandidate {
  id: number
  full_name: string
  cv_file: string
  cv_file_path: string
  cv_file_url: string | null
  status: "pending_extraction" | "processing" | "failed"
  is_extracted: boolean
  upload_date: string
  created_at: string
}

// Nouveau type pour les réponses d'upload
export interface UploadResponse {
  success: boolean
  message?: string
  candidate?: {
    id: number
    cv_file_path: string
    cv_file_url: string | null
    status: string
    upload_date: string
  }
  error?: string
}

export interface CandidateNote {
  id: number
  content: string
  note_type: "note" | "interview" | "call" | "email"
  author: {
    id: number
    first_name: string
    last_name: string
    get_full_name: string
  }
  created_at: string
}
export interface TimelineEvent {
  id: string
  type: "application" | "review" | "interview" | "call" | "email" | "status_change"
  title: string
  description: string
  date: string
  author?: string
}

export interface JobMatch {
  job_id: number
  job_title: string
  company_name: string
  location: string
  contract_type: string
  salary_range: string
  overall_score: number
  recommendation: string
  breakdown: Record<
    string,
    {
      score: number
      confidence: number
    }
  >
}

export interface PaginatedResponse<T> {
  results: T[]
  count: number
  next: string | null // Changed from string | null
  previous: string | null // Changed from string | null
}

// Types pour les filtres
export interface JobFilters {
  status?: string
  experience_level?: string
  location?: string
  search?: string
  page?: number
  contract_type?: string
  salary_min?: number
  salary_max?: number
  remote_allowed?: boolean
}

export interface CandidateFilters {
  status?: string
  location?: string
  skills?: string[]
  search?: string
  job?: string
  page?: number
  page_size?: number
  group?: string;
  experience_level?: "junior" | "middle" | "senior" // Add this line
  experience_min?: number
  experience_max?: number
  is_active?: boolean
  is_favorite?: boolean
}
// Types pour les groupes
export interface CandidateGroup {
  id: number
  nom: string
  description: string
  type_groupe: "competence" | "experience" | "projet" | "pipeline" | "performance" | "geographic" | "custom"
  couleur: "blue" | "green" | "red" | "yellow" | "purple" | "orange" | "gray" | "teal"
  ordre_affichage: number
  is_active: boolean
  is_public: boolean
  candidats_count: number
  skills_distribution?: {
    technical: Record<string, number>
    soft: Record<string, number>
  }
  experience_distribution?: {
    min: number
    max: number
    avg: number
    distribution: {
      "0-2": number
      "3-5": number
      "6-10": number
      "10+": number
    }
  }
  created_by: {
    id: number
    first_name: string
    last_name: string
  }
  created_at: string
  updated_at: string
  last_sync?: string
}

export interface CandidateGroupCreate {
  nom: string
  description?: string
  type_groupe: CandidateGroup["type_groupe"]
  couleur: CandidateGroup["couleur"]
  ordre_affichage?: number
  is_active?: boolean
  is_public?: boolean
}

export interface CandidateGroupFilters {
  search?: string
  type_groupe?: string
  is_active?: boolean
  candidat_id?: number
  ordering?: string
  page?: number
}

export interface GroupAnalytics {
  total: number
  skills: {
    technical: Record<string, number>
    soft: Record<string, number>
  }
  experience: {
    min: number
    max: number
    avg: number
    distribution: Record<string, number>
  }
  status_distribution: Record<string, number>
  applications_count: number
  avg_match_score: number
  last_updated: string
  last_sync?: string
}

export interface BulkActionRequest {
  action: "activate" | "deactivate" | "delete" | "sync_all"
  groupe_ids: number[]
}

export interface BulkActionResponse {
  success: boolean
  action: string
  processed: number
  successful: number
  results: string[]
}
export interface BulkUploadResult {
  success: boolean;
  uploaded_count: number;
  error_count: number;
  results: Array<{
    candidate_id: number;
    filename: string;
    cv_file_url: string;
    status: string;
  }>;
  errors: string[];
}