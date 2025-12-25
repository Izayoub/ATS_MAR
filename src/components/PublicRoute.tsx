"use client"

import type React from "react"
import type { ReactNode } from "react"
import { Navigate } from "react-router-dom"
import { useAuth } from "../contexts/AuthContext"

interface PublicRouteProps {
  children: ReactNode
  redirectTo?: string
}

const PublicRoute: React.FC<PublicRouteProps> = ({ 
  children, 
  redirectTo = "/dashboard" 
}) => {
  const { isAuthenticated, isLoading } = useAuth()

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Chargement...</p>
        </div>
      </div>
    )
  }

  // Redirect to dashboard if already authenticated
  if (isAuthenticated) {
    return <Navigate to={redirectTo} replace />
  }

  // Render the public component if not authenticated
  return <>{children}</>
}

export default PublicRoute