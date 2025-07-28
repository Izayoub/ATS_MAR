"use client"

import type React from "react"
import { useState } from "react"
import Header from "../components/Layout/Header"
import Footer from "../components/Layout/Footer"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { useToast } from "../contexts/ToastContext"
import { Mail, Phone, MapPin, Clock, Send, MessageSquare, Users, Headphones, Calendar, ArrowRight } from "lucide-react"

const ContactPage: React.FC = () => {
  const { addToast } = useToast()
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    phone: "",
    subject: "",
    message: "",
    type: "general",
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 1500))
      addToast("Message envoyé avec succès ! Nous vous répondrons sous 24h.", "success")
      setFormData({
        name: "",
        email: "",
        company: "",
        phone: "",
        subject: "",
        message: "",
        type: "general",
      })
    } catch (error) {
      addToast("Erreur lors de l'envoi du message. Veuillez réessayer.", "error")
    } finally {
      setIsSubmitting(false)
    }
  }

  const contactInfo = [
    {
      icon: Mail,
      title: "Email",
      value: "hello@talentai.ma",
      description: "Réponse sous 24h",
      color: "bg-blue-500",
    },
    {
      icon: Phone,
      title: "Téléphone",
      value: "+212 5XX XX XX XX",
      description: "Lun-Ven 9h-18h",
      color: "bg-green-500",
    },
    {
      icon: MapPin,
      title: "Adresse",
      value: "Casablanca, Maroc",
      description: "Twin Center, Tour A",
      color: "bg-red-500",
    },
    {
      icon: Clock,
      title: "Horaires",
      value: "9h00 - 18h00",
      description: "Lundi au Vendredi",
      color: "bg-purple-500",
    },
  ]

  const supportOptions = [
    {
      icon: MessageSquare,
      title: "Chat en direct",
      description: "Assistance immédiate pour vos questions urgentes",
      action: "Démarrer le chat",
      available: true,
    },
    {
      icon: Calendar,
      title: "Réserver une démo",
      description: "Découvrez TalentAI en 30 minutes avec un expert",
      action: "Planifier",
      available: true,
    },
    {
      icon: Headphones,
      title: "Support technique",
      description: "Aide pour l'installation et la configuration",
      action: "Contacter",
      available: true,
    },
    {
      icon: Users,
      title: "Formation équipe",
      description: "Sessions de formation personnalisées",
      action: "En savoir plus",
      available: false,
    },
  ]

  const faqs = [
    {
      question: "Combien de temps faut-il pour configurer TalentAI ?",
      answer: "La configuration initiale prend environ 30 minutes. Notre équipe vous accompagne gratuitement.",
    },
    {
      question: "TalentAI s'intègre-t-il avec nos outils existants ?",
      answer: "Oui, nous nous intégrons avec ReKrute, Amaljob, LinkedIn et la plupart des SIRH marocains.",
    },
    {
      question: "Proposez-vous une formation pour nos équipes ?",
      answer: "Absolument ! Nous offrons des sessions de formation gratuites pour tous nos clients.",
    },
    {
      question: "Vos données sont-elles sécurisées ?",
      answer: "Oui, nous respectons les normes RGPD et utilisons un chiffrement de niveau bancaire.",
    },
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
      <Header />

      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <div className="flex items-center justify-center space-x-2 mb-6">
            <MessageSquare className="w-5 h-5 text-purple-600" />
            <span className="text-sm text-gray-600 dark:text-gray-400 font-medium">Nous sommes là pour vous</span>
          </div>

          <h1 className="text-5xl font-bold text-gray-900 dark:text-white mb-6">Contactez-nous</h1>

          <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto">
            Une question ? Besoin d'aide ? Notre équipe d'experts est à votre disposition pour vous accompagner dans
            votre transformation RH.
          </p>
        </div>
      </section>

      {/* Contact Info Cards */}
      <section className="pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {contactInfo.map((info) => (
              <Card
                key={info.title}
                className="hover:shadow-lg transition-shadow dark:bg-gray-800 dark:border-gray-700"
              >
                <CardContent className="p-6">
                  <div className={`w-12 h-12 ${info.color} rounded-lg flex items-center justify-center mx-auto mb-4`}>
                    <info.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{info.title}</h3>
                  <p className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-1">{info.value}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{info.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Main Content */}
      <section className="py-16 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle className="text-2xl text-gray-900 dark:text-white">Envoyez-nous un message</CardTitle>
                  <p className="text-gray-600 dark:text-gray-400">
                    Remplissez le formulaire ci-dessous et nous vous répondrons rapidement.
                  </p>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label
                          htmlFor="name"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                        >
                          Nom complet *
                        </label>
                        <input
                          type="text"
                          id="name"
                          name="name"
                          required
                          value={formData.name}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="Ahmed Benali"
                        />
                      </div>
                      <div>
                        <label
                          htmlFor="email"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                        >
                          Email *
                        </label>
                        <input
                          type="email"
                          id="email"
                          name="email"
                          required
                          value={formData.email}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="ahmed@entreprise.ma"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <label
                          htmlFor="company"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                        >
                          Entreprise
                        </label>
                        <input
                          type="text"
                          id="company"
                          name="company"
                          value={formData.company}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="TechCorp Maroc"
                        />
                      </div>
                      <div>
                        <label
                          htmlFor="phone"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                        >
                          Téléphone
                        </label>
                        <input
                          type="tel"
                          id="phone"
                          name="phone"
                          value={formData.phone}
                          onChange={handleChange}
                          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="+212 6XX XX XX XX"
                        />
                      </div>
                    </div>

                    <div>
                      <label htmlFor="type" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Type de demande
                      </label>
                      <select
                        id="type"
                        name="type"
                        value={formData.type}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      >
                        <option value="general">Question générale</option>
                        <option value="demo">Demande de démo</option>
                        <option value="support">Support technique</option>
                        <option value="partnership">Partenariat</option>
                        <option value="press">Presse</option>
                      </select>
                    </div>

                    <div>
                      <label
                        htmlFor="subject"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                      >
                        Sujet *
                      </label>
                      <input
                        type="text"
                        id="subject"
                        name="subject"
                        required
                        value={formData.subject}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="Comment TalentAI peut-il nous aider ?"
                      />
                    </div>

                    <div>
                      <label
                        htmlFor="message"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
                      >
                        Message *
                      </label>
                      <textarea
                        id="message"
                        name="message"
                        required
                        rows={5}
                        value={formData.message}
                        onChange={handleChange}
                        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        placeholder="Décrivez votre besoin ou votre question..."
                      />
                    </div>

                    <Button type="submit" disabled={isSubmitting} className="w-full" size="lg">
                      {isSubmitting ? (
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                      ) : (
                        <Send className="w-4 h-4 mr-2" />
                      )}
                      {isSubmitting ? "Envoi en cours..." : "Envoyer le message"}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Support Options & FAQ */}
            <div className="space-y-8">
              {/* Support Options */}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
                  Autres moyens de nous contacter
                </h2>
                <div className="space-y-4">
                  {supportOptions.map((option) => (
                    <Card
                      key={option.title}
                      className="hover:shadow-md transition-shadow dark:bg-gray-800 dark:border-gray-700"
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start space-x-4">
                          <div className="w-10 h-10 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center flex-shrink-0">
                            <option.icon className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                          </div>
                          <div className="flex-1">
                            <h3 className="font-semibold text-gray-900 dark:text-white mb-1">{option.title}</h3>
                            <p className="text-gray-600 dark:text-gray-400 text-sm mb-3">{option.description}</p>
                            <Button
                              variant={option.available ? "default" : "outline"}
                              size="sm"
                              disabled={!option.available}
                            >
                              {option.action}
                              {option.available && <ArrowRight className="w-3 h-3 ml-1" />}
                            </Button>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>

              {/* FAQ */}
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">Questions fréquentes</h2>
                <div className="space-y-4">
                  {faqs.map((faq, index) => (
                    <Card key={index} className="dark:bg-gray-800 dark:border-gray-700">
                      <CardContent className="p-4">
                        <h3 className="font-semibold text-gray-900 dark:text-white mb-2">{faq.question}</h3>
                        <p className="text-gray-600 dark:text-gray-400 text-sm">{faq.answer}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Map Section */}
      <section className="py-16 bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-gray-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Venez nous rendre visite</h2>
            <p className="text-gray-600 dark:text-gray-400">
              Nos bureaux sont situés au cœur de Casablanca, dans le quartier d'affaires
            </p>
          </div>

          <Card className="overflow-hidden dark:bg-gray-800 dark:border-gray-700">
            <div className="h-96 bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
              <div className="text-center">
                <MapPin className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">Carte interactive</p>
                <p className="text-sm text-gray-400">Twin Center, Tour A, Casablanca</p>
              </div>
            </div>
          </Card>
        </div>
      </section>

      <Footer />
    </div>
  )
}

export default ContactPage
