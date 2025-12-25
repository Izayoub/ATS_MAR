// Fixed apiClient.ts
import { API_BASE_URL } from "../config/api"

class ApiClient {
private readonly TOKEN_KEY = "auth_token"

// Get token from localStorage
private getToken(): string | null {
if (typeof window === "undefined") return null
return localStorage.getItem(this.TOKEN_KEY)
}

// Get default headers with authentication (FIXED: Don't include Content-Type for FormData)
private getHeaders(includeAuth = true, isFormData = false): HeadersInit {
const headers: HeadersInit = {}

// CRITICAL FIX: Only set Content-Type for JSON, not for FormData
if (!isFormData) {
headers["Content-Type"] = "application/json"
}

if (includeAuth) {
const token = this.getToken()
if (token) {
headers["Authorization"] = `Token ${token}`
}
}

return headers
}

// Generic request method (FIXED: Handle FormData properly)
private async request<T>(endpoint: string, options: RequestInit = {}, includeAuth = true): Promise<T> {
const url = `${API_BASE_URL}${endpoint}`

// CRITICAL FIX: Detect if body is FormData
const isFormData = options.body instanceof FormData

const config: RequestInit = {
...options,
headers: {
...this.getHeaders(includeAuth, isFormData),
...options.headers,
},
}

try {
const response = await fetch(url, config)

// Handle authentication errors
if (response.status === 401) {
if (typeof window !== "undefined") {
localStorage.removeItem(this.TOKEN_KEY)
localStorage.removeItem("user")

if (!window.location.pathname.includes("/login")) {
window.location.href = "/login"
}
}
throw new Error("Token expired or invalid")
}

// Handle other HTTP errors
if (!response.ok) {
const errorData = await response.json().catch(() => null)
throw new Error(errorData?.message || errorData?.error || `HTTP ${response.status}`)
}

// Handle empty responses (like 204 No Content)
if (response.status === 204) {
return {} as T
}

const data = await response.json()
return data
} catch (error) {
console.error(`API Error for ${endpoint}:`, error)
throw error
}
}

// GET request
async get<T>(endpoint: string, includeAuth = true): Promise<T> {
return this.request<T>(endpoint, { method: "GET" }, includeAuth)
}

// POST request (FIXED: Handle both JSON and FormData)
async post<T>(endpoint: string, data?: any, includeAuth = true): Promise<T> {
let body: any

if (data instanceof FormData) {
// FormData - pass as-is
body = data
} else if (data !== undefined) {
// JSON - stringify
body = JSON.stringify(data)
}

return this.request<T>(
endpoint,
{
method: "POST",
body,
},
includeAuth,
)
}

// PUT request
async put<T>(endpoint: string, data?: any, includeAuth = true): Promise<T> {
let body: any

if (data instanceof FormData) {
body = data
} else if (data !== undefined) {
body = JSON.stringify(data)
}

return this.request<T>(
endpoint,
{
method: "PUT",
body,
},
includeAuth,
)
}

// PATCH request
async patch<T>(endpoint: string, data?: any, includeAuth = true): Promise<T> {
let body: any

if (data instanceof FormData) {
body = data
} else if (data !== undefined) {
body = JSON.stringify(data)
}

return this.request<T>(
endpoint,
{
method: "PATCH",
body,
},
includeAuth,
)
}

// DELETE request
async delete<T>(endpoint: string, includeAuth = true): Promise<T> {
return this.request<T>(endpoint, { method: "DELETE" }, includeAuth)
}

// REMOVED: uploadFile method is now redundant since post() handles FormData
}

const apiClient = new ApiClient()
export { apiClient }
export default apiClient