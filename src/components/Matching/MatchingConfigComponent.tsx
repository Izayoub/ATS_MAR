import React, { useState, useEffect, useMemo, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card'
import { Button } from '../ui/button'
import { Badge } from '../ui/badge'
import { Slider } from '../ui/slider'
import { 
  Settings, 
  RotateCcw, 
  Save, 
  AlertCircle, 
  Info, 
  Brain,
  Zap,
  Target,
  Loader2,
  CheckCircle
} from 'lucide-react'
import { type MatchingWeights, DEFAULT_MATCHING_WEIGHTS } from '../../types/api'
import jobService from '../../services/JobService'

interface MatchingConfigProps {
  jobId: number // Si 0 ou null, mode création
  currentWeights?: MatchingWeights
  currentPrompt?: string
  isCustomized?: boolean
  onConfigUpdated?: (updated: boolean) => void
  onConfigChange?: (config: { matching_weights?: MatchingWeights, system_prompt?: string }) => void // Pour mode création
  className?: string
  mode?: 'creation' | 'edit' // Nouveau prop pour différencier les modes
}

const MatchingConfigComponent: React.FC<MatchingConfigProps> = ({
  jobId,
  currentWeights,
  currentPrompt = '',
  isCustomized = false,
  onConfigUpdated,
  onConfigChange, // Callback pour le mode création
  className = '',
  mode = jobId > 0 ? 'edit' : 'creation'
}) => {
  // États locaux
  const [weights, setWeights] = useState<MatchingWeights>(
    currentWeights || DEFAULT_MATCHING_WEIGHTS
  )
  const [prompt, setPrompt] = useState(currentPrompt)
  const [isExpanded, setIsExpanded] = useState(mode === 'creation')
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string>('')
  const [successMessage, setSuccessMessage] = useState<string>('')
  const [configCustomized, setConfigCustomized] = useState(isCustomized)

  const isCreationMode = mode === 'creation' || !jobId || jobId === 0

  // Memoize the default weights comparison to avoid infinite loops
  const defaultWeightsString = useMemo(() => 
    JSON.stringify(currentWeights || DEFAULT_MATCHING_WEIGHTS), 
    [currentWeights]
  )

  // Memoize hasUnsavedChanges to avoid recalculation on every render
  const hasUnsavedChanges = useMemo(() => {
    const weightsChanged = JSON.stringify(weights) !== defaultWeightsString
    const promptChanged = prompt !== currentPrompt
    return weightsChanged || promptChanged
  }, [weights, defaultWeightsString, prompt, currentPrompt])

  // Memoize the config object to prevent unnecessary onConfigChange calls
  const configToSend = useMemo(() => {
    const hasCustomConfig = hasUnsavedChanges || Boolean(prompt.trim())
    return {
      matching_weights: hasCustomConfig ? weights : undefined,
      system_prompt: prompt.trim() || undefined
    }
  }, [weights, prompt, hasUnsavedChanges])

  // Charger la configuration au montage (seulement en mode édition)
  useEffect(() => {
    if (!isCreationMode) {
      loadConfig()
    }
  }, [jobId, isCreationMode])

  // En mode création, notifier le parent des changements - Fixed with useCallback and proper dependencies
  useEffect(() => {
    if (isCreationMode && onConfigChange) {
      onConfigChange(configToSend)
    }
  }, [isCreationMode, onConfigChange, configToSend])

  const loadConfig = async () => {
    if (isCreationMode) return
    
    setLoading(true)
    setError('')
    
    try {
      const response = await jobService.getMatchingConfig(jobId)
      
      if (response.success && response.config) {
        setWeights(response.config.effective_weights || DEFAULT_MATCHING_WEIGHTS)
        setPrompt(response.config.system_prompt || '')
        setConfigCustomized(response.config.weights_customized || response.config.prompt_customized)
      }
    } catch (err: any) {
      setError(err.message || 'Erreur lors du chargement de la configuration')
    } finally {
      setLoading(false)
    }
  }

  // Gestion des changements de poids
  const handleWeightChange = useCallback((field: keyof MatchingWeights, value: number[]) => {
    setWeights(prev => ({
      ...prev,
      [field]: value[0] / 100 // Convertir de 0-100 à 0-1
    }))
    setError('')
    setSuccessMessage('')
  }, [])

  // Normaliser les poids pour qu'ils totalisent 100%
  const normalizeWeights = useCallback((inputWeights: MatchingWeights): MatchingWeights => {
    const total = Object.values(inputWeights).reduce((sum, weight) => sum + weight, 0)
    if (total === 0) return DEFAULT_MATCHING_WEIGHTS
    
    return Object.keys(inputWeights).reduce((normalized, key) => ({
      ...normalized,
      [key]: inputWeights[key as keyof MatchingWeights] / total
    }), {} as MatchingWeights)
  }, [])

  // Sauvegarder les modifications (seulement en mode édition)
  const handleSave = async () => {
    if (isCreationMode) {
      // En mode création, juste notifier le parent
      const normalizedWeights = normalizeWeights(weights)
      onConfigChange?.({
        matching_weights: normalizedWeights,
        system_prompt: prompt.trim() || undefined
      })
      setSuccessMessage('Configuration mise à jour localement')
      setTimeout(() => setSuccessMessage(''), 2000)
      return
    }

    setSaving(true)
    setError('')
    setSuccessMessage('')
    
    try {
      const normalizedWeights = normalizeWeights(weights)
      const response = await jobService.updateMatchingConfig(jobId, {
        matching_weights: normalizedWeights,
        system_prompt: prompt.trim() || undefined
      })
      
      if (response.success) {
        setWeights(normalizedWeights)
        setConfigCustomized(true)
        setSuccessMessage('Configuration sauvegardée avec succès')
        onConfigUpdated?.(true)
        
        // Effacer le message après 3 secondes
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la sauvegarde')
    } finally {
      setSaving(false)
    }
  }

  // Réinitialiser aux valeurs par défaut
  const handleReset = async () => {
    if (isCreationMode) {
      // En mode création, réinitialiser localement
      setWeights(DEFAULT_MATCHING_WEIGHTS)
      setPrompt('')
      setConfigCustomized(false)
      setSuccessMessage('Configuration réinitialisée')
      onConfigChange?.({
        matching_weights: undefined,
        system_prompt: undefined
      })
      setTimeout(() => setSuccessMessage(''), 2000)
      return
    }

    setSaving(true)
    setError('')
    setSuccessMessage('')
    
    try {
      const response = await jobService.resetMatchingConfig(jobId)
      
      if (response.success) {
        setWeights(response.default_weights || DEFAULT_MATCHING_WEIGHTS)
        setPrompt('')
        setConfigCustomized(false)
        setSuccessMessage('Configuration réinitialisée')
        onConfigUpdated?.(false)
        
        setTimeout(() => setSuccessMessage(''), 3000)
      }
    } catch (err: any) {
      setError(err.message || 'Erreur lors de la réinitialisation')
    } finally {
      setSaving(false)
    }
  }

  // Handle prompt change with useCallback to prevent unnecessary re-renders
  const handlePromptChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setPrompt(e.target.value)
    setError('')
    setSuccessMessage('')
  }, [])

  // Labels pour les champs
  const weightLabels = {
    technical_skills: 'Compétences techniques',
    soft_skills: 'Compétences transversales',
    experience: 'Expérience professionnelle',
    education: 'Formation & diplômes'
  }

  const weightDescriptions = {
    technical_skills: 'Technologies, langages, outils spécialisés',
    soft_skills: 'Communication, leadership, adaptabilité',
    experience: 'Années d\'expérience et projets réalisés',
    education: 'Diplômes, certifications, formations'
  }

  // Calculate total weights percentage
  const totalWeightPercent = useMemo(() => 
    Math.round(Object.values(weights).reduce((sum, w) => sum + w, 0) * 100), 
    [weights]
  )

  if (loading && !isCreationMode) {
    return (
      <Card className={`border-2 border-purple-200 dark:border-purple-800 ${className}`}>
        <CardContent className="flex items-center justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-purple-600" />
          <span className="ml-2">Chargement de la configuration...</span>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={`border-2 border-purple-200 dark:border-purple-800 ${className}`}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Brain className="w-5 h-5 text-purple-600" />
            Configuration du matching IA
            {isCreationMode && (
              <Badge variant="secondary" className="bg-blue-100 text-blue-700">
                Mode création
              </Badge>
            )}
            {!isCreationMode && configCustomized && (
              <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                Personnalisé
              </Badge>
            )}
          </CardTitle>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <Settings className="w-4 h-4 mr-2" />
            {isExpanded ? 'Masquer' : 'Configurer'}
          </Button>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="space-y-6 pt-0">
          {/* Messages de succès/erreur */}
          {successMessage && (
            <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <CheckCircle className="w-5 h-5 text-green-500" />
                <div className="text-sm text-green-800 dark:text-green-200">
                  {successMessage}
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <AlertCircle className="w-5 h-5 text-red-500" />
                <div className="text-sm text-red-800 dark:text-red-200">
                  {error}
                </div>
              </div>
            </div>
          )}

          {/* Info sur la personnalisation */}
          <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
            <div className="flex items-start gap-3">
              <Info className="w-5 h-5 text-blue-500 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-blue-800 dark:text-blue-200 mb-1">
                  {isCreationMode ? 'Configuration préliminaire' : 'Matching personnalisé'}
                </p>
                <p className="text-blue-700 dark:text-blue-300">
                  {isCreationMode 
                    ? 'Ajustez les paramètres qui seront appliqués lors de la création de l\'offre.'
                    : 'Ajustez l\'importance de chaque critère et personnalisez les instructions IA pour cette offre spécifique.'
                  }
                </p>
              </div>
            </div>
          </div>

          {/* Configuration des poids */}
          <div className="space-y-4">
            <h4 className="font-semibold flex items-center gap-2">
              <Target className="w-4 h-4" />
              Pondération des critères
            </h4>
            
            {Object.entries(weights).map(([key, value]) => (
              <div key={key} className="space-y-2">
                <div className="flex justify-between items-center">
                  <div>
                    <label className="text-sm font-medium">
                      {weightLabels[key as keyof MatchingWeights]}
                    </label>
                    <p className="text-xs text-gray-500">
                      {weightDescriptions[key as keyof MatchingWeights]}
                    </p>
                  </div>
                  <Badge variant="outline">
                    {Math.round(value * 100)}%
                  </Badge>
                </div>
                
                <Slider
                  value={[value * 100]}
                  onValueChange={(newValue) => handleWeightChange(key as keyof MatchingWeights, newValue)}
                  max={100}
                  min={0}
                  step={5}
                  className="w-full"
                />
              </div>
            ))}
            
            {/* Vérification total = 100% */}
            <div className="bg-gray-50 dark:bg-gray-800 rounded p-3">
              <div className="flex justify-between items-center text-sm">
                <span>Total des poids:</span>
                <span className={`font-medium ${
                  Math.abs(totalWeightPercent - 100) > 1
                    ? 'text-amber-600' 
                    : 'text-green-600'
                }`}>
                  {totalWeightPercent}%
                </span>
              </div>
              {Math.abs(totalWeightPercent - 100) > 1 && (
                <p className="text-xs text-amber-600 mt-1 flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  Les poids seront automatiquement normalisés à 100%
                </p>
              )}
            </div>
          </div>

          {/* Prompt système personnalisé */}
          <div className="space-y-3">
            <h4 className="font-semibold flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Instructions IA personnalisées
            </h4>
            <textarea
              value={prompt}
              onChange={handlePromptChange}
              placeholder="Laissez vide pour utiliser le prompt par défaut, ou personnalisez les instructions pour l'analyse des candidats..."
              className="w-full h-32 px-3 py-2 border rounded-lg resize-none focus:ring-2 focus:ring-purple-500 focus:border-transparent dark:bg-gray-800 dark:border-gray-600"
            />
            <p className="text-xs text-gray-500">
              Ces instructions guideront l'IA dans l'évaluation des candidats pour cette offre spécifique.
            </p>
          </div>

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <Button 
              onClick={handleSave} 
              disabled={saving || (!hasUnsavedChanges && !error)}
              className="flex-1"
            >
              {saving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Save className="w-4 h-4 mr-2" />
              )}
              {saving ? 'Sauvegarde...' : (isCreationMode ? 'Appliquer' : 'Sauvegarder')}
            </Button>
            
            <Button 
              variant="outline" 
              onClick={handleReset}
              disabled={saving || (!configCustomized && !hasUnsavedChanges)}
            >
              {saving ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RotateCcw className="w-4 h-4 mr-2" />
              )}
              Réinitialiser
            </Button>
          </div>

          {/* Warning sur les changements non sauvés */}
          {!isCreationMode && hasUnsavedChanges && !successMessage && (
            <div className="bg-amber-50 dark:bg-amber-900/20 rounded-lg p-3">
              <div className="flex items-center gap-2 text-amber-800 dark:text-amber-200">
                <AlertCircle className="w-4 h-4" />
                <span className="text-sm font-medium">
                  Modifications non sauvegardées
                </span>
              </div>
            </div>
          )}
        </CardContent>
      )}
    </Card>
  )
}

export default MatchingConfigComponent