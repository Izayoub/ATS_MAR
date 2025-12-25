import type React from "react"
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom"
import { AuthProvider } from "./contexts/AuthContext"
import { ThemeProvider } from "./contexts/ThemeContext"
import { ToastProvider } from "./contexts/ToastContext"
import ProtectedRoute from "./components/ProtectedRoute"
import PublicRoute from "./components/PublicRoute"

// Pages
import HomePage from "./pages/HomePage"
import LoginPage from "./pages/LoginPage"
import RegisterPage from "./pages/RegisterPage"
import DashboardPage from "./pages/DashboardPage"
import AboutPage from "./pages/AboutPage"
import ContactPage from "./pages/ContactPage"
import JobsPage from "./pages/JobsPage"
import CandidatesPage from "./pages/CandidatesPage"
import AnalyticsPage from "./pages/AnalyticsPage"
import SettingsPage from "./pages/SettingsPage"
import PricingPage from "./pages/PricingPage"
import NotFoundPage from "./pages/NotFoundPage"
import CreateJobPage from "./pages/CreateJobPage"
import ViewJobPage from "./pages/ViewJobPage"
import EditJobPage from "./pages/EditJobPage"
import ViewCandidatePage from "./pages/ViewCandidatePage"
import AIAssistantPage from "./pages/AIAssistantPage"
import MatchingPage from "./pages/MatchingPage"

import "./App.css"
import Matching1Page from "./pages/Matching1Page"

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <Router>
            <div className="App">
              <Routes>
                {/* Routes publiques - Home page reste accessible même si connecté */}
                <Route path="/" element={<HomePage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/contact" element={<ContactPage />} />
                <Route path="/pricing" element={<PricingPage />} />

                {/* Routes d'authentification - redirect si déjà connecté */}
                <Route
                  path="/login"
                  element={
                    <PublicRoute>
                      <LoginPage />
                    </PublicRoute>
                  }
                />
                <Route
                  path="/register"
                  element={
                    <PublicRoute>
                      <RegisterPage />
                    </PublicRoute>
                  }
                />

                {/* Routes protégées - require authentication */}
                <Route
                  path="/dashboard"
                  element={
                    /*<ProtectedRoute>*/
                      <DashboardPage />
                    /*</ProtectedRoute>*/
                  }
                />
                <Route
                  path="/jobs"
                  element={
                    /*<ProtectedRoute>*/
                      <JobsPage />
                    /*</ProtectedRoute> */
                  }
                />
                <Route
                  path="/jobs/create"
                  element={
                    /*<ProtectedRoute>*/
                      <CreateJobPage />
                    /*</ProtectedRoute>  */
                  }
                />
                <Route
                  path="/jobs/:id"
                  element={
                    /*<ProtectedRoute> $*/
                      <ViewJobPage />
                    /*</ProtectedRoute> */
                  }
                />
                <Route
                  path="/jobs/:id/edit"
                  element={
                    /*<ProtectedRoute>*/
                      <EditJobPage />
                    /*</ProtectedRoute>$  */
                  }
                />
                <Route
                  path="/candidates"
                  element={
                    /*<ProtectedRoute>*/
                      <CandidatesPage />
                    /*</ProtectedRoute>*/
                  }
                />
                <Route
                  path="/candidates/:id"
                  element={
                    /*<ProtectedRoute>*/
                      <ViewCandidatePage />
                    /*</ProtectedRoute> */
                  }
                />
                <Route
                  path="/matching"
                  element={
                    /*<ProtectedRoute> */
                      <MatchingPage />
                    /*</ProtectedRoute> */
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    /*<ProtectedRoute>*/
                      <AnalyticsPage />
                    /*</ProtectedRoute> */
                  }
                />
                <Route
                  path="/ai-assistant"
                  element={
                    /*<ProtectedRoute> */
                      <AIAssistantPage />
                    /*</ProtectedRoute> */
                  }
                />
                <Route
                  path="/matching1"
                  element={
                    /*<ProtectedRoute> */
                      <Matching1Page />
                    /*</ProtectedRoute>*/
                  }
                />
                <Route
                  path="/settings"
                  element={
                    /*<ProtectedRoute>*/
                      <SettingsPage />
                    /*</ProtectedRoute>*/
                  }
                />

                {/* Route 404 */}
                <Route path="*" element={<NotFoundPage />} />
              </Routes>
            </div>
          </Router>
        </ToastProvider>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App