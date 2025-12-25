import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export const useAuthNavigation = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated, user } = useAuth()

  // Get the page user was trying to access before login
  const getIntendedDestination = () => {
    const from = location.state?.from?.pathname
    
    // Don't redirect to auth pages
    if (from && !from.startsWith('/login') && !from.startsWith('/register')) {
      return from
    }
    
    return '/dashboard'
  }

  // Redirect after successful login
  const redirectAfterLogin = () => {
    const destination = getIntendedDestination()
    navigate(destination, { replace: true })
  }

  // Redirect to login if not authenticated
  const redirectToLogin = (from?: string) => {
    const state = from ? { from: { pathname: from } } : { from: location }
    navigate('/login', { state, replace: true })
  }

  // Redirect after successful registration
  const redirectAfterRegister = () => {
    navigate('/dashboard', { replace: true })
  }

  // Check if current route requires authentication
  const isProtectedRoute = (pathname: string) => {
    const publicRoutes = ['/', '/login', '/register', '/about', '/contact', '/pricing']
    return !publicRoutes.includes(pathname)
  }

  return {
    redirectAfterLogin,
    redirectToLogin,
    redirectAfterRegister,
    getIntendedDestination,
    isProtectedRoute,
    isAuthenticated,
    user
  }
}