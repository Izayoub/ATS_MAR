"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useTheme } from "../contexts/ThemeContext"
import { useToast } from "../contexts/ToastContext"
import { Button } from "../components/ui/button"
import { Card } from "../components/ui/card"
import {
  Send,
  Bot,
  User,
  Sparkles,
  FileText,
  Users,
  TrendingUp,
  MessageSquare,
  Clock,
  Star,
  Download,
  Copy,
  RefreshCw,
  Zap,
  Brain,
  Target,
  Search,
  BarChart3,
  MoreVertical,
} from "lucide-react"

interface Message {
  id: string
  type: "user" | "assistant"
  content: string
  timestamp: Date
  suggestions?: string[]
}

interface QuickAction {
  id: string
  title: string
  description: string
  icon: React.ReactNode
  prompt: string
  category: "analysis" | "generation" | "optimization"
}

const AIAssistantPage: React.FC = () => {
  const { actualTheme } = useTheme()
  const { addToast } = useToast()
  const navigate = useNavigate()

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "assistant",
      content:
        "Bonjour ! Je suis votre assistant IA pour le recrutement. Comment puis-je vous aider aujourd'hui ? Je peux analyser des CV, générer des descriptions de poste, suggérer des questions d'entretien, ou vous aider avec vos stratégies de recrutement.",
      timestamp: new Date(),
      suggestions: [
        "Analyser un CV",
        "Créer une description de poste",
        "Générer des questions d'entretien",
        "Optimiser une offre d'emploi",
      ],
    },
  ])

  const [inputMessage, setInputMessage] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const quickActions: QuickAction[] = [
    {
      id: "1",
      title: "Analyser un CV",
      description: "Analysez les compétences, expérience et compatibilité d'un candidat",
      icon: <FileText className="w-5 h-5" />,
      prompt: "Peux-tu analyser ce CV et me donner un score de compatibilité pour le poste de [POSTE] ?",
      category: "analysis",
    },
    {
      id: "2",
      title: "Générer description de poste",
      description: "Créez une description de poste attractive et complète",
      icon: <Users className="w-5 h-5" />,
      prompt:
        "Aide-moi à créer une description de poste pour un [POSTE] avec les compétences suivantes : [COMPÉTENCES]",
      category: "generation",
    },
    {
      id: "3",
      title: "Questions d'entretien",
      description: "Générez des questions d'entretien personnalisées",
      icon: <MessageSquare className="w-5 h-5" />,
      prompt: "Génère 10 questions d'entretien pour un candidat [POSTE] avec [X] années d'expérience",
      category: "generation",
    },
    {
      id: "4",
      title: "Optimiser une offre",
      description: "Améliorez l'attractivité de vos offres d'emploi",
      icon: <TrendingUp className="w-5 h-5" />,
      prompt: "Comment puis-je optimiser cette offre d'emploi pour attirer plus de candidats qualifiés ?",
      category: "optimization",
    },
    {
      id: "5",
      title: "Stratégie de sourcing",
      description: "Développez des stratégies de recherche de candidats",
      icon: <Target className="w-5 h-5" />,
      prompt: "Quelle stratégie de sourcing recommandes-tu pour trouver des [PROFIL] au Maroc ?",
      category: "optimization",
    },
    {
      id: "6",
      title: "Analyse de marché",
      description: "Analysez les tendances du marché de l'emploi",
      icon: <BarChart3 className="w-5 h-5" />,
      prompt: "Peux-tu analyser les tendances actuelles du marché pour les profils [DOMAINE] au Maroc ?",
      category: "analysis",
    },
  ]

  const categories = [
    { id: "all", label: "Toutes", icon: <Sparkles className="w-4 h-4" /> },
    { id: "analysis", label: "Analyse", icon: <Search className="w-4 h-4" /> },
    { id: "generation", label: "Génération", icon: <Brain className="w-4 h-4" /> },
    { id: "optimization", label: "Optimisation", icon: <Zap className="w-4 h-4" /> },
  ]

  const filteredActions =
    selectedCategory === "all" ? quickActions : quickActions.filter((action) => action.category === selectedCategory)

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  const handleSendMessage = async () => {
    if (!inputMessage.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputMessage,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputMessage("")
    setIsLoading(true)

    // Simuler une réponse de l'IA
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "assistant",
        content: generateAIResponse(inputMessage),
        timestamp: new Date(),
        suggestions: generateSuggestions(inputMessage),
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1500)
  }

  const generateAIResponse = (input: string): string => {
    const responses = [
      `Excellente question ! Pour ${input.toLowerCase()}, je recommande une approche structurée. Voici mes suggestions détaillées basées sur les meilleures pratiques du recrutement au Maroc...`,
      `Basé sur mon analyse des tendances actuelles, voici ce que je peux vous dire concernant ${input.toLowerCase()}. Cette approche a montré des résultats positifs dans 85% des cas similaires...`,
      `C'est un point important dans le recrutement moderne. Laissez-moi vous expliquer les meilleures pratiques que j'ai observées chez les entreprises performantes...`,
      `D'après les données du marché marocain et les retours de nos utilisateurs, voici mon analyse détaillée avec des recommandations concrètes...`,
    ]
    return responses[Math.floor(Math.random() * responses.length)]
  }

  const generateSuggestions = (input: string): string[] => {
    return [
      "Peux-tu être plus spécifique ?",
      "Montre-moi un exemple concret",
      "Quelles sont les alternatives ?",
      "Comment mesurer les résultats ?",
    ]
  }

  const handleQuickAction = (action: QuickAction) => {
    setInputMessage(action.prompt)
    inputRef.current?.focus()
  }

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion)
    inputRef.current?.focus()
  }

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content)
    addToast("Message copié dans le presse-papiers", "success")
  }

  const exportConversation = () => {
    const conversation = messages
      .map(
        (msg) =>
          `${msg.type === "user" ? "Vous" : "Assistant IA"} (${msg.timestamp.toLocaleTimeString()}): ${msg.content}`,
      )
      .join("\n\n")

    const blob = new Blob([conversation], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `conversation-ai-${new Date().toISOString().split("T")[0]}.txt`
    a.click()
    URL.revokeObjectURL(url)
    addToast("Conversation exportée avec succès", "success")
  }

  const clearConversation = () => {
    setMessages([
      {
        id: "1",
        type: "assistant",
        content: "Nouvelle conversation démarrée ! Comment puis-je vous aider ?",
        timestamp: new Date(),
      },
    ])
    addToast("Conversation effacée", "success")
  }

  return (
    <div
      className={`min-h-screen transition-colors duration-200 ${actualTheme === "dark" ? "dark bg-gray-900" : "bg-gray-50"}`}
    >
      
      <div className="flex">
        
        
          <div className="p-6">
            <div className="max-w-7xl mx-auto">
              {/* En-tête de la page */}
              <div className="mb-6">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="p-3 bg-purple-100 dark:bg-purple-900/50 rounded-xl transition-colors duration-200">
                      <Bot className="w-8 h-8 text-purple-600 dark:text-purple-400" />
                    </div>
                    <div>
                      <h1 className="text-3xl font-bold text-gray-900 dark:text-white transition-colors duration-200">
                        Assistant IA
                      </h1>
                      <p className="text-gray-600 dark:text-gray-400 mt-1 transition-colors duration-200">
                        Votre assistant intelligent pour optimiser vos processus de recrutement
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <Button
                      variant="outline"
                      onClick={exportConversation}
                      className="flex items-center space-x-2 bg-transparent border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200"
                    >
                      <Download className="w-4 h-4" />
                      <span>Exporter</span>
                    </Button>
                    <Button
                      variant="outline"
                      onClick={clearConversation}
                      className="flex items-center space-x-2 bg-transparent border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors duration-200"
                    >
                      <RefreshCw className="w-4 h-4" />
                      <span>Nouveau</span>
                    </Button>
                  </div>
                </div>
              </div>

              {/* Statistiques rapides */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
                <Card className="p-6 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-colors duration-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 transition-colors duration-200">
                        Messages aujourd'hui
                      </p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2 transition-colors duration-200">
                        24
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-400 mt-1">+12% vs hier</p>
                    </div>
                    <div className="p-3 bg-blue-100 dark:bg-blue-900/50 rounded-lg transition-colors duration-200">
                      <MessageSquare className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                  </div>
                </Card>

                <Card className="p-6 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-colors duration-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 transition-colors duration-200">
                        CV analysés
                      </p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2 transition-colors duration-200">
                        12
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-400 mt-1">+8% vs hier</p>
                    </div>
                    <div className="p-3 bg-green-100 dark:bg-green-900/50 rounded-lg transition-colors duration-200">
                      <FileText className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                </Card>

                <Card className="p-6 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-colors duration-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 transition-colors duration-200">
                        Temps économisé
                      </p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2 transition-colors duration-200">
                        3.2h
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-400 mt-1">Cette semaine</p>
                    </div>
                    <div className="p-3 bg-purple-100 dark:bg-purple-900/50 rounded-lg transition-colors duration-200">
                      <Clock className="w-6 h-6 text-purple-600 dark:text-purple-400" />
                    </div>
                  </div>
                </Card>

                <Card className="p-6 bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-colors duration-200">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400 transition-colors duration-200">
                        Satisfaction
                      </p>
                      <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2 transition-colors duration-200">
                        4.8/5
                      </p>
                      <p className="text-sm text-green-600 dark:text-green-400 mt-1">Excellent</p>
                    </div>
                    <div className="p-3 bg-yellow-100 dark:bg-yellow-900/50 rounded-lg transition-colors duration-200">
                      <Star className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                    </div>
                  </div>
                </Card>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                {/* Panneau des actions rapides */}
                <div className="lg:col-span-1">
                  <Card className="p-6 h-fit bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-colors duration-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center transition-colors duration-200">
                        <Zap className="w-5 h-5 mr-2 text-purple-600 dark:text-purple-400" />
                        Actions rapides
                      </h3>
                    </div>

                    {/* Filtres par catégorie */}
                    <div className="flex flex-wrap gap-2 mb-6">
                      {categories.map((category) => (
                        <Button
                          key={category.id}
                          variant={selectedCategory === category.id ? "default" : "outline"}
                          size="sm"
                          onClick={() => setSelectedCategory(category.id)}
                          className="flex items-center space-x-1 text-xs transition-colors duration-200"
                        >
                          {category.icon}
                          <span>{category.label}</span>
                        </Button>
                      ))}
                    </div>

                    {/* Liste des actions */}
                    <div className="space-y-3">
                      {filteredActions.map((action) => (
                        <div
                          key={action.id}
                          onClick={() => handleQuickAction(action)}
                          className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors duration-200"
                        >
                          <div className="flex items-start space-x-3">
                            <div className="p-2 bg-purple-100 dark:bg-purple-900/50 rounded-lg transition-colors duration-200">
                              {action.icon}
                            </div>
                            <div className="flex-1 min-w-0">
                              <h4 className="font-medium text-gray-900 dark:text-white text-sm transition-colors duration-200">
                                {action.title}
                              </h4>
                              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 transition-colors duration-200">
                                {action.description}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                </div>

                {/* Zone de chat principale */}
                <div className="lg:col-span-3">
                  <Card className="h-[700px] flex flex-col bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 transition-colors duration-200">
                    {/* En-tête du chat */}
                    <div className="p-4 border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-green-100 dark:bg-green-900/50 rounded-full transition-colors duration-200">
                            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900 dark:text-white transition-colors duration-200">
                              Assistant IA TalentAI
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400 transition-colors duration-200">
                              En ligne • Répond généralement en quelques secondes
                            </p>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm" className="hover:bg-gray-100 dark:hover:bg-gray-700">
                          <MoreVertical className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>

                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-6">
                      {messages.map((message) => (
                        <div
                          key={message.id}
                          className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                        >
                          <div
                            className={`flex items-start space-x-3 max-w-3xl group ${
                              message.type === "user" ? "flex-row-reverse space-x-reverse" : ""
                            }`}
                          >
                            <div
                              className={`p-2 rounded-full transition-colors duration-200 ${
                                message.type === "user" ? "bg-purple-600" : "bg-gray-200 dark:bg-gray-700"
                              }`}
                            >
                              {message.type === "user" ? (
                                <User className="w-4 h-4 text-white" />
                              ) : (
                                <Bot className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                              )}
                            </div>
                            <div className={`flex-1 ${message.type === "user" ? "text-right" : ""}`}>
                              <div
                                className={`p-4 rounded-2xl transition-colors duration-200 ${
                                  message.type === "user"
                                    ? "bg-purple-600 text-white"
                                    : "bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white"
                                }`}
                              >
                                <p className="text-sm leading-relaxed">{message.content}</p>
                              </div>
                              <div className="flex items-center justify-between mt-2">
                                <p className="text-xs text-gray-500 dark:text-gray-400 transition-colors duration-200">
                                  {message.timestamp.toLocaleTimeString("fr-FR", {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  })}
                                </p>
                                {message.type === "assistant" && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={() => copyMessage(message.content)}
                                    className="p-1 h-auto opacity-0 group-hover:opacity-100 transition-opacity hover:bg-gray-200 dark:hover:bg-gray-600"
                                  >
                                    <Copy className="w-3 h-3" />
                                  </Button>
                                )}
                              </div>
                              {/* Suggestions */}
                              {message.suggestions && (
                                <div className="mt-3 flex flex-wrap gap-2">
                                  {message.suggestions.map((suggestion, index) => (
                                    <Button
                                      key={index}
                                      variant="outline"
                                      size="sm"
                                      onClick={() => handleSuggestionClick(suggestion)}
                                      className="text-xs h-8 px-3 border-gray-300 dark:border-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors duration-200"
                                    >
                                      {suggestion}
                                    </Button>
                                  ))}
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}

                      {/* Indicateur de frappe */}
                      {isLoading && (
                        <div className="flex justify-start">
                          <div className="flex items-center space-x-3">
                            <div className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 transition-colors duration-200">
                              <Bot className="w-4 h-4 text-gray-600 dark:text-gray-300" />
                            </div>
                            <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-2xl transition-colors duration-200">
                              <div className="flex space-x-1">
                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                                <div
                                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                  style={{ animationDelay: "0.1s" }}
                                ></div>
                                <div
                                  className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                                  style={{ animationDelay: "0.2s" }}
                                ></div>
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                      <div ref={messagesEndRef} />
                    </div>

                    {/* Zone de saisie */}
                    <div className="border-t border-gray-200 dark:border-gray-700 p-4 transition-colors duration-200">
                      <div className="flex items-end space-x-3">
                        <div className="flex-1">
                          <input
                            ref={inputRef}
                            type="text"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                            placeholder="Tapez votre message..."
                            className="w-full p-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none transition-colors duration-200"
                            disabled={isLoading}
                          />
                        </div>
                        <Button
                          onClick={handleSendMessage}
                          disabled={!inputMessage.trim() || isLoading}
                          className="p-3 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:bg-gray-400 transition-colors duration-200"
                        >
                          <Send className="w-4 h-4" />
                        </Button>
                      </div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2 px-1 transition-colors duration-200">
                        Appuyez sur Entrée pour envoyer • L'IA peut faire des erreurs, vérifiez les informations
                        importantes
                      </p>
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        
      </div>
    </div>
  )
}

export default AIAssistantPage
