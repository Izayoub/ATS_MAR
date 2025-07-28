import type React from "react"
import { Link, useLocation } from "react-router-dom"
import {
  LayoutDashboard,
  Briefcase,
  Users,
  BarChart3,
  Settings,
  Brain,
  MessageSquare,
  FileText,
  Calendar,
} from "lucide-react"

const Sidebar: React.FC = () => {
  const location = useLocation()

  const menuItems = [
    {
      name: "Dashboard",
      href: "/dashboard",
      icon: LayoutDashboard,
      description: "Vue d'ensemble",
    },
    {
      name: "Offres d'emploi",
      href: "/jobs",
      icon: Briefcase,
      description: "Gestion des postes",
    },
    {
      name: "Candidats",
      href: "/candidates",
      icon: Users,
      description: "Base de talents",
    },
    {
      name: "Analytics",
      href: "/analytics",
      icon: BarChart3,
      description: "Rapports & KPIs",
    },
    {
      name: "IA Assistant",
      href: "/ai-assistant",
      icon: Brain,
      description: "Outils intelligents",
    },
    {
      name: "Messages",
      href: "/messages",
      icon: MessageSquare,
      description: "Communications",
    },
    {
      name: "Rapports",
      href: "/reports",
      icon: FileText,
      description: "Documents RH",
    },
    {
      name: "Calendrier",
      href: "/calendar",
      icon: Calendar,
      description: "Entretiens",
    },
    {
      name: "Paramètres",
      href: "/settings",
      icon: Settings,
      description: "Configuration",
    },
  ]

  return (
    <aside className="fixed left-0 top-16 h-[calc(100vh-4rem)] w-64 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 overflow-y-auto">
      <div className="p-4">
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const isActive = location.pathname === item.href
            const Icon = item.icon

            return (
              <Link
                key={item.name}
                to={item.href}
                className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors ${
                  isActive
                    ? "bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300"
                    : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 hover:text-gray-900 dark:hover:text-gray-200"
                }`}
              >
                <Icon className="w-5 h-5" />
                <div className="flex-1">
                  <div className="text-sm font-medium">{item.name}</div>
                  <div className="text-xs opacity-75">{item.description}</div>
                </div>
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}

export default Sidebar
