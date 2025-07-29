"use client"

import type React from "react"
import { useState } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../../contexts/AuthContext"
import { Button } from "../ui/button"
import { Home, Users, Briefcase, BarChart3, Settings, Bot, ChevronLeft, ChevronRight } from "lucide-react"

const Sidebar: React.FC = () => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const menuItems = [
    {
      id: "dashboard",
      label: "Tableau de bord",
      icon: <Home className="w-5 h-5" />,
      path: "/dashboard",
    },
    {
      id: "jobs",
      label: "Offres d'emploi",
      icon: <Briefcase className="w-5 h-5" />,
      path: "/jobs",
    },
    {
      id: "candidates",
      label: "Candidats",
      icon: <Users className="w-5 h-5" />,
      path: "/candidates",
    },
    {
      id: "ai-assistant",
      label: "Assistant IA",
      icon: <Bot className="w-5 h-5" />,
      path: "/ai-assistant",
    },
    {
      id: "analytics",
      label: "Analyses",
      icon: <BarChart3 className="w-5 h-5" />,
      path: "/analytics",
    },
    {
      id: "settings",
      label: "Paramètres",
      icon: <Settings className="w-5 h-5" />,
      path: "/settings",
    },
  ]

  const isActive = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path + "/")
  }

  const handleNavigation = (path: string) => {
    navigate(path)
  }

  return (
    <aside
      className={`fixed left-0 top-16 h-[calc(100vh-4rem)] bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 z-40 ${
        isCollapsed ? "w-16" : "w-64"
      }`}
    >
      <div className="flex flex-col h-full">
        {/* Toggle button */}
        <div className="flex justify-end p-2 border-b border-gray-200 dark:border-gray-700">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4">
          <div className="space-y-2">
            {menuItems.map((item) => (
              <Button
                key={item.id}
                variant={isActive(item.path) ? "default" : "ghost"}
                className={`w-full justify-start transition-colors duration-200 ${isCollapsed ? "px-2" : "px-4"} ${
                  isActive(item.path)
                    ? "bg-blue-600 text-white hover:bg-blue-700"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
                onClick={() => handleNavigation(item.path)}
                title={isCollapsed ? item.label : undefined}
              >
                <div className="flex items-center space-x-3">
                  {item.icon}
                  {!isCollapsed && <span className="text-sm font-medium">{item.label}</span>}
                </div>
              </Button>
            ))}
          </div>
        </nav>

        {/* User info */}
        {!isCollapsed && (
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">{user?.name?.charAt(0).toUpperCase() || "U"}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user?.name || "Utilisateur"}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email || "user@example.com"}</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}

export default Sidebar
