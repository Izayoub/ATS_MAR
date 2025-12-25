"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect } from "react"
import authService from "../services/authService"
import type { User } from "../types/api"

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (data: any) => Promise<void>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = async () => {
    try {
      // Check if token exists in localStorage
      const token = authService.getToken()
      if (token) {
        // Check if we have stored user data
        const storedUser = authService.getCurrentUser()
        if (storedUser) {
          // Set user immediately from localStorage to avoid flash
          setUser(storedUser)
        }
        
        try {
          // Try to get fresh user profile with the token
          const currentUser = await authService.getProfile()
          setUser(currentUser)
        } catch (error) {
          console.error("Token invalide ou expiré:", error)
          // Clear invalid auth data
          await authService.logout()
          setUser(null)
        }
      } else {
        // No token, user is not authenticated
        setUser(null)
      }
    } catch (error) {
      console.error("Erreur initialisation auth:", error)
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    try {
      setIsLoading(true)
      const response = await authService.login({ username, password })
      setUser(response.user)
    } catch (error) {
      console.error("Login error in context:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const register = async (data: any) => {
    try {
      setIsLoading(true)
      const response = await authService.register(data)
      setUser(response.user)
    } catch (error) {
      console.error("Registration error in context:", error)
      throw error
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      setIsLoading(true)
      await authService.logout()
    } catch (error) {
      console.error("Logout error:", error)
    } finally {
      setUser(null)
      setIsLoading(false)
    }
  }

  const refreshUser = async () => {
    try {
      if (!authService.getToken()) {
        setUser(null)
        return
      }
      
      const currentUser = await authService.getProfile()
      setUser(currentUser)
    } catch (error) {
      console.error("Erreur refresh user:", error)
      await logout()
    }
  }

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    register,
    logout,
    refreshUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}