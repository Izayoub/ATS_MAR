"use client"

import type React from "react"

import { Card, CardContent } from "../ui/card"
import { Button } from "../ui/button"
import { Input } from "../ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select"
import { Search } from "lucide-react"
import { useState } from "react"

interface CandidateFiltersProps {
  onSearch: (term: string) => void
  onFilterChange: (key: string, value: string) => void
  searchTerm: string
  experienceLevel: string
  location: string
  skills: string
}

export function CandidateFiltersComponent({
  onSearch,
  onFilterChange,
  searchTerm,
  experienceLevel,
  location,
  skills,
}: CandidateFiltersProps) {
  const [localSearchTerm, setLocalSearchTerm] = useState(searchTerm)

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch(localSearchTerm)
  }

  return (
    <Card className="bg-card border-border">
      <CardContent className="p-6">
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
            <Input
              type="text"
              placeholder="Rechercher un candidat..."
              value={localSearchTerm}
              onChange={(e) => setLocalSearchTerm(e.target.value)}
              className="pl-10 pr-20 h-12 text-base bg-input border-border"
            />
            <Button
              type="submit"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              Rechercher
            </Button>
          </div>
        </form>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Niveau d'expérience</label>
            <Select value={experienceLevel} onValueChange={(value) => onFilterChange("experience_level", value)}>
              <SelectTrigger className="bg-input border-border">
                <SelectValue placeholder="Tous les niveaux" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tous les niveaux</SelectItem>
                <SelectItem value="junior">Junior</SelectItem>
                <SelectItem value="middle">Confirmé</SelectItem>
                <SelectItem value="senior">Senior</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Localisation</label>
            <Input
              type="text"
              placeholder="Ville, région..."
              value={location}
              onChange={(e) => onFilterChange("location", e.target.value)}
              className="bg-input border-border"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Compétences</label>
            <Input
              type="text"
              placeholder="React, Python, etc."
              value={skills}
              onChange={(e) => onFilterChange("skills", e.target.value)}
              className="bg-input border-border"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
