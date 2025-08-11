"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect, type ReactNode } from "react"
import  authService  from "../services/authService"
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

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    initializeAuth()
  }, [])

  const initializeAuth = async () => {
    try {
      if (authService.isAuthenticated()) {
        const storedUser = authService.getCurrentUser()
        if (storedUser) {
          setUser(storedUser)
          // Optionnel: vérifier que le token est toujours valide
          try {
            const currentUser = await authService.getCurrentUser()
            setUser(currentUser)
            localStorage.setItem("user", JSON.stringify(currentUser))
          } catch (error) {
            console.error("Token invalide:", error)
            await logout()
          }
        }
      }
    } catch (error) {
      console.error("Erreur initialisation auth:", error)
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const response = await authService.login({ username, password })
      setUser(response.user)
    } catch (error) {
      throw error
    }
  }

  const register = async (data: any) => {
    try {
      const response = await authService.register(data)
      setUser(response.user)
    } catch (error) {
      throw error
    }
  }

  const logout = async () => {
    try {
      await authService.logout()
    } catch (error) {
      console.error("Erreur logout:", error)
    } finally {
      setUser(null)
    }
  }

  const refreshUser = async () => {
    try {
      const currentUser = await authService.getCurrentUser()
      setUser(currentUser)
      localStorage.setItem("user", JSON.stringify(currentUser))
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

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
