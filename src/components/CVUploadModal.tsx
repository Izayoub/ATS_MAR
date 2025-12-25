"use client"

import type React from "react"
import { useState } from "react"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "./ui/dialog"
import { Button } from "./ui/button"
import { Upload, X } from "lucide-react"
import { CVUploadDropzone } from "./CVUploadDropzone"
import type { Candidate } from "../types/api"

interface CVUploadModalProps {
  isOpen: boolean
  onClose: () => void
  onSuccess?: (candidate: Candidate) => void;
  onUploadComplete?: (results: any) => void
  maxFiles?: number
  destinationGroup?: string
}

export const CVUploadModal: React.FC<CVUploadModalProps> = ({
  isOpen,
  onClose,
  onUploadComplete,
  maxFiles = 10,
  destinationGroup,
}) => {
  const [hasUploads, setHasUploads] = useState(false)

  const handleUploadComplete = (results: any) => {
    setHasUploads(true)
    onUploadComplete?.(results)
  }

  const handleClose = () => {
    setHasUploads(false)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Upload className="h-5 w-5" />
            Importer des CVs
          </DialogTitle>
          <DialogDescription>
            Glissez-déposez ou sélectionnez des fichiers CV à importer dans le système. Les candidats seront créés
            automatiquement avec extraction des données.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <CVUploadDropzone
            onUploadComplete={handleUploadComplete}
            maxFiles={maxFiles}
            destinationGroup={destinationGroup}
          />
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            <X className="h-4 w-4 mr-2" />
            Fermer
          </Button>
          {hasUploads && <Button onClick={handleClose}>Terminer</Button>}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
