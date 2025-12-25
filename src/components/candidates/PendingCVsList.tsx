import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"
import { FileText, Eye, Trash2, Sparkles, Download } from "lucide-react"
import { usePendingCandidates } from "../../hooks/usePendingCandidates"
import { useToast } from "../../contexts/ToastContext"

interface PendingCVsListProps {
  isVisible: boolean
  onToggleVisibility: () => void
}

export const PendingCVsList: React.FC<PendingCVsListProps> = ({ 
  isVisible, 
  onToggleVisibility 
}) => {
  const { 
    pendingCandidates, 
    loading, 
    error, 
    extractCandidate 
  } = usePendingCandidates()
  const { addToast } = useToast()

  const handleExtractCandidate = async (candidateId: number) => {
    try {
      const response = await extractCandidate(candidateId)
      if (response.success) {
        addToast("Extraction déclenchée avec succès", "success")
      }
    } catch (error: any) {
      addToast(error.message, "error")
    }
  }

  const formatFileSize = (path: string) => {
    // Estimation basique - dans un vrai cas, vous devriez stocker la taille
    return "~500 KB"
  }

  if (!isVisible) return null

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-5 w-5" />
          CVs En Attente d'Extraction
          <Badge variant="secondary">{pendingCandidates.length}</Badge>
        </CardTitle>
        <Button variant="ghost" size="sm" onClick={onToggleVisibility}>
          Masquer
        </Button>
      </CardHeader>
      <CardContent>
        {loading ? (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-blue-600 border-t-transparent" />
          </div>
        ) : error ? (
          <div className="text-center py-8 text-red-600">
            <p>Erreur: {error}</p>
          </div>
        ) : pendingCandidates.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <FileText className="h-16 w-16 mx-auto mb-4 opacity-30" />
            <p className="text-lg">Aucun CV en attente d'extraction</p>
            <p className="text-sm">Les CVs uploadés apparaîtront ici</p>
          </div>
        ) : (
          <div className="space-y-3">
            {pendingCandidates.map((candidate) => (
              <div
                key={candidate.id}
                className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800"
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-4 h-4 rounded-full ${
                      candidate.status === "pending_extraction"
                        ? "bg-yellow-400"
                        : candidate.status === "processing"
                          ? "bg-blue-500 animate-pulse"
                          : "bg-red-500"
                    }`}
                  />
                  <div>
                    <p className="font-medium">{candidate.cv_file_path}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      {formatFileSize(candidate.cv_file_path)} • 
                      {new Date(candidate.upload_date).toLocaleDateString("fr-FR")}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant={
                      candidate.status === "pending_extraction" 
                        ? "secondary" 
                        : candidate.status === "processing" 
                          ? "default" 
                          : "destructive"
                    }
                  >
                    {candidate.status === "pending_extraction" 
                      ? "En attente" 
                      : candidate.status === "processing" 
                        ? "Traitement" 
                        : "Échec"}
                  </Badge>
                  
                  {candidate.cv_file_url && (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => window.open(candidate.cv_file_url!, '_blank')}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  )}
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExtractCandidate(candidate.id)}
                    disabled={candidate.is_extracted}
                    className="flex items-center gap-1"
                  >
                    <Sparkles className="h-4 w-4" />
                    {candidate.is_extracted ? "Extrait" : "Extraire"}
                  </Button>
                  
                  <Button variant="outline" size="sm">
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  )
}