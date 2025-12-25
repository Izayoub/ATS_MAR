// Configuration de l'API
const getApiUrl = (): string => {
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    return "http://localhost:8000"
  }
  return ""
}

export const API_BASE_URL = getApiUrl()

export const API_ENDPOINTS = {
  // Auth
  LOGIN: "/api/auth/login/",
  REGISTER: "/api/auth/register/",
  LOGOUT: "/api/auth/logout/",
  USER_PROFILE: "/api/auth/user/",

  // Jobs
  JOBS: "/recruitment/jobs/",
  JOB_DETAIL: (id: number) => `/recruitment/jobs/${id}/`,
  JOB_QUESTIONS: (id: number) => `/recruitment/jobs/${id}/generate_questions/`,
  JOB_MATCHING: (jobId: number) => `/recruitment/jobs/${jobId}/matching/`,
  // Candidates
  CANDIDATES: '/api/recruitment/candidates/',
  CANDIDATE_DETAIL: (id: number) => `/api/recruitment/candidates/${id}/`,
  CANDIDATE_NOTES: (id: number) => `/api/recruitment/candidates/${id}/notes/`,
  CANDIDATE_TIMELINE: (id: number) => `/api/recruitment/candidates/${id}/timeline/`,
  CANDIDATE_MATCHING: (id: number) => `/api/recruitment/candidates/${id}/matching/`,
  CANDIDATE_GROUPS: "/api/recruitment/candidate-groups/",
  CANDIDATE_GROUP_DETAIL: (id: number) => `/api/recruitment/candidate-groups/${id}/`,
  CANDIDATE_GROUP_ANALYTICS: (id: number) => `/api/recruitment/candidate-groups/${id}/analytics/`,
  CANDIDATE_GROUP_ADD_CANDIDATES: (id: number) => `/api/recruitment/candidate-groups/${id}/add_candidats/`,
  CANDIDATE_GROUP_REMOVE_CANDIDATES: (id: number) => `/api/recruitment/candidate-groups/${id}/remove_candidats/`,
  CANDIDATE_GROUP_SYNC: (id: number) => `/api/recruitment/candidate-groups/${id}/sync_auto_criteria/`,
  CANDIDATE_GROUPS_BULK: "/api/recruitment/candidate-groups/bulk_actions/",
  CANDIDATE_GROUPS_SUMMARY: "/api/recruitment/candidate-groups/list_summary/",
  CANDIDATE_UPLOAD_CV: "/api/recruitment/upload-cv/",
  CANDIDATE_BULK_UPLOAD: "/api/recruitment/bulk-upload/", 
  CANDIDATE_PENDING_EXTRACTION: "/api/recruitment/pending-extraction/",
  CANDIDATE_EXTRACT_DATA: (id: number) => `/api/recruitment/candidates/${id}/extract/`,

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
