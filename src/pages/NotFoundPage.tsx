"use client"

import type React from "react"
import { Link } from "react-router-dom"
import { Home, ArrowLeft, Search } from "lucide-react"
import { Button } from "../components/ui/button"

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        {/* 404 Animation */}
        <div className="mb-8">
          <div className="text-9xl font-bold text-purple-600 dark:text-purple-400 mb-4 animate-bounce-in">404</div>
          <div className="w-24 h-1 bg-gradient-to-r from-purple-600 to-blue-600 mx-auto rounded-full"></div>
        </div>

        {/* Content */}
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Page introuvable</h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Désolé, la page que vous recherchez n'existe pas ou a été déplacée.
            </p>
          </div>

          {/* Search suggestion */}
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-center mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Vous cherchiez peut-être :</p>
            <div className="space-y-2 text-sm">
              <Link
                to="/dashboard"
                className="block text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
              >
                → Tableau de bord
              </Link>
              <Link
                to="/jobs"
                className="block text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
              >
                → Offres d'emploi
              </Link>
              <Link
                to="/candidates"
                className="block text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300"
              >
                → Candidats
              </Link>
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild variant="default" size="lg">
              <Link to="/">
                <Home className="w-4 h-4 mr-2" />
                Accueil
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg" onClick={() => window.history.back()}>
              <button>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Retour
              </button>
            </Button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-sm text-gray-500 dark:text-gray-400">
          <p>
            Besoin d'aide ?{" "}
            <Link to="/contact" className="text-purple-600 hover:text-purple-700 dark:text-purple-400">
              Contactez-nous
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage
