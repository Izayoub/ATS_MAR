"use client"

import { Button } from "../ui/button"
import { Target, Upload, FileText, Brain, FolderPlus } from "lucide-react"

interface CandidateHeaderProps {
  onImportMultiple: () => void
  onCreateGroup: () => void
  onToggleUnprocessed: () => void
  onExtractInfo: () => void
  onImportCV: () => void
  onMatching: () => void
  unprocessedCount: number
  isExtracting: boolean
}

export function CandidateHeader({
  onImportMultiple,
  onCreateGroup,
  onToggleUnprocessed,
  onExtractInfo,
  onImportCV,
  onMatching,
  unprocessedCount,
  isExtracting,
}: CandidateHeaderProps) {
  return (
    <div className="bg-card border-b border-border">
      <div className="px-6 py-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">Candidats</h1>
            <p className="text-muted-foreground text-lg">Gérez vos candidats et lancez le matching IA</p>
          </div>

          <div className="flex gap-4">
            {/* Import Actions */}
            <div className="flex gap-2">
              <Button
                onClick={onImportMultiple}
                variant="outline"
                className="border-border hover:bg-muted bg-transparent"
              >
                <Upload className="h-4 w-4 mr-2" />
                Import Multiple
              </Button>
              <Button onClick={onImportCV} className="bg-secondary hover:bg-secondary/90 text-secondary-foreground">
                <Upload className="h-4 w-4 mr-2" />
                Importer CV
              </Button>
            </div>

            {/* Management Actions */}
            <div className="flex gap-2">
              <Button onClick={onCreateGroup} variant="outline" className="border-border hover:bg-muted bg-transparent">
                <FolderPlus className="h-4 w-4 mr-2" />
                Nouveau Groupe
              </Button>
              <Button
                onClick={onToggleUnprocessed}
                variant="outline"
                className="border-border hover:bg-muted bg-transparent"
              >
                <FileText className="h-4 w-4 mr-2" />
                CVs Non Traités ({unprocessedCount})
              </Button>
            </div>

            {/* AI Actions */}
            <div className="flex gap-2">
              <Button
                onClick={onExtractInfo}
                disabled={isExtracting || unprocessedCount === 0}
                className="bg-accent hover:bg-accent/90 text-accent-foreground"
              >
                <Brain className="h-4 w-4 mr-2" />
                {isExtracting ? "Extraction..." : "Extraire Infos"}
              </Button>
              <Button onClick={onMatching} className="bg-primary hover:bg-primary/90 text-primary-foreground">
                <Target className="h-4 w-4 mr-2" />
                Matching IA
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
