import type React from "react"
import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import { AuthProvider } from "./contexts/AuthContext"
import { ThemeProvider } from "./contexts/ThemeContext"
import { ToastProvider } from "./contexts/ToastContext"
import ProtectedRoute from "./components/ProtectedRoute"

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

import "./App.css"

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AuthProvider>
        <ToastProvider>
          <Router>
            <div className="App">
              <Routes>
                {/* Routes publiques */}
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="/contact" element={<ContactPage />} />
                <Route path="/pricing" element={<PricingPage />} />

                {/* Routes protégées */}
                <Route
                  path="/dashboard"
                  element={
                    <ProtectedRoute>
                      <DashboardPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/jobs"
                  element={
                    <ProtectedRoute>
                      <JobsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/jobs/create"
                  element={
                    <ProtectedRoute>
                      <CreateJobPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/jobs/:id"
                  element={
                    <ProtectedRoute>
                      <ViewJobPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/jobs/:id/edit"
                  element={
                    <ProtectedRoute>
                      <EditJobPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/candidates"
                  element={
                    <ProtectedRoute>
                      <CandidatesPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/candidates/:id"
                  element={
                    <ProtectedRoute>
                      <ViewCandidatePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/analytics"
                  element={
                    <ProtectedRoute>
                      <AnalyticsPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/ai-assistant"
                  element={
                    <ProtectedRoute>
                      <AIAssistantPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/settings"
                  element={
                    <ProtectedRoute>
                      <SettingsPage />
                    </ProtectedRoute>
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
