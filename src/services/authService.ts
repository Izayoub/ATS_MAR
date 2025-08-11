import apiClient from './apiClient'
import { API_ENDPOINTS } from '../config/api'
import type { AuthResponse, LoginRequest, RegisterRequest, User } from '../types/api'

class AuthService {
  // Connexion utilisateur
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.LOGIN, credentials)
      
      // Django DRF peut renvoyer directement les données ou dans response.data
      const data = response.data
      
      if (data.token) {
        localStorage.setItem('authToken', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return data
      } else {
        throw new Error('Token non reçu du serveur')
      }
    } catch (error: any) {
      console.error('Erreur login:', error)
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        error.message || 
        'Erreur de connexion'
      )
    }
  }

  // Inscription utilisateur
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await apiClient.post(API_ENDPOINTS.REGISTER, userData)
      
      const data = response.data
      
      if (data.token) {
        localStorage.setItem('authToken', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return data
      } else {
        throw new Error('Token non reçu du serveur')
      }
    } catch (error: any) {
      console.error('Erreur register:', error)
      
      // Gestion des erreurs de validation Django
      if (error.response?.data) {
        const errorData = error.response.data
        if (typeof errorData === 'object') {
          const errorMessages = Object.values(errorData).flat().join(', ')
          throw new Error(errorMessages)
        }
      }
      
      throw new Error(
        error.response?.data?.error || 
        error.response?.data?.detail || 
        error.message || 
        'Erreur d\'inscription'
      )
    }
  }

  // Déconnexion
  async logout(): Promise<void> {
    try {
      await apiClient.post(API_ENDPOINTS.LOGOUT)
    } catch (error) {
      console.error('Erreur lors de la déconnexion:', error)
    } finally {
      localStorage.removeItem('authToken')
      localStorage.removeItem('user')
    }
  }

  // Récupérer le profil utilisateur
  async getProfile(): Promise<User> {
    try {
      const response = await apiClient.get(API_ENDPOINTS.USER_PROFILE)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.error || 'Erreur de récupération du profil')
    }
  }

  // Vérifier si l'utilisateur est connecté
  isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken')
  }

  // Récupérer l'utilisateur depuis le localStorage
  getCurrentUser(): User | null {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }

  // Récupérer le token d'authentification
  getAuthToken(): string | null {
    return localStorage.getItem('authToken')
  }
}

export default new AuthService()
