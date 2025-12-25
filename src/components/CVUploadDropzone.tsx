
import React, { useState, useCallback, useRef } from 'react'
import { Card, CardContent } from "./ui/card"
import { Button } from "./ui/button"
import { Badge } from "./ui/badge"
import { Progress } from "./ui/progress"
import { 
  Upload, 
  FileText, 
  X, 
  CheckCircle, 
  AlertCircle,
  Download,
  Eye
} from "lucide-react"
import { validateCVFile, validateMultipleFiles } from "../utils/fileValidation"
import { usePendingCandidates } from "../hooks/usePendingCandidates"
import { useToast } from "../contexts/ToastContext"
import type { BulkUploadResult, SingleUploadResult } from '../types/api'

interface CVUploadDropzoneProps {
  onUploadComplete?: (results: SingleUploadResult | BulkUploadResult) => void;
  maxFiles?: number;
  destinationGroup?: string;
}
interface FileWithStatus {
  file: File
  id: string
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  progress?: number
  candidateId?: number
  cvUrl?: string
}

export const CVUploadDropzone: React.FC<CVUploadDropzoneProps> = ({
  onUploadComplete,
  maxFiles = 10,
  destinationGroup
}) => {
  const [files, setFiles] = useState<FileWithStatus[]>([])
  const [dragActive, setDragActive] = useState(false)
  const [uploading, setUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  
  const { uploadCV, bulkUploadCVs } = usePendingCandidates()
  const { addToast } = useToast()

  const generateFileId = () => `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const addFiles = useCallback((newFiles: File[]) => {
    const { valid, invalid } = validateMultipleFiles(newFiles)
    
    // Afficher les erreurs pour les fichiers invalides
    invalid.forEach(({ file, error }) => {
      addToast(`${file.name}: ${error}`, 'error')
    })

    // Vérifier la limite de fichiers
    const totalFiles = files.length + valid.length
    if (totalFiles > maxFiles) {
      addToast(`Maximum ${maxFiles} fichiers autorisés`, 'error')
      return
    }

    // Ajouter les fichiers valides
    const filesWithStatus: FileWithStatus[] = valid.map(file => ({
      file,
      id: generateFileId(),
      status: 'pending' as const
    }))

    setFiles(prev => [...prev, ...filesWithStatus])
  }, [files, maxFiles, addToast])

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const droppedFiles = Array.from(e.dataTransfer.files)
    addFiles(droppedFiles)
  }, [addFiles])

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const selectedFiles = Array.from(e.target.files)
      addFiles(selectedFiles)
    }
    // Reset input pour permettre la resélection du même fichier
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }, [addFiles])

  const removeFile = useCallback((fileId: string) => {
    setFiles(prev => prev.filter(f => f.id !== fileId))
  }, [])

  const uploadFiles = async () => {
    if (files.length === 0) return

    setUploading(true)
    
    try {
      const filesToUpload = files.filter(f => f.status === 'pending').map(f => f.file)
      
      if (filesToUpload.length === 0) {
        addToast('Aucun fichier à uploader', 'warning')
        return
      }

      // Marquer les fichiers comme en cours d'upload
      setFiles(prev => prev.map(f => 
        f.status === 'pending' 
          ? { ...f, status: 'uploading' as const, progress: 0 }
          : f
      ))

      let results: SingleUploadResult | BulkUploadResult;
      if (filesToUpload.length === 1) {
        // Upload simple
        results = await uploadCV(filesToUpload[0])
        
        if (results.success) {
          setFiles(prev => prev.map(f => 
            f.status === 'uploading'
              ? { 
                  ...f, 
                  status: 'success' as const, 
                  progress: 100,
                  candidateId: results.candidate?.id,
                  cvUrl: results.candidate?.cv_file_url
                }
              : f
          ))
          addToast('CV uploadé avec succès', 'success')
        }
      } else {
        // Upload en lot
        results = await bulkUploadCVs(filesToUpload)
        
        if (results.success) {
          // Mapper les résultats aux fichiers
          setFiles(prev => prev.map((f, index) => {
            if (f.status === 'uploading') {
              const result = results.results[index]
              return {
                ...f,
                status: result ? 'success' as const : 'error' as const,
                progress: 100,
                candidateId: result?.candidate_id,
                cvUrl: result?.cv_file_url,
                error: result ? undefined : 'Upload échoué'
              }
            }
            return f
          }))
          
          addToast(`${results.uploaded_count} CV(s) uploadé(s) avec succès`, 'success')
          
          if (results.error_count > 0) {
            addToast(`${results.error_count} erreur(s)`, 'warning')
          }
        }
      }

      onUploadComplete?.(results)
      
    } catch (error: any) {
      // Marquer tous les fichiers en cours comme erreur
      setFiles(prev => prev.map(f => 
        f.status === 'uploading'
          ? { ...f, status: 'error' as const, error: error.message }
          : f
      ))
      addToast(error.message, 'error')
    } finally {
      setUploading(false)
    }
  }

  const clearAll = () => {
    setFiles([])
  }

  const clearCompleted = () => {
    setFiles(prev => prev.filter(f => f.status !== 'success'))
  }

  const hasFiles = files.length > 0
  const hasErrors = files.some(f => f.status === 'error')
  const hasSuccess = files.some(f => f.status === 'success')
  const pendingFiles = files.filter(f => f.status === 'pending')

  return (
    <div className="space-y-6">
      {/* Zone de drop */}
      <Card
        className={`relative border-2 border-dashed transition-all duration-300 ${
          dragActive
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50 dark:hover:bg-gray-800'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <CardContent className="p-12">
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.txt,.doc,.docx"
            onChange={handleFileSelect}
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          <div className="text-center space-y-6">
            <div className="mx-auto w-20 h-20 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
              <Upload className="h-10 w-10 text-blue-600 dark:text-blue-300" />
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-2">
                Glissez-déposez vos CVs ici
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                ou cliquez pour sélectionner des fichiers
              </p>

              <Button 
                type="button" 
                size="lg"
                onClick={() => fileInputRef.current?.click()}
              >
                <Download className="h-5 w-5 mr-2" />
                Parcourir les fichiers
              </Button>
            </div>

            <div className="flex flex-wrap justify-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <span>📄 PDF, DOC, DOCX, TXT</span>
              <span>📏 Max 5MB par fichier</span>
              <span>📚 Max {maxFiles} fichiers</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Liste des fichiers */}
      {hasFiles && (
        <Card>
          <CardContent className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h4 className="font-semibold flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Fichiers sélectionnés ({files.length})
              </h4>
              <div className="flex gap-2">
                {hasSuccess && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={clearCompleted}
                  >
                    Effacer réussis
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={clearAll}
                >
                  Tout effacer
                </Button>
              </div>
            </div>

            <div className="space-y-3 max-h-60 overflow-y-auto">
              {files.map((fileItem) => (
                <div
                  key={fileItem.id}
                  className="flex items-center justify-between p-3 border rounded-lg"
                >
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className="flex-shrink-0">
                      {fileItem.status === 'success' && (
                        <CheckCircle className="h-5 w-5 text-green-600" />
                      )}
                      {fileItem.status === 'error' && (
                        <AlertCircle className="h-5 w-5 text-red-600" />
                      )}
                      {fileItem.status === 'uploading' && (
                        <div className="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent" />
                      )}
                      {fileItem.status === 'pending' && (
                        <FileText className="h-5 w-5 text-gray-400" />
                      )}
                    </div>

                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">
                        {fileItem.file.name}
                      </p>
                      <div className="flex items-center gap-2 text-xs text-gray-500">
                        <span>{formatFileSize(fileItem.file.size)}</span>
                        {fileItem.error && (
                          <span className="text-red-600">• {fileItem.error}</span>
                        )}
                        {fileItem.candidateId && (
                          <span className="text-green-600">• ID: {fileItem.candidateId}</span>
                        )}
                      </div>

                      {fileItem.status === 'uploading' && (
                        <Progress 
                          value={fileItem.progress || 0} 
                          className="mt-2 h-2" 
                        />
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Badge
                      variant={
                        fileItem.status === 'success' ? 'default' :
                        fileItem.status === 'error' ? 'destructive' :
                        fileItem.status === 'uploading' ? 'secondary' : 'outline'
                      }
                    >
                      {fileItem.status === 'success' && 'Uploadé'}
                      {fileItem.status === 'error' && 'Erreur'}
                      {fileItem.status === 'uploading' && 'Upload...'}
                      {fileItem.status === 'pending' && 'En attente'}
                    </Badge>

                    {fileItem.cvUrl && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(fileItem.cvUrl!, '_blank')}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                    )}

                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(fileItem.id)}
                      disabled={fileItem.status === 'uploading'}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      {hasFiles && (
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            {pendingFiles.length > 0 && `${pendingFiles.length} fichier(s) prêt(s)`}
            {hasSuccess && ` • ${files.filter(f => f.status === 'success').length} uploadé(s)`}
            {hasErrors && ` • ${files.filter(f => f.status === 'error').length} erreur(s)`}
          </div>

          <Button
            onClick={uploadFiles}
            disabled={uploading || pendingFiles.length === 0}
            size="lg"
          >
            {uploading ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent mr-2" />
                Upload en cours...
              </>
            ) : (
              <>
                <Upload className="h-4 w-4 mr-2" />
                Uploader {pendingFiles.length > 0 ? `(${pendingFiles.length})` : ''} CV(s)
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  )
}
