"use client"

import { useState, useEffect } from "react"
import candidateService from "../services/candidateService"
import type { Candidate, CandidateNote, TimelineEvent, JobMatch } from "../types/api"

export const useCandidate = (id: number) => {
  const [candidate, setCandidate] = useState<Candidate | null>(null)
  const [notes, setNotes] = useState<CandidateNote[]>([])
  const [timeline, setTimeline] = useState<TimelineEvent[]>([])
  const [matches, setMatches] = useState<JobMatch[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [notesLoading, setNotesLoading] = useState(false)
  const [timelineLoading, setTimelineLoading] = useState(false)
  const [matchingLoading, setMatchingLoading] = useState(false)

  const fetchCandidate = async () => {
    try {
      setLoading(true)
      setError(null)
      const candidateData = await candidateService.getCandidateById(id)
      setCandidate(candidateData)
    } catch (err: any) {
      setError(err.message || "Erreur lors du chargement du candidat")
    } finally {
      setLoading(false)
    }
  }

  const fetchNotes = async () => {
    try {
      setNotesLoading(true)
      const notesData = await candidateService.getCandidateNotes(id)
      setNotes(notesData)
    } catch (err: any) {
      console.error("Erreur lors du chargement des notes:", err)
    } finally {
      setNotesLoading(false)
    }
  }

  const fetchTimeline = async () => {
    try {
      setTimelineLoading(true)
      const timelineData = await candidateService.getCandidateTimeline(id)
      setTimeline(timelineData)
    } catch (err: any) {
      console.error("Erreur lors du chargement de la timeline:", err)
    } finally {
      setTimelineLoading(false)
    }
  }

  const findMatches = async () => {
    try {
      setMatchingLoading(true)
      const matchData = await candidateService.findMatchingJobs(id)
      setMatches(matchData.matches)
    } catch (err: any) {
      console.error("Erreur lors du matching:", err)
    } finally {
      setMatchingLoading(false)
    }
  }

  const updateStatus = async (newStatus: Candidate["status"]) => {
    if (!candidate) return

    try {
      const updatedCandidate = await candidateService.updateCandidateStatus(id, newStatus)
      setCandidate(updatedCandidate)
      // Refresh timeline to show status change
      fetchTimeline()
      return updatedCandidate
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de la mise à jour du statut")
    }
  }

  const addNote = async (content: string, noteType = "note") => {
    try {
      const newNote = await candidateService.addCandidateNote(id, content, noteType)
      setNotes((prev) => [newNote, ...prev])
      // Refresh timeline to show new note
      fetchTimeline()
      return newNote
    } catch (err: any) {
      throw new Error(err.message || "Erreur lors de l'ajout de la note")
    }
  }

  useEffect(() => {
    if (id) {
      fetchCandidate()
    }
  }, [id])

  return {
    candidate,
    notes,
    timeline,
    matches,
    loading,
    error,
    notesLoading,
    timelineLoading,
    matchingLoading,
    fetchNotes,
    fetchTimeline,
    findMatches,
    updateStatus,
    addNote,
    refetch: fetchCandidate,
  }
}
