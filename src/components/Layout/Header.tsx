"use client"

import type React from "react"
import { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../../contexts/AuthContext"
import { useTheme } from "../../contexts/ThemeContext"
import { Button } from "../ui/button"
import { Bell, Search, Settings, User, LogOut, Sun, Moon, Monitor, ChevronDown } from "lucide-react"

const Header: React.FC = () => {
  const { user, logout } = useAuth()
  const { theme, setTheme, actualTheme } = useTheme()
  const navigate = useNavigate()
  const location = useLocation()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showThemeMenu, setShowThemeMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)

  const handleLogout = () => {
    logout()
    navigate("/login")
  }

  const getThemeIcon = () => {
    switch (theme) {
      case "light":
        return <Sun className="w-4 h-4" />
      case "dark":
        return <Moon className="w-4 h-4" />
      case "system":
        return <Monitor className="w-4 h-4" />
      default:
        return <Sun className="w-4 h-4" />
    }
  }

  const getThemeLabel = () => {
    switch (theme) {
      case "light":
        return "Clair"
      case "dark":
        return "Sombre"
      case "system":
        return "Système"
      default:
        return "Clair"
    }
  }

  const notifications = [
    {
      id: 1,
      title: "Nouvelle candidature",
      message: "Ahmed Benali a postulé pour le poste de Développeur React",
      time: "Il y a 5 min",
      unread: true,
    },
    {
      id: 2,
      title: "Entretien programmé",
      message: "Entretien avec Sarah Alami prévu demain à 14h",
      time: "Il y a 1h",
      unread: true,
    },
    {
      id: 3,
      title: "Offre expirée",
      message: "L'offre 'Chef de projet IT' expire dans 2 jours",
      time: "Il y a 3h",
      unread: false,
    },
  ]

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 shadow-sm">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Logo et titre */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">TA</span>
            </div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">TalentAI Maroc</h1>
          </div>
        </div>

        {/* Barre de recherche */}
        <div className="flex-1 max-w-2xl mx-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Rechercher des candidats, offres d'emploi..."
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>

        {/* Actions de droite */}
        <div className="flex items-center space-x-4">
          {/* Sélecteur de thème */}
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowThemeMenu(!showThemeMenu)}
              className="flex items-center space-x-2 px-3 py-2"
            >
              {getThemeIcon()}
              <span className="hidden md:inline text-sm">{getThemeLabel()}</span>
              <ChevronDown className="w-3 h-3" />
            </Button>

            {showThemeMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                <button
                  onClick={() => {
                    setTheme("light")
                    setShowThemeMenu(false)
                  }}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-3 ${
                    theme === "light" ? "bg-gray-100 dark:bg-gray-700" : ""
                  }`}
                >
                  <Sun className="w-4 h-4" />
                  <span className="text-gray-900 dark:text-white">Clair</span>
                </button>
                <button
                  onClick={() => {
                    setTheme("dark")
                    setShowThemeMenu(false)
                  }}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-3 ${
                    theme === "dark" ? "bg-gray-100 dark:bg-gray-700" : ""
                  }`}
                >
                  <Moon className="w-4 h-4" />
                  <span className="text-gray-900 dark:text-white">Sombre</span>
                </button>
                <button
                  onClick={() => {
                    setTheme("system")
                    setShowThemeMenu(false)
                  }}
                  className={`w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-3 ${
                    theme === "system" ? "bg-gray-100 dark:bg-gray-700" : ""
                  }`}
                >
                  <Monitor className="w-4 h-4" />
                  <span className="text-gray-900 dark:text-white">Système</span>
                </button>
              </div>
            )}
          </div>

          {/* Notifications */}
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2"
            >
              <Bell className="w-5 h-5" />
              <span className="absolute -top-1 -right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
                2
              </span>
            </Button>

            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-2 z-50">
                <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                  <h3 className="font-semibold text-gray-900 dark:text-white">Notifications</h3>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {notifications.map((notification) => (
                    <div
                      key={notification.id}
                      className={`px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer ${
                        notification.unread ? "bg-blue-50 dark:bg-blue-900/20" : ""
                      }`}
                    >
                      <div className="flex items-start space-x-3">
                        <div
                          className={`w-2 h-2 rounded-full mt-2 ${notification.unread ? "bg-blue-500" : "bg-gray-300"}`}
                        />
                        <div className="flex-1">
                          <p className="font-medium text-sm text-gray-900 dark:text-white">{notification.title}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">{notification.message}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{notification.time}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700">
                  <Button variant="ghost" size="sm" className="w-full text-sm">
                    Voir toutes les notifications
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Menu utilisateur */}
          <div className="relative">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center space-x-2 px-3 py-2"
            >
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <User className="w-4 h-4 text-white" />
              </div>
              <div className="hidden md:block text-left">
                <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.name || "Utilisateur"}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{user?.email || "user@example.com"}</p>
              </div>
              <ChevronDown className="w-3 h-3" />
            </Button>

            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                <div className="px-4 py-3 border-b border-gray-200 dark:border-gray-700">
                  <p className="font-medium text-gray-900 dark:text-white">{user?.name || "Utilisateur"}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{user?.email || "user@example.com"}</p>
                </div>
                <button
                  onClick={() => {
                    navigate("/settings")
                    setShowUserMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-3"
                >
                  <Settings className="w-4 h-4" />
                  <span className="text-gray-900 dark:text-white">Paramètres</span>
                </button>
                <button
                  onClick={() => {
                    navigate("/settings")
                    setShowUserMenu(false)
                  }}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-3"
                >
                  <User className="w-4 h-4" />
                  <span className="text-gray-900 dark:text-white">Mon profil</span>
                </button>
                <div className="border-t border-gray-200 dark:border-gray-700 my-1"></div>
                <button
                  onClick={handleLogout}
                  className="w-full px-4 py-2 text-left text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center space-x-3 text-red-600 dark:text-red-400"
                >
                  <LogOut className="w-4 h-4" />
                  <span>Se déconnecter</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Fermer les menus en cliquant à l'extérieur */}
      {(showUserMenu || showThemeMenu || showNotifications) && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => {
            setShowUserMenu(false)
            setShowThemeMenu(false)
            setShowNotifications(false)
          }}
        />
      )}
    </header>
  )
}

export default Header
