"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import Header from "../components/Layout/Header"
import Footer from "../components/Layout/Footer"
import {
  Brain,
  Globe,
  Zap,
  BarChart3,
  MessageSquare,
  Shield,
  Users,
  TrendingUp,
  CheckCircle,
  ArrowRight,
  Play,
  Star,
} from "lucide-react"

const HomePage: React.FC = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0)

  const features = [
    {
      icon: Brain,
      title: "IA de Matching Avancée",
      description:
        "Algorithmes sémantiques pour analyser les CV en arabe, français et anglais avec une précision inégalée.",
      color: "bg-purple-500",
      badge: "98% de précision",
    },
    {
      icon: Globe,
      title: "Pipeline Kanban Intelligent",
      description: "Gestion visuelle du processus de recrutement avec prédictions IA et recommandations automatiques.",
      color: "bg-red-500",
      badge: "3x plus rapide",
    },
    {
      icon: Zap,
      title: "Génération d'Offres IA",
      description:
        "Création automatique d'annonces optimisées pour ReKrute, Amaljob et LinkedIn avec adaptation culturelle.",
      color: "bg-green-500",
      badge: "85% d'engagement",
    },
    {
      icon: MessageSquare,
      title: "Chatbot Multilingue",
      description: "Assistant conversationnel pour pré-screening automatique des candidats en temps réel.",
      color: "bg-blue-500",
      badge: "24/7 disponible",
    },
    {
      icon: BarChart3,
      title: "Analytics Prédictifs",
      description: "Insights avancés sur les tendances de recrutement et prévisions des besoins en talents.",
      color: "bg-orange-500",
      badge: "ROI +150%",
    },
    {
      icon: Shield,
      title: "Conformité RGPD & Locale",
      description: "Respect automatique des réglementations marocaines et européennes avec audit trail complet.",
      color: "bg-teal-500",
      badge: "100% conforme",
    },
  ]

  const stats = [
    { number: "500+", label: "Entreprises", icon: Users },
    { number: "50K+", label: "CV analysés", icon: TrendingUp },
    { number: "85%", label: "Temps économisé", icon: CheckCircle },
    { number: "94%", label: "Précision matching", icon: Brain },
  ]

  const testimonials = [
    {
      name: "Fatima El Mansouri",
      role: "DRH, TechCorp Maroc",
      company: "TechCorp",
      content:
        "TalentAI a révolutionné notre processus de recrutement. Nous trouvons les bons candidats 3x plus rapidement.",
      avatar: "/placeholder.svg?height=60&width=60",
    },
    {
      name: "Ahmed Benali",
      role: "Responsable Recrutement, StartupHub",
      company: "StartupHub",
      content: "L'IA de matching est impressionnante. Elle comprend parfaitement les nuances du marché marocain.",
      avatar: "/placeholder.svg?height=60&width=60",
    },
    {
      name: "Khadija Alami",
      role: "CEO, InnovateMA",
      company: "InnovateMA",
      content: "Le support multilingue et l'intégration avec les plateformes locales font toute la différence.",
      avatar: "/placeholder.svg?height=60&width=60",
    },
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length)
    }, 5000)
    return () => clearInterval(interval)
  }, [testimonials.length])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <Header />

      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="flex items-center space-x-2">
                <Brain className="w-5 h-5 text-purple-600" />
                <span className="text-sm text-gray-600 dark:text-gray-400 font-medium">Powered by AI</span>
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 dark:text-white">
                TalentAI
                <span className="text-red-500 block">Maroc</span>
              </h1>

              <p className="text-xl text-gray-600 dark:text-gray-300 leading-relaxed">
                Le premier ATS marocain dopé à l'IA. Recrutez plus intelligemment avec notre plateforme multilingue
                adaptée au marché local.
              </p>

              {/* Feature Pills */}
              <div className="grid grid-cols-2 gap-4">
                {[
                  {
                    icon: Brain,
                    title: "Matching IA",
                    subtitle: "Sémantique avancé",
                    color: "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300",
                  },
                  {
                    icon: Globe,
                    title: "Multilingue",
                    subtitle: "AR/FR/EN",
                    color: "bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300",
                  },
                  {
                    icon: Zap,
                    title: "Automation",
                    subtitle: "Pipeline intelligent",
                    color: "bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300",
                  },
                  {
                    icon: BarChart3,
                    title: "Analytics",
                    subtitle: "Insights prédictifs",
                    color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900 dark:text-yellow-300",
                  },
                ].map((feature, index) => (
                  <div key={feature.title} className={`${feature.color} rounded-lg p-4 flex items-center space-x-3`}>
                    <feature.icon className="w-5 h-5" />
                    <div>
                      <div className="font-semibold text-sm">{feature.title}</div>
                      <div className="text-xs opacity-75">{feature.subtitle}</div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex flex-col sm:flex-row gap-4">
                <Link
                  to="/register"
                  className="inline-flex items-center justify-center px-6 py-3 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors font-medium"
                >
                  Démarrer l'essai gratuit
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Link>
                <button className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 dark:border-gray-600 bg-transparent text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors font-medium">
                  <Play className="w-4 h-4 mr-2" />
                  Voir la démo
                </button>
              </div>
            </div>

            <div className="relative">
              <div className="absolute -top-4 -right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium z-10">
                ✓ Match trouvé
              </div>
              <div className="absolute -bottom-4 -left-4 bg-blue-500 text-white px-3 py-1 rounded-full text-sm font-medium z-10">
                📊 CV analysé
              </div>
              <img
                src="/placeholder.svg?height=600&width=800&text=TalentAI Dashboard"
                alt="TalentAI Dashboard"
                className="rounded-2xl shadow-2xl w-full"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={stat.label} className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                    <stat.icon className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                  </div>
                </div>
                <div className="text-3xl font-bold text-gray-900 dark:text-white mb-2">{stat.number}</div>
                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section
        id="solutions"
        className="py-20 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="flex items-center justify-center space-x-2 mb-4">
              <Zap className="w-5 h-5 text-purple-600" />
              <span className="text-sm text-purple-600 font-medium">Fonctionnalités IA</span>
            </div>
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
              Révolutionnez votre processus de <span className="text-red-500">recrutement</span>
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
              Une suite complète d'outils IA conçus spécifiquement pour le marché marocain, intégrant les meilleures
              pratiques internationales.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={feature.title}
                className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 ${feature.color} rounded-lg flex items-center justify-center`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <span className="text-xs bg-yellow-100 dark:bg-yellow-900 text-yellow-700 dark:text-yellow-300 px-2 py-1 rounded-full font-medium">
                    {feature.badge}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">{feature.title}</h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Ce que disent nos clients</h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Plus de 500 entreprises marocaines nous font confiance
            </p>
          </div>

          <div className="relative">
            <div className="bg-gradient-to-r from-purple-50 to-blue-50 dark:from-gray-700 dark:to-gray-600 rounded-2xl p-8">
              <div className="flex items-center mb-6">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                ))}
              </div>

              <blockquote className="text-xl text-gray-700 dark:text-gray-200 mb-6 leading-relaxed">
                "{testimonials[currentTestimonial].content}"
              </blockquote>

              <div className="flex items-center">
                <img
                  src={testimonials[currentTestimonial].avatar || "/placeholder.svg"}
                  alt={testimonials[currentTestimonial].name}
                  className="w-12 h-12 rounded-full mr-4"
                />
                <div>
                  <div className="font-semibold text-gray-900 dark:text-white">
                    {testimonials[currentTestimonial].name}
                  </div>
                  <div className="text-gray-600 dark:text-gray-400">{testimonials[currentTestimonial].role}</div>
                </div>
              </div>
            </div>

            {/* Testimonial indicators */}
            <div className="flex justify-center mt-6 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-colors ${
                    index === currentTestimonial ? "bg-purple-600" : "bg-gray-300 dark:bg-gray-600"
                  }`}
                />
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-6">Prêt à transformer votre recrutement ?</h2>
          <p className="text-xl text-purple-100 mb-8">
            Rejoignez les 500+ entreprises marocaines qui font confiance à TalentAI
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="inline-flex items-center justify-center px-8 py-4 bg-white text-purple-600 rounded-lg hover:bg-gray-100 transition-colors font-medium text-lg"
            >
              <Brain className="w-5 h-5 mr-2" />
              Commencer gratuitement
            </Link>
            <Link
              to="/contact"
              className="inline-flex items-center justify-center px-8 py-4 border-2 border-white text-white rounded-lg hover:bg-white hover:text-purple-600 transition-colors font-medium text-lg"
            >
              Demander une démo
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export default HomePage
