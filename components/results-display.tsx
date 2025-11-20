import { Card } from "@/components/ui/card"
import { AlertCircle, CheckCircle, AlertTriangle, Zap, Lightbulb } from "lucide-react"

interface Source {
  id: string
  type: string
  location: string
  date: string
  similarity: string
}

interface ResultsDisplayProps {
  results: {
    answer?: string
    sources?: Source[]
    insights?: string[]
    metadata?: {
      resultCount: number
      queryTime: number
      method: string
      documentsRetrieved: number
      contextSize?: string
    }
    error?: string
  }
  isLoading: boolean
}

export default function ResultsDisplay({ results, isLoading }: ResultsDisplayProps) {
  if (results.error) {
    return (
      <Card className="p-6 border-red-500/20 bg-red-500/5">
        <div className="flex gap-3">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-foreground">Error</h3>
            <p className="text-sm text-muted-foreground mt-1">{results.error}</p>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <div className="space-y-4">
      {/* AI Response */}
      <Card className="p-6 bg-gradient-to-br from-blue-500/5 to-transparent border-blue-500/20">
        <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
          <CheckCircle className="h-4 w-4 text-blue-500" />
          Analysis
        </h3>
        <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
          {results.answer || "Processing your query..."}
        </p>
      </Card>

      {/* Key Insights */}
      {results.insights && results.insights.length > 0 && (
        <Card className="p-6 bg-amber-500/5 border-amber-500/20">
          <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-amber-500" />
            Key Insights
          </h3>
          <ul className="space-y-2">
            {results.insights.slice(0, 3).map((insight, i) => (
              <li key={i} className="text-xs text-muted-foreground flex gap-2">
                <span className="text-amber-500 font-bold flex-shrink-0">•</span>
                <span>{insight}</span>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {/* Sources */}
      {results.sources && results.sources.length > 0 && (
        <Card className="p-6">
          <h3 className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-500" />
            Incident Sources ({results.sources.length})
          </h3>
          <div className="space-y-2 max-h-80 overflow-y-auto">
            {results.sources.map((source, i) => (
              <div
                key={i}
                className="text-xs p-3 rounded bg-muted border border-border hover:border-blue-500/30 transition-colors"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <p className="font-semibold text-foreground">{source.id}</p>
                    <p className="text-muted-foreground mt-1">
                      <span className="inline-block px-2 py-0.5 bg-blue-500/10 text-blue-600 rounded text-xs mr-2">
                        {source.type}
                      </span>
                      {source.location} • {source.date}
                    </p>
                  </div>
                  <div className="text-right">
                    <span className="text-blue-500 font-mono text-xs font-semibold">{source.similarity}%</span>
                    <p className="text-muted-foreground text-xs">match</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Performance Metadata */}
      {results.metadata && (
        <Card className="p-4 bg-muted/30">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground flex items-center gap-1">
                <Zap className="h-3 w-3" />
                <span>Query Time</span>
              </p>
              <p className="text-sm font-semibold text-foreground mt-1">{results.metadata.queryTime}ms</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Documents Retrieved</p>
              <p className="text-sm font-semibold text-foreground mt-1">
                {results.metadata.documentsRetrieved} of {results.metadata.resultCount}
              </p>
            </div>
            {results.metadata.contextSize && (
              <div className="col-span-2">
                <p className="text-xs text-muted-foreground">Context Size</p>
                <p className="text-sm font-semibold text-foreground mt-1">{results.metadata.contextSize}</p>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  )
}
