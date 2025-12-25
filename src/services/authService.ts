import { API_BASE_URL, API_ENDPOINTS } from '../config/api'
import type { AuthResponse, LoginRequest, User } from '../types/api'

class AuthService {
  private readonly TOKEN_KEY = 'auth_token'
  private readonly USER_KEY = 'user'

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem(this.TOKEN_KEY)
  }

  // Get current user from localStorage
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem(this.USER_KEY)
    return userStr ? JSON.parse(userStr) : null
  }

  // Get token from localStorage
  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY)
  }

  // Set authentication data
  private setAuthData(token: string, user: User): void {
    localStorage.setItem(this.TOKEN_KEY, token)
    localStorage.setItem(this.USER_KEY, JSON.stringify(user))
  }

  // Clear authentication data
  private clearAuthData(): void {
    localStorage.removeItem(this.TOKEN_KEY)
    localStorage.removeItem(this.USER_KEY)
  }

  // Login user
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.LOGIN}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Login failed')
      }

      const data: AuthResponse = await response.json()
      this.setAuthData(data.token, data.user)
      
      return data
    } catch (error) {
      throw error
    }
  }

  // Register user
  async register(userData: any): Promise<AuthResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.REGISTER}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      })

      if (!response.ok) {
        const errorData = await response.json()
        // Handle different error response formats
        if (errorData.errors) {
          // Django REST framework error format
          const error = new Error('Registration failed')
          ;(error as any).response = { data: errorData }
          throw error
        } else if (errorData.error) {
          throw new Error(errorData.error)
        } else {
          throw new Error('Registration failed')
        }
      }

      const data: AuthResponse = await response.json()
      
      // Check if we have both token and user in the response
      if (data.token && data.user) {
        this.setAuthData(data.token, data.user)
      } else if (data.token) {
        // If we only have a token, we might need to fetch user data separately
        localStorage.setItem(this.TOKEN_KEY, data.token)
        const user = await this.getProfile()
        this.setAuthData(data.token, user)
        return { token: data.token, user }
      } else {
        throw new Error('Invalid response structure')
      }
      
      return data
    } catch (error) {
      throw error
    }
  }

  // Get user profile
  async getProfile(): Promise<User> {
    const token = this.getToken()
    if (!token) {
      throw new Error('No token available')
    }

    try {
      const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.USER_PROFILE}`, {
        method: 'GET',
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json',
        },
      })

      if (!response.ok) {
        if (response.status === 401) {
          this.clearAuthData()
          throw new Error('Token expired')
        }
        throw new Error('Failed to fetch profile')
      }

      const user: User = await response.json()
      localStorage.setItem(this.USER_KEY, JSON.stringify(user))
      
      return user
    } catch (error) {
      throw error
    }
  }

  // Logout user
  async logout(): Promise<void> {
    const token = this.getToken()
    
    if (token) {
      try {
        await fetch(`${API_BASE_URL}${API_ENDPOINTS.LOGOUT}`, {
          method: 'POST',
          headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
          },
        })
      } catch (error) {
        console.error('Logout error:', error)
        // Continue with local cleanup even if server request fails
      }
    }
    
    this.clearAuthData()
  }

  // Make authenticated API request
  async authenticatedRequest(url: string, options: RequestInit = {}): Promise<Response> {
    const token = this.getToken()
    
    if (!token) {
      throw new Error('No authentication token')
    }

    const headers = {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    }

    const response = await fetch(`${API_BASE_URL}${url}`, {
      ...options,
      headers,
    })

    if (response.status === 401) {
      this.clearAuthData()
      throw new Error('Token expired')
    }

    return response
  }
}

const authService = new AuthService()
export default authService