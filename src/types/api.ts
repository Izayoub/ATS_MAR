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

// Types pour les offres d'emploi
export interface JobOffer {
  id: number
  title: string
  description: string
  requirements: string
  benefits: string
  status: "draft" | "active" | "paused" | "closed"
  experience_level: "junior" | "middle" | "senior"
  salary_min?: number
  salary_max?: number
  location: string
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
}

export interface JobOfferCreate {
  title: string
  description: string
  requirements: string
  benefits: string
  status: 'draft' | 'active' | 'paused' | 'closed'
  experience_level: 'junior' | 'middle' | 'senior'
  salary_min: number | null
  salary_max: number | null
  location: string
  remote_allowed: boolean
  contract_type: string
  deadline: string | null
}

// Types pour les candidats
export interface Candidate {
  id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  gender?: "M" | "F"
  birth_date?: string
  address: string
  city: string
  linkedin_url: string
  cv_file?: string
  cv_text: string
  cv_parsed_data: any
  skills_extracted: string[]
  experience_years?: number
  education_level: string
  languages: string[]
  ai_summary: string
  created_at: string
  updated_at: string
  skills_display: string[]
}

// Types pour les candidatures
export interface Application {
  id: number
  job_offer: JobOffer
  candidate: Candidate
  status: "received" | "screening" | "interview" | "tests" | "final" | "accepted" | "rejected" | "withdrawn"
  status_display: string
  cover_letter: string
  ai_match_score?: number
  cultural_fit_score?: number
  applied_at: string
  last_updated: string
  source: string
}

// Types pour les entretiens
export interface Interview {
  id: number
  application: Application
  interview_type: "phone" | "video" | "in_person" | "ai_screening"
  scheduled_at: string
  duration_minutes: number
  interviewer_name: string
  questions: string[]
  notes: string
  ai_evaluation: any
  completed_at?: string
}

// Types pour les réponses API
export interface ApiResponse<T = any> {
  success?: boolean
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  count: number
  next?: string
  previous?: string
  results: T[]
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
  city?: string
  experience_years?: number
  skills?: string
  search?: string
  page?: number
}
