"use client"

import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { Badge } from "../ui/badge"
import { Users2 } from "lucide-react"

interface CandidateGroup {
  id: number
  name: string
  description?: string
  color: string
  candidateCount: number
}

interface CandidateGroupsProps {
  groups: CandidateGroup[]
  selectedGroup: string
  totalCount: number
  onGroupFilter: (groupId: string) => void
}

export function CandidateGroups({ groups, selectedGroup, totalCount, onGroupFilter }: CandidateGroupsProps) {
  return (
    <Card className="bg-card border-border">
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-foreground">
          <Users2 className="h-5 w-5 text-primary" />
          Groupes de Candidats
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-3">
          <Badge
            variant={selectedGroup === "" ? "default" : "outline"}
            className={`cursor-pointer px-4 py-2 text-sm font-medium transition-colors ${
              selectedGroup === ""
                ? "bg-primary text-primary-foreground hover:bg-primary/90"
                : "border-border hover:bg-muted text-foreground"
            }`}
            onClick={() => onGroupFilter("")}
          >
            Tous ({totalCount})
          </Badge>
          {groups.map((group) => (
            <Badge
              key={group.id}
              variant={selectedGroup === group.id.toString() ? "default" : "outline"}
              className={`cursor-pointer px-4 py-2 text-sm font-medium transition-colors ${
                selectedGroup === group.id.toString() ? "text-white" : "border-border hover:bg-muted text-foreground"
              }`}
              style={{
                backgroundColor: selectedGroup === group.id.toString() ? group.color : "transparent",
                borderColor: group.color,
                color: selectedGroup === group.id.toString() ? "white" : group.color,
              }}
              onClick={() => onGroupFilter(group.id.toString())}
            >
              {group.name} ({group.candidateCount})
            </Badge>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
