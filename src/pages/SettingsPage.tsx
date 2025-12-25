"use client"

import type React from "react"
import { useState } from "react"
import { useAuth } from "../contexts/AuthContext"
import { useTheme } from "../contexts/ThemeContext"
import { useToast } from "../contexts/ToastContext"
import Layout from "../components/Layout/Layout"
import { Button } from "../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import {
  User,
  Building,
  Bell,
  Shield,
  Palette,
  Globe,
  Key,
  CreditCard,
  Users,
  Save,
  Eye,
  EyeOff,
  Upload,
  Trash2,
  Plus,
  Edit,
  Download,
  Sun,
  Moon,
} from "lucide-react"

const SettingsPage: React.FC = () => {
  const { user } = useAuth()
  const { theme, setTheme, actualTheme, toggleTheme } = useTheme()
  const { addToast } = useToast()
  const [activeTab, setActiveTab] = useState("profile")
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)

  const [profileData, setProfileData] = useState({
    name: user?.name || "",
    email: user?.email || "",
    phone: "+212 6XX XX XX XX",
    position: "Responsable RH",
    bio: "Passionné par les ressources humaines et l'innovation technologique.",
  })

  const [companyData, setCompanyData] = useState({
    name: user?.company || "",
    industry: "Technologie",
    size: "50-100",
    website: "https://techcorp.ma",
    address: "Casablanca, Maroc",
    description: "Entreprise technologique innovante spécialisée dans le développement web.",
  })

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    newApplications: true,
    interviewReminders: true,
    weeklyReports: true,
    marketingEmails: false,
  })

  const [securitySettings, setSecuritySettings] = useState({
    twoFactorAuth: false,
    sessionTimeout: "30",
    passwordExpiry: "90",
    ipRestriction: false,
  })

  const tabs = [
    { id: "profile", label: "Profil", icon: User },
    { id: "company", label: "Entreprise", icon: Building },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "security", label: "Sécurité", icon: Shield },
    { id: "appearance", label: "Apparence", icon: Palette },
    { id: "integrations", label: "Intégrations", icon: Globe },
    { id: "billing", label: "Facturation", icon: CreditCard },
    { id: "team", label: "Équipe", icon: Users },
  ]

  const handleSave = async (section: string) => {
    setLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 1000))
      addToast(`Paramètres ${section} sauvegardés avec succès`, "success")
    } catch (error) {
      addToast("Erreur lors de la sauvegarde", "error")
    } finally {
      setLoading(false)
    }
  }

  const integrations = [
    {
      name: "ReKrute",
      description: "Synchronisation automatique des offres d'emploi",
      status: "connected",
      logo: "/placeholder.svg?height=40&width=40&text=R",
    },
    {
      name: "Amaljob",
      description: "Publication automatique des postes",
      status: "connected",
      logo: "/placeholder.svg?height=40&width=40&text=A",
    },
    {
      name: "LinkedIn",
      description: "Sourcing de candidats et publication d'offres",
      status: "disconnected",
      logo: "/placeholder.svg?height=40&width=40&text=L",
    },
    {
      name: "Sage Paie",
      description: "Intégration avec le système de paie",
      status: "pending",
      logo: "/placeholder.svg?height=40&width=40&text=S",
    },
  ]

  const teamMembers = [
    {
      name: "Ahmed Benali",
      email: "ahmed@techcorp.ma",
      role: "Admin",
      status: "active",
      lastActive: "Il y a 2h",
      avatar: "/placeholder.svg?height=40&width=40&text=AB",
    },
    {
      name: "Fatima El Mansouri",
      email: "fatima@techcorp.ma",
      role: "Recruteur",
      status: "active",
      lastActive: "Il y a 1h",
      avatar: "/placeholder.svg?height=40&width=40&text=FE",
    },
    {
      name: "Youssef Tazi",
      email: "youssef@techcorp.ma",
      role: "RH Manager",
      status: "inactive",
      lastActive: "Il y a 2 jours",
      avatar: "/placeholder.svg?height=40&width=40&text=YT",
    },
  ]

  const renderTabContent = () => {
    switch (activeTab) {
      case "profile":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Informations personnelles</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center space-x-4 mb-6">
                  <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-2xl font-bold">{user?.username?.charAt(0).toUpperCase() || "U"}</span>
                  </div>
                  <div>
                    <Button variant="outline" size="sm">
                      <Upload className="w-4 h-4 mr-2" />
                      Changer la photo
                    </Button>
                    <p className="text-sm text-gray-500 mt-1">JPG, PNG max 2MB</p>
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nom complet
                    </label>
                    <input
                      type="text"
                      value={profileData.name}
                      onChange={(e) => setProfileData({ ...profileData, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Email</label>
                    <input
                      type="email"
                      value={profileData.email}
                      onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Téléphone</label>
                    <input
                      type="tel"
                      value={profileData.phone}
                      onChange={(e) => setProfileData({ ...profileData, phone: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Poste</label>
                    <input
                      type="text"
                      value={profileData.position}
                      onChange={(e) => setProfileData({ ...profileData, position: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Bio</label>
                  <textarea
                    rows={3}
                    value={profileData.bio}
                    onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>

                <Button onClick={() => handleSave("profil")} disabled={loading} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? "Sauvegarde..." : "Sauvegarder"}
                </Button>
              </CardContent>
            </Card>
          </div>
        )

      case "appearance":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Préférences d'apparence</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-4">Thème</h4>
                  <div className="grid grid-cols-3 gap-4">
                    <button
                      onClick={() => setTheme("light")}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        theme === "light"
                          ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                          : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                      }`}
                    >
                      <Sun className="w-6 h-6 mx-auto mb-2 text-yellow-500" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">Clair</span>
                    </button>
                    <button
                      onClick={() => setTheme("dark")}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        theme === "dark"
                          ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                          : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                      }`}
                    >
                      <Moon className="w-6 h-6 mx-auto mb-2 text-indigo-500" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">Sombre</span>
                    </button>
                    <button
                      onClick={() => setTheme("system")}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        theme === "system"
                          ? "border-purple-500 bg-purple-50 dark:bg-purple-900/20"
                          : "border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600"
                      }`}
                    >
                      <Palette className="w-6 h-6 mx-auto mb-2 text-purple-500" />
                      <span className="text-sm font-medium text-gray-900 dark:text-white">Système</span>
                    </button>
                  </div>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
                    Thème actuel : {actualTheme === "dark" ? "Sombre" : "Clair"}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-4">Langue</h4>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                    <option value="fr">Français</option>
                    <option value="ar">العربية</option>
                    <option value="en">English</option>
                  </select>
                </div>

                <div>
                  <h4 className="font-medium text-gray-900 dark:text-white mb-4">Fuseau horaire</h4>
                  <select className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent">
                    <option value="Africa/Casablanca">Casablanca (GMT+1)</option>
                    <option value="Europe/Paris">Paris (GMT+1)</option>
                    <option value="UTC">UTC (GMT+0)</option>
                  </select>
                </div>

                <Button onClick={() => handleSave("apparence")} disabled={loading} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? "Sauvegarde..." : "Sauvegarder"}
                </Button>
              </CardContent>
            </Card>
          </div>
        )

      case "company":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Informations de l'entreprise</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Nom de l'entreprise
                    </label>
                    <input
                      type="text"
                      value={companyData.name}
                      onChange={(e) => setCompanyData({ ...companyData, name: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Secteur d'activité
                    </label>
                    <select
                      value={companyData.industry}
                      onChange={(e) => setCompanyData({ ...companyData, industry: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="Technologie">Technologie</option>
                      <option value="Finance">Finance</option>
                      <option value="Santé">Santé</option>
                      <option value="Éducation">Éducation</option>
                      <option value="Commerce">Commerce</option>
                      <option value="Industrie">Industrie</option>
                    </select>
                  </div>
                </div>

                <Button onClick={() => handleSave("entreprise")} disabled={loading} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? "Sauvegarde..." : "Sauvegarder"}
                </Button>
              </CardContent>
            </Card>
          </div>
        )

      case "notifications":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Préférences de notification</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  {[
                    { key: "emailNotifications", label: "Notifications par email", desc: "Recevoir les notifications par email" },
                    { key: "pushNotifications", label: "Notifications push", desc: "Notifications dans le navigateur" },
                    { key: "newApplications", label: "Nouvelles candidatures", desc: "Alertes pour les nouvelles candidatures" },
                    { key: "interviewReminders", label: "Rappels d'entretien", desc: "Rappels avant les entretiens programmés" },
                    { key: "weeklyReports", label: "Rapports hebdomadaires", desc: "Résumé hebdomadaire des activités" },
                  ].map((item) => (
                    <div key={item.key} className="flex items-center justify-between">
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">{item.label}</h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{item.desc}</p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={notificationSettings[item.key as keyof typeof notificationSettings]}
                          onChange={(e) =>
                            setNotificationSettings({
                              ...notificationSettings,
                              [item.key]: e.target.checked,
                            })
                          }
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
                      </label>
                    </div>
                  ))}
                </div>

                <Button onClick={() => handleSave("notifications")} disabled={loading} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? "Sauvegarde..." : "Sauvegarder"}
                </Button>
              </CardContent>
            </Card>
          </div>
        )

      case "security":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Paramètres de sécurité</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium text-gray-900 dark:text-white">Authentification à deux facteurs</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Sécurité renforcée avec 2FA</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={securitySettings.twoFactorAuth}
                      onChange={(e) =>
                        setSecuritySettings({
                          ...securitySettings,
                          twoFactorAuth: e.target.checked,
                        })
                      }
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-purple-600"></div>
                  </label>
                </div>

                <div className="border-t pt-4 dark:border-gray-700">
                  <h4 className="font-medium text-gray-900 dark:text-white mb-4">Changer le mot de passe</h4>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Mot de passe actuel
                      </label>
                      <div className="relative">
                        <input
                          type={showPassword ? "text" : "password"}
                          className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                          placeholder="Mot de passe actuel"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPassword(!showPassword)}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        >
                          {showPassword ? (
                            <EyeOff className="h-4 w-4 text-gray-400" />
                          ) : (
                            <Eye className="h-4 w-4 text-gray-400" />
                          )}
                        </button>
                      </div>
                    </div>
                    <Button variant="outline">
                      <Key className="w-4 h-4 mr-2" />
                      Changer le mot de passe
                    </Button>
                  </div>
                </div>

                <Button onClick={() => handleSave("sécurité")} disabled={loading} className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                  <Save className="w-4 h-4 mr-2" />
                  {loading ? "Sauvegarde..." : "Sauvegarder"}
                </Button>
              </CardContent>
            </Card>
          </div>
        )

      case "integrations":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Intégrations</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {integrations.map((integration) => (
                    <div
                      key={integration.name}
                      className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center text-lg font-bold">
                          {integration.name.charAt(0)}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">{integration.name}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{integration.description}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            integration.status === "connected"
                              ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                              : integration.status === "pending"
                                ? "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
                                : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
                          }`}
                        >
                          {integration.status === "connected"
                            ? "Connecté"
                            : integration.status === "pending"
                              ? "En attente"
                              : "Déconnecté"}
                        </span>
                        <Button variant={integration.status === "connected" ? "outline" : "default"} size="sm">
                          {integration.status === "connected" ? "Déconnecter" : "Connecter"}
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )

      case "billing":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <CardTitle className="text-gray-900 dark:text-white">Plan actuel</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white">Plan Professional</h3>
                    <p className="text-gray-600 dark:text-gray-400">799 MAD/mois • Facturé annuellement</p>
                  </div>
                  <Button variant="outline">Changer de plan</Button>
                </div>

                <div className="grid md:grid-cols-3 gap-4 mb-6">
                  <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">200</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Candidats/mois</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">20</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Offres actives</div>
                  </div>
                  <div className="text-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">∞</div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">Utilisateurs</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )

      case "team":
        return (
          <div className="space-y-6">
            <Card className="dark:bg-gray-800 dark:border-gray-700">
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-gray-900 dark:text-white">Gestion de l'équipe</CardTitle>
                  <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Inviter un membre
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {teamMembers.map((member) => (
                    <div
                      key={member.email}
                      className="flex items-center justify-between p-4 border border-gray-200 dark:border-gray-700 rounded-lg"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                          {member.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div>
                          <h4 className="font-medium text-gray-900 dark:text-white">{member.name}</h4>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{member.email}</p>
                          <p className="text-xs text-gray-500">{member.lastActive}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-3">
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            member.status === "active"
                              ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                              : "bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-200"
                          }`}
                        >
                          {member.status === "active" ? "Actif" : "Inactif"}
                        </span>
                        <select
                          value={member.role}
                          className="px-3 py-1 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                          <option value="Admin">Admin</option>
                          <option value="Recruteur">Recruteur</option>
                          <option value="RH Manager">RH Manager</option>
                          <option value="Viewer">Viewer</option>
                        </select>
                        <Button variant="outline" size="sm">
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="w-4 h-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )

      default:
        return null
    }
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Paramètres</h1>
        <p className="text-gray-600 dark:text-gray-400">Gérez vos préférences et configurations</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="w-64 flex-shrink-0">
          <Card className="dark:bg-gray-800 dark:border-gray-700">
            <CardContent className="p-4">
              <nav className="space-y-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-colors ${
                      activeTab === tab.id
                        ? "bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300"
                        : "text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-900 dark:hover:text-gray-200"
                    }`}
                  >
                    <tab.icon className="w-5 h-5" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                ))}
              </nav>
            </CardContent>
          </Card>
        </div>

        {/* Content */}
        <div className="flex-1">{renderTabContent()}</div>
      </div>
    </Layout>
  )
}

export default SettingsPage
