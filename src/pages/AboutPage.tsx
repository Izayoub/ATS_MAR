import type React from "react"
import { Link } from "react-router-dom"
import Header from "../components/Layout/Header"
import Footer from "../components/Layout/Footer"
import { Button } from "../components/ui/button"
import { Card, CardContent } from "../components/ui/card"
import { Brain, Users, Target, Award, Globe, Heart, ArrowRight, Star, MapPin, Calendar} from 'lucide-react'

const AboutPage: React.FC = () => {
  const stats = [
    { number: "2024", label: "Année de création", icon: Calendar },
    { number: "500+", label: "Entreprises clientes", icon: Users },
    { number: "50K+", label: "CV analysés", icon: Brain },
    { number: "94%", label: "Précision IA", icon: Target },
  ]

  const team = [
    {
      name: "Youssef El Alami",
      role: "CEO & Co-fondateur",
      description: "Expert en IA et ancien directeur technique chez une licorne tech",
      avatar: "/placeholder.svg?height=120&width=120&text=YA",
      linkedin: "#",
    },
    {
      name: "Fatima Benali",
      role: "CTO & Co-fondatrice",
      description: "Spécialiste en machine learning et ancienne lead engineer chez Google",
      avatar: "/placeholder.svg?height=120&width=120&text=FB",
      linkedin: "#",
    },
    {
      name: "Ahmed Tazi",
      role: "Head of Product",
      description: "Expert UX/UI avec 10 ans d'expérience dans les produits SaaS",
      avatar: "/placeholder.svg?height=120&width=120&text=AT",
      linkedin: "#",
    },
    {
      name: "Khadija Mansouri",
      role: "Head of Sales",
      description: "Experte en développement commercial B2B et marché marocain",
      avatar: "/placeholder.svg?height=120&width=120&text=KM",
      linkedin: "#",
    },
  ]

  const values = [
    {
      icon: Brain,
      title: "Innovation",
      description: "Nous repoussons les limites de l'IA pour révolutionner le recrutement au Maroc.",
      color: "bg-purple-500",
    },
    {
      icon: Heart,
      title: "Impact Social",
      description: "Nous démocratisons l'accès aux opportunités d'emploi pour tous les Marocains.",
      color: "bg-red-500",
    },
    {
      icon: Globe,
      title: "Diversité",
      description: "Nous célébrons la richesse culturelle et linguistique du Maroc.",
      color: "bg-green-500",
    },
    {
      icon: Award,
      title: "Excellence",
      description: "Nous visons l'excellence dans chaque fonctionnalité que nous développons.",
      color: "bg-blue-500",
    },
  ]

  const milestones = [
    {
      year: "2024",
      title: "Lancement de TalentAI Maroc",
      description: "Première plateforme ATS marocaine avec IA intégrée",
    },
    {
      year: "2024",
      title: "100 premières entreprises",
      description: "Adoption rapide par les startups et PME marocaines",
    },
    {
      year: "2024",
      title: "Intégration ReKrute & Amaljob",
      description: "Partenariats stratégiques avec les leaders du marché",
    },
    {
      year: "2025",
      title: "Expansion régionale",
      description: "Déploiement prévu en Tunisie et Algérie",
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <Header />

      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-6">
            <Heart className="w-5 h-5 text-red-500" />
            <span className="text-sm text-gray-600 dark:text-gray-400 font-medium">Notre mission</span>
          </div>

          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Révolutionner le recrutement au <span className="text-red-500">Maroc</span>
          </h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            TalentAI Maroc est né de la conviction que chaque talent mérite sa chance. Nous utilisons l'intelligence
            artificielle pour créer un écosystème de recrutement plus équitable, efficace et adapté au marché marocain.
          </p>

          <div className="flex items-center justify-center space-x-2 text-gray-500 dark:text-gray-400">
            <MapPin className="w-4 h-4" />
            <span>Fondé à Casablanca, Maroc</span>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="flex justify-center mb-4">
                  <div className="w-16 h-16 bg-purple-100 dark:bg-purple-900 rounded-full flex items-center justify-center">
                    <stat.icon className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                  </div>
                </div>
                <div className="text-4xl font-bold text-gray-900 dark:text-white mb-2">{stat.number}</div>
                <div className="text-gray-600 dark:text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Story Section */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-6">Notre histoire</h2>
              <div className="space-y-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                <p>
                  En 2024, nos fondateurs ont identifié un problème majeur : le marché du recrutement marocain manquait
                  d'outils adaptés à sa diversité linguistique et culturelle. Les solutions internationales ne
                  comprenaient pas les spécificités locales.
                </p>
                <p>
                  C'est ainsi qu'est née TalentAI Maroc, la première plateforme ATS conçue spécifiquement pour le marché
                  marocain, intégrant l'arabe, le français et l'anglais dans ses algorithmes d'IA.
                </p>
                <p>
                  Aujourd'hui, nous sommes fiers d'accompagner plus de 500 entreprises dans leur transformation
                  digitale RH, de la startup innovante à la grande entreprise établie.
                </p>
              </div>
            </div>
            <div className="relative">
              <img
                src="/placeholder.svg?height=400&width=600&text=Notre équipe à Casablanca"
                alt="Équipe TalentAI Maroc"
                className="rounded-2xl shadow-2xl w-full"
              />
              <div className="absolute -bottom-6 -right-6 bg-white dark:bg-gray-800 p-4 rounded-lg shadow-lg">
                <div className="flex items-center space-x-2">
                  <Star className="w-5 h-5 text-yellow-400 fill-current" />
                  <span className="font-semibold text-gray-900 dark:text-white">4.9/5</span>
                  <span className="text-gray-600 dark:text-gray-400">satisfaction client</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Values Section */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Nos valeurs</h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Les principes qui guident chacune de nos décisions et innovations
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value) => (
              <Card key={value.title} className="text-center hover:shadow-xl transition-all duration-300">
                <CardContent className="p-6">
                  <div className={`w-16 h-16 ${value.color} rounded-full flex items-center justify-center mx-auto mb-4`}>
                    <value.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">{value.title}</h3>
                  <p className="text-gray-600 dark:text-gray-300 leading-relaxed">{value.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-20 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Notre équipe</h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Des experts passionnés qui révolutionnent le recrutement au Maroc
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member) => (
              <Card key={member.name} className="text-center hover:shadow-xl transition-all duration-300">
                <CardContent className="p-6">
                  <img
                    src={member.avatar || "/placeholder.svg"}
                    alt={member.name}
                    className="w-24 h-24 rounded-full mx-auto mb-4 object-cover"
                  />
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">{member.name}</h3>
                  <p className="text-purple-600 dark:text-purple-400 font-medium mb-3">{member.role}</p>
                  <p className="text-gray-600 dark:text-gray-300 text-sm leading-relaxed mb-4">{member.description}</p>
                  <Button variant="outline" size="sm" asChild>
                    <a href={member.linkedin} target="_blank" rel="noopener noreferrer">
                      LinkedIn
                    </a>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline Section */}
      <section className="py-20 bg-white dark:bg-gray-800">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Notre parcours</h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">Les étapes clés de notre croissance</p>
          </div>

          <div className="space-y-8">
            {milestones.map((milestone) => (
              <div key={milestone.year} className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <div className="w-12 h-12 bg-purple-600 rounded-full flex items-center justify-center">
                    <span className="text-white font-bold text-sm">{milestone.year}</span>
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">{milestone.title}</h3>
                  <p className="text-gray-600 dark:text-gray-300">{milestone.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-purple-600 to-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white mb-6">Rejoignez notre mission</h2>
          <p className="text-xl text-purple-100 mb-8">
            Ensemble, construisons l'avenir du recrutement au Maroc
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button asChild size="lg" className="bg-white text-purple-600 hover:bg-gray-100">
              <Link to="/register">
                Commencer gratuitement
                <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="border-white text-white hover:bg-white hover:text-purple-600 bg-transparent"
            >
              <Link to="/contact">Nous contacter</Link>
            </Button>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export default AboutPage
