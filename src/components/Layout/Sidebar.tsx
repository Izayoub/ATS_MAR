"use client"

import type React from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useAuth } from "../../contexts/AuthContext"
import { Button } from "../ui/button"
import { Home, Users, Briefcase, BarChart3, Settings, Bot, ChevronLeft, ChevronRight, Zap } from "lucide-react"

interface SidebarProps {
  isCollapsed: boolean
  onToggle: () => void
}

const Sidebar: React.FC<SidebarProps> = ({ isCollapsed, onToggle }) => {
  const { user } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

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
      id: "matching",
      label: "Matching",
      icon: <Zap className="w-5 h-5" />,
      path: "/matching1",
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
            onClick={onToggle}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400"
          >
            {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </Button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 overflow-y-auto">
          <div className="space-y-1">
            {menuItems.map((item) => (
              <Button
                key={item.id}
                variant={isActive(item.path) ? "default" : "ghost"}
                className={`w-full justify-start transition-all duration-200 ${isCollapsed ? "px-3" : "px-4"} ${
                  isActive(item.path)
                    ? "bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-md"
                    : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800"
                }`}
                onClick={() => handleNavigation(item.path)}
                title={isCollapsed ? item.label : undefined}
              >
                <div className={`flex items-center ${isCollapsed ? "" : "space-x-3"}`}>
                  <span className={isActive(item.path) ? "text-white" : "text-gray-500 dark:text-gray-400"}>
                    {item.icon}
                  </span>
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
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-md">
                <span className="text-white text-sm font-bold">{user?.username?.charAt(0).toUpperCase() || "U"}</span>
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  {user?.username || "Utilisateur"}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email || "user@example.com"}</p>
              </div>
            </div>
          </div>
        )}

        {/* Collapsed user avatar */}
        {isCollapsed && (
          <div className="p-3 border-t border-gray-200 dark:border-gray-700 flex justify-center">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center shadow-md">
              <span className="text-white text-sm font-bold">{user?.username?.charAt(0).toUpperCase() || "U"}</span>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}

export default Sidebar
