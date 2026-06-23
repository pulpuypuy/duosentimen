import { Routes, Route, Navigate } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import ScrapingPage from './pages/ScrapingPage'
import PreprocessingPage from './pages/PreprocessingPage'
import TrainingPage from './pages/TrainingPage'
import HasilAnalisisPage from './pages/HasilAnalisisPage'
import PrediksiPage from './pages/PrediksiPage'
import ProtectedRoute from './components/ProtectedRoute'

export default function App() {
  return (
    <Routes>
      <Route path="/login"         element={<LoginPage />} />
      <Route path="/dashboard"     element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/scraping"      element={<ProtectedRoute><ScrapingPage /></ProtectedRoute>} />
      <Route path="/preprocessing" element={<ProtectedRoute><PreprocessingPage /></ProtectedRoute>} />
      <Route path="/training"      element={<ProtectedRoute><TrainingPage /></ProtectedRoute>} />
      <Route path="/analisis"      element={<ProtectedRoute><HasilAnalisisPage /></ProtectedRoute>} />
      <Route path="/prediksi"      element={<ProtectedRoute><PrediksiPage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

