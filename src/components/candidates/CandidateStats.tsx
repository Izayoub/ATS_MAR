import { Card, CardContent } from "../ui/card"
import { Users, CheckCircle, Clock, Brain } from "lucide-react"
import type { Candidate } from "../../types/api"

interface CandidateStatsProps {
  candidates: Candidate[]
  totalCount: number
}

export function CandidateStats({ candidates, totalCount }: CandidateStatsProps) {
  const hiredCount = candidates.filter((c) => c.status === "hired").length

  const newCandidatesCount = candidates.filter((c) => {
    const weekAgo = new Date()
    weekAgo.setDate(weekAgo.getDate() - 7)
    return new Date(c.created_at) > weekAgo
  }).length

  const avgScore =
    candidates.length > 0
      ? Math.round(
          candidates.filter((c) => c.global_match_score).reduce((acc, c) => acc + (c.global_match_score || 0), 0) /
            candidates.filter((c) => c.global_match_score).length,
        )
      : 0

  const stats = [
    {
      title: "Total candidats",
      value: totalCount,
      icon: Users,
      color: "text-chart-1",
      bgColor: "bg-chart-1/10",
    },
    {
      title: "Candidats embauchés",
      value: hiredCount,
      icon: CheckCircle,
      color: "text-chart-2",
      bgColor: "bg-chart-2/10",
    },
    {
      title: "Nouveaux (7j)",
      value: newCandidatesCount,
      icon: Clock,
      color: "text-chart-3",
      bgColor: "bg-chart-3/10",
    },
    {
      title: "Score IA moyen",
      value: `${avgScore}%`,
      icon: Brain,
      color: "text-chart-4",
      bgColor: "bg-chart-4/10",
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {stats.map((stat, index) => (
        <Card key={index} className="bg-card border-border">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground mb-1">{stat.title}</p>
                <p className="text-3xl font-bold text-foreground">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
