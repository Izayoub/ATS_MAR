"use client"

import type React from "react"
import { useState } from "react"
import { Link } from "react-router-dom"
import Header from "../components/Layout/Header"
import Footer from "../components/Layout/Footer"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Check, X, Brain, Users, Briefcase, BarChart3, Shield, Headphones, Star, ArrowRight } from "lucide-react"

const PricingPage: React.FC = () => {
  const [isAnnual, setIsAnnual] = useState(false)

  const plans = [
    {
      name: "Starter",
      description: "Parfait pour les petites entreprises",
      monthlyPrice: 299,
      annualPrice: 2990,
      features: [
        "Jusqu'à 50 candidats/mois",
        "5 offres d'emploi actives",
        "Matching IA basique",
        "Support email",
        "Intégration ReKrute",
        "Tableau de bord simple",
      ],
      limitations: ["Analytics avancés", "Chatbot multilingue", "API access", "Support prioritaire"],
      popular: false,
      color: "border-gray-200",
    },
    {
      name: "Professional",
      description: "Idéal pour les entreprises en croissance",
      monthlyPrice: 799,
      annualPrice: 7990,
      features: [
        "Jusqu'à 200 candidats/mois",
        "20 offres d'emploi actives",
        "Matching IA avancé",
        "Chatbot multilingue",
        "Analytics détaillés",
        "Support prioritaire",
        "Intégrations multiples",
        "Pipeline Kanban",
        "Génération d'offres IA",
      ],
      limitations: ["API complète", "White-label"],
      popular: true,
      color: "border-purple-500",
    },
    {
      name: "Enterprise",
      description: "Pour les grandes organisations",
      monthlyPrice: 1999,
      annualPrice: 19990,
      features: [
        "Candidats illimités",
        "Offres illimitées",
        "IA personnalisée",
        "Support dédié 24/7",
        "API complète",
        "White-label",
        "Formation équipe",
        "Conformité avancée",
        "Intégrations sur mesure",
        "Analytics prédictifs",
        "Multi-entreprises",
      ],
      limitations: [],
      popular: false,
      color: "border-gold-500",
    },
  ]

  const faqs = [
    {
      question: "Puis-je changer de plan à tout moment ?",
      answer:
        "Oui, vous pouvez upgrader ou downgrader votre plan à tout moment. Les changements prennent effet immédiatement.",
    },
    {
      question: "Y a-t-il une période d'essai gratuite ?",
      answer:
        "Oui, nous offrons 14 jours d'essai gratuit sur tous nos plans, sans engagement ni carte de crédit requise.",
    },
    {
      question: "Les intégrations sont-elles incluses ?",
      answer:
        "Les intégrations de base (ReKrute, Amaljob) sont incluses. Les intégrations avancées dépendent de votre plan.",
    },
    {
      question: "Comment fonctionne le support ?",
      answer:
        "Support email pour Starter, support prioritaire pour Professional, et support dédié 24/7 pour Enterprise.",
    },
    {
      question: "Mes données sont-elles sécurisées ?",
      answer:
        "Absolument. Nous respectons les normes RGPD et les réglementations marocaines avec chiffrement end-to-end.",
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <Header />

      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-6">
            <Star className="w-5 h-5 text-purple-600" />
            <span className="text-sm text-purple-600 font-medium">Tarification transparente</span>
          </div>

          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Choisissez le plan qui vous convient
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Commencez gratuitement et évoluez avec votre entreprise. Tous les plans incluent notre IA de matching
            révolutionnaire.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-12">
            <span className={`text-sm ${!isAnnual ? "text-gray-900 dark:text-white font-medium" : "text-gray-500"}`}>
              Mensuel
            </span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                isAnnual ? "bg-purple-600" : "bg-gray-200 dark:bg-gray-700"
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  isAnnual ? "translate-x-6" : "translate-x-1"
                }`}
              />
            </button>
            <span className={`text-sm ${isAnnual ? "text-gray-900 dark:text-white font-medium" : "text-gray-500"}`}>
              Annuel
            </span>
            {isAnnual && (
              <span className="bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-1 rounded-full text-xs font-medium">
                -17%
              </span>
            )}
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <Card
                key={plan.name}
                className={`relative ${plan.color} ${plan.popular ? "ring-2 ring-purple-500 scale-105" : ""} hover:shadow-xl transition-all duration-300`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="bg-purple-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Plus populaire
                    </span>
                  </div>
                )}

                <CardHeader className="text-center pb-8">
                  <CardTitle className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{plan.name}</CardTitle>
                  <p className="text-gray-600 dark:text-gray-400 mb-6">{plan.description}</p>

                  <div className="space-y-2">
                    <div className="text-4xl font-bold text-gray-900 dark:text-white">
                      {isAnnual ? plan.annualPrice : plan.monthlyPrice}
                      <span className="text-lg text-gray-500"> MAD</span>
                    </div>
                    <div className="text-sm text-gray-500">{isAnnual ? "par an" : "par mois"}</div>
                    {isAnnual && (
                      <div className="text-sm text-green-600 dark:text-green-400">
                        Économisez {(plan.monthlyPrice * 12 - plan.annualPrice).toLocaleString()} MAD
                      </div>
                    )}
                  </div>
                </CardHeader>

                <CardContent className="space-y-6">
                  {/* Features */}
                  <div className="space-y-3">
                    {plan.features.map((feature, idx) => (
                      <div key={idx} className="flex items-center space-x-3">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700 dark:text-gray-300 text-sm">{feature}</span>
                      </div>
                    ))}

                    {plan.limitations.map((limitation, idx) => (
                      <div key={idx} className="flex items-center space-x-3 opacity-50">
                        <X className="w-5 h-5 text-gray-400 flex-shrink-0" />
                        <span className="text-gray-500 text-sm line-through">{limitation}</span>
                      </div>
                    ))}
                  </div>

                  {/* CTA Button */}
                  <Button
                    asChild
                    className={`w-full ${plan.popular ? "bg-purple-600 hover:bg-purple-700" : "bg-gray-900 hover:bg-gray-800 dark:bg-white dark:text-gray-900 dark:hover:bg-gray-100"}`}
                    size="lg"
                  >
                    <Link to="/register">
                      Commencer l'essai gratuit
                      <ArrowRight className="w-4 h-4 ml-2" />
                    </Link>
                  </Button>

                  <p className="text-xs text-gray-500 text-center">14 jours gratuits • Sans engagement</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Features Comparison */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
              Comparaison détaillée des fonctionnalités
            </h2>
            <p className="text-gray-600 dark:text-gray-400">Découvrez ce qui est inclus dans chaque plan</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              {
                icon: Brain,
                title: "IA de Matching",
                description: "Algorithmes sémantiques avancés pour un matching précis",
                color: "bg-purple-500",
              },
              {
                icon: Users,
                title: "Gestion Candidats",
                description: "Base de données centralisée avec profils détaillés",
                color: "bg-blue-500",
              },
              {
                icon: Briefcase,
                title: "Pipeline Intelligent",
                description: "Workflow automatisé avec prédictions IA",
                color: "bg-green-500",
              },
              {
                icon: BarChart3,
                title: "Analytics Avancés",
                description: "Rapports détaillés et insights prédictifs",
                color: "bg-orange-500",
              },
              {
                icon: Shield,
                title: "Sécurité & Conformité",
                description: "RGPD et réglementations marocaines",
                color: "bg-red-500",
              },
              {
                icon: Headphones,
                title: "Support Expert",
                description: "Assistance technique et formation",
                color: "bg-teal-500",
              },
            ].map((feature, index) => (
              <Card key={feature.title} className="text-center hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div
                    className={`w-12 h-12 ${feature.color} rounded-lg flex items-center justify-center mx-auto mb-4`}
                  >
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{feature.title}</h3>
                  <p className="text-sm text-gray-600 dark:text-gray-400">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Questions fréquentes</h2>
            <p className="text-gray-600 dark:text-gray-400">Tout ce que vous devez savoir sur nos plans</p>
          </div>

          <div className="space-y-6">
            {faqs.map((faq, index) => (
              <Card key={index} className="hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-3">{faq.question}</h3>
                  <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{faq.answer}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-purple-600 to-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-bold text-white mb-4">Prêt à révolutionner votre recrutement ?</h2>
          <p className="text-xl text-purple-100 mb-8">Commencez votre essai gratuit de 14 jours dès aujourd'hui</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="bg-white text-purple-600 hover:bg-gray-100">
              <Link to="/register">
                Essai gratuit 14 jours
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="border-white text-white hover:bg-white hover:text-purple-600 bg-transparent"
            >
              <Link to="/contact">Demander une démo</Link>
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export default PricingPage
