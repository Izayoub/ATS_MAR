"use client"

import { useState, useEffect, useCallback } from "react"

interface ApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

interface ApiOptions {
  immediate?: boolean
}

export function useApi<T>(apiFunction: () => Promise<T>, options: ApiOptions = { immediate: true }) {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }))

    try {
      const data = await apiFunction()
      setState({ data, loading: false, error: null })
      return data
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Une erreur est survenue"
      setState({ data: null, loading: false, error: errorMessage })
      throw error
    }
  }, [apiFunction])

  useEffect(() => {
    if (options.immediate) {
      execute()
    }
  }, [execute, options.immediate])

  return {
    ...state,
    execute,
    reset: () => setState({ data: null, loading: false, error: null }),
  }
}
