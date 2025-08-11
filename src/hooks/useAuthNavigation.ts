
import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export const useAuthNavigation = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { isAuthenticated, user } = useAuth()

  // Rediriger après connexion réussie
  const redirectAfterLogin = () => {
    const from = location.state?.from?.pathname || '/dashboard'
    navigate(from, { replace: true })
  }

  // Rediriger vers login si déconnecté
  const redirectToLogin = () => {
    navigate('/login', { replace: true })
  }

  // Rediriger vers dashboard après inscription
  const redirectAfterRegister = () => {
    navigate('/dashboard', { replace: true })
  }

  return {
    redirectAfterLogin,
    redirectToLogin,
    redirectAfterRegister,
    isAuthenticated,
    user
  }
}