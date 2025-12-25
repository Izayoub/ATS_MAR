import React, { useState } from 'react'
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Sparkles, AlertCircle } from "lucide-react"
import { usePendingCandidates } from "../hooks/usePendingCandidates"
import { useToast } from "../contexts/ToastContext"

export const ExtractDataButton: React.FC = () => {
  const [isExtracting, setIsExtracting] = useState(false)
  const { pendingCandidates, extractCandidate } = usePendingCandidates()
  const { addToast } = useToast()

  const extractableCandidates = pendingCandidates.filter(
    c => c.status === 'pending_extraction' && !c.is_extracted
  )

  const handleBulkExtraction = async () => {
    if (extractableCandidates.length === 0) {
      addToast('Aucun CV à extraire', 'warning')
      return
    }

    setIsExtracting(true)
    let successCount = 0
    let errorCount = 0

    for (const candidate of extractableCandidates) {
      try {
        await extractCandidate(candidate.id)
        successCount++
        
        // Petite pause entre les extractions
        await new Promise(resolve => setTimeout(resolve, 500))
      } catch (error: any) {
        console.error(`Erreur extraction candidat ${candidate.id}:`, error)
        errorCount++
      }
    }

    if (successCount > 0) {
      addToast(`${successCount} extraction(s) déclenchée(s) avec succès`, 'success')
    }
    if (errorCount > 0) {
      addToast(`${errorCount} erreur(s) lors de l'extraction`, 'error')
    }

    setIsExtracting(false)
  }

  if (extractableCandidates.length === 0) {
    return (
      <Button disabled variant="outline" className="flex items-center gap-2">
        <Sparkles className="h-4 w-4" />
        Aucun CV à extraire
      </Button>
    )
  }

  return (
    <Button
      onClick={handleBulkExtraction}
      disabled={isExtracting}
      className="flex items-center gap-2 relative"
    >
      {isExtracting ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent" />
          Extraction en cours...
        </>
      ) : (
        <>
          <Sparkles className="h-4 w-4" />
          Extraire Infos
          <Badge variant="secondary" className="ml-2">
            {extractableCandidates.length}
          </Badge>
        </>
      )}
    </Button>
  )
}