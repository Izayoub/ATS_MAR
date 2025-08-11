// Configuration de l'API
const getApiUrl = (): string => {
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return "http://localhost:8000/api"
  }
  return "/api"
}

export const API_BASE_URL = getApiUrl()

export const API_ENDPOINTS = {
  // Auth
  LOGIN: "/auth/login/",
  REGISTER: "/auth/register/",
  LOGOUT: "/auth/logout/",
  USER_PROFILE: "/auth/user/",

  // Jobs
  JOBS: "/recruitment/jobs/",
  JOB_DETAIL: (id: number) => `/recruitment/jobs/${id}/`,
  JOB_QUESTIONS: (id: number) => `/recruitment/jobs/${id}/generate_questions/`,
  JOB_MATCHING: (id: number) => `/recruitment/jobs/${id}/matching_candidates/`,

  // Candidates
  CANDIDATES: "/recruitment/candidates/",
  CANDIDATE_DETAIL: (id: number) => `/recruitment/candidates/${id}/`,
  CANDIDATE_UPLOAD: "/recruitment/candidates/upload_cv/",
  CANDIDATE_REPARSE: (id: number) => `/recruitment/candidates/${id}/reparse_cv/`,

  // Applications
  APPLICATIONS: "/recruitment/applications/",
  APPLICATION_CREATE: "/recruitment/applications/create_application/",
  APPLICATION_STATUS: (id: number) => `/recruitment/applications/${id}/update_status/`,
  PIPELINE_STATS: "/recruitment/applications/pipeline_stats/",

  // Interviews
  INTERVIEWS: "/recruitment/interviews/",
  INTERVIEW_EVALUATION: (id: number) => `/recruitment/interviews/${id}/generate_evaluation/`,

  // AI
  AI_PROCESSING: "/ai/processing/",
}
