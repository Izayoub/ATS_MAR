"use client"

import { Card, CardContent } from "../ui/card"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"
import { Mail, Phone, MapPin, Briefcase, GraduationCap, Eye, Trash2, Target } from "lucide-react"
import type { Candidate } from "../../types/api"
import type { CandidateGroup } from "../../types/api";
interface CandidateCardProps {
  candidate: Candidate
  onStartMatching: (candidate: Candidate) => void
  onViewDetails: (candidateId: number) => void
  onDelete: (candidateId: number) => void
  groups: CandidateGroup[]
  onAddToGroup: (candidateId: number, groupId: number) => Promise<void>
}

export function CandidateCard({ candidate, onStartMatching, onViewDetails, onDelete }: CandidateCardProps) {
  const getStatusColor = (status: Candidate["status"]) => {
    switch (status) {
      case "new":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
      case "reviewed":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200"
      case "interviewed":
        return "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
      case "hired":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
      case "rejected":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
      default:
        return "bg-gray-100 text-gray-800"
    }
  }

  const getStatusText = (status: Candidate["status"]) => {
    switch (status) {
      case "new":
        return "Nouveau"
      case "reviewed":
        return "Examiné"
      case "interviewed":
        return "Entretien"
      case "hired":
        return "Embauché"
      case "rejected":
        return "Rejeté"
      default:
        return status
    }
  }

  return (
    <Card className="bg-card border-border hover:shadow-lg transition-all duration-200 hover:border-primary/20">
      <CardContent className="p-6">
        <div className="flex justify-between items-start">
          <div className="flex items-start gap-4 flex-1">
            <div className="w-16 h-16 bg-gradient-to-br from-primary to-accent rounded-full flex items-center justify-center text-white font-bold text-xl shadow-md">
              {candidate.first_name[0]}
              {candidate.last_name[0]}
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <h3 className="text-xl font-bold text-foreground">{candidate.full_name}</h3>
                <Badge className={`${getStatusColor(candidate.status)} border-0`}>
                  {getStatusText(candidate.status)}
                </Badge>
                {candidate.global_match_score && (
                  <Badge className="bg-accent/10 text-accent border-accent/20">
                    {Math.round(candidate.global_match_score)}% IA
                  </Badge>
                )}
              </div>

              <p className="text-muted-foreground mb-4 font-medium">{candidate.current_position}</p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm text-muted-foreground mb-4">
                <div className="flex items-center gap-2">
                  <Mail className="h-4 w-4 text-primary" />
                  <span className="truncate">{candidate.email}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Phone className="h-4 w-4 text-primary" />
                  <span>{candidate.phone}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-primary" />
                  <span>{candidate.city}</span>
                </div>
              </div>

              <div className="flex items-center gap-6 text-sm text-muted-foreground mb-4">
                {candidate.experience_summary && (
                  <div className="flex items-center gap-2">
                    <Briefcase className="h-4 w-4 text-accent" />
                    <span>
                      {candidate.experience_summary.years} ans - {candidate.experience_summary.level}
                    </span>
                  </div>
                )}
                <div className="flex items-center gap-2">
                  <GraduationCap className="h-4 w-4 text-accent" />
                  <span>{candidate.education_level}</span>
                </div>
              </div>

              {candidate.skills_summary && candidate.skills_summary.top_technical.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4">
                  {candidate.skills_summary.top_technical.slice(0, 5).map((skill, index) => (
                    <Badge
                      key={index}
                      variant="outline"
                      className="bg-primary/5 text-primary border-primary/20 text-xs"
                    >
                      {skill}
                    </Badge>
                  ))}
                  {candidate.skills_summary.technical_count > 5 && (
                    <Badge variant="outline" className="bg-muted text-muted-foreground text-xs">
                      +{candidate.skills_summary.technical_count - 5} autres
                    </Badge>
                  )}
                </div>
              )}

              <div className="flex items-center gap-4 text-xs text-muted-foreground">
                <span>Inscrit le {new Date(candidate.created_at).toLocaleDateString("fr-FR")}</span>
                {candidate.last_matching_date && (
                  <>
                    <span>•</span>
                    <span>Dernier matching: {new Date(candidate.last_matching_date).toLocaleDateString("fr-FR")}</span>
                  </>
                )}
              </div>
            </div>
          </div>

          <div className="flex flex-col gap-2 ml-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => onStartMatching(candidate)}
              className="text-primary hover:text-primary-foreground hover:bg-primary border-primary/20"
            >
              <Target className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={() => onViewDetails(candidate.id)} className="hover:bg-muted">
              <Eye className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDelete(candidate.id)}
              className="text-destructive hover:text-destructive-foreground hover:bg-destructive border-destructive/20"
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
