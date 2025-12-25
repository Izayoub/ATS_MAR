export const validateCVFile = (file: File): { valid: boolean; error?: string } => {
  const allowedTypes = ['application/pdf', 'text/plain', 'application/msword', 
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
  const maxSize = 5 * 1024 * 1024 // 5MB

  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Format de fichier non autorisé. Veuillez utiliser PDF, TXT, DOC ou DOCX.'
    }
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'Fichier trop volumineux. Taille maximum : 5MB.'
    }
  }

  return { valid: true }
}

export const validateMultipleFiles = (files: File[]): { 
  valid: File[], 
  invalid: Array<{file: File, error: string}> 
} => {
  const valid: File[] = []
  const invalid: Array<{file: File, error: string}> = []

  files.forEach(file => {
    const validation = validateCVFile(file)
    if (validation.valid) {
      valid.push(file)
    } else {
      invalid.push({ file, error: validation.error! })
    }
  })

  return { valid, invalid }
}