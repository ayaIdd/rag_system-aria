"use client"

import type React from "react"

import { useState } from "react"
import { Search, AlertCircle, Database, Sparkles, Key } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import ResultsDisplay from "@/components/results-display"

export default function Page() {
  const [groqKey, setGroqKey] = useState("")
  const [query, setQuery] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [keyConfigured, setKeyConfigured] = useState(false)

  const handleConfigureKey = (e: React.FormEvent) => {
    e.preventDefault()
    if (groqKey.trim()) {
      setKeyConfigured(true)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim() || !groqKey.trim()) return

    setIsLoading(true)
    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, groqKey }),
      })
      const data = await response.json()
      setResults(data)
    } catch (error) {
      console.error("[v0] Query error:", error)
      setResults({
        error: "Failed to process query. Please try again.",
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (!keyConfigured) {
    return (
      <main className="min-h-screen bg-background flex items-center justify-center">
        <Card className="w-full max-w-md p-8">
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-2">
              <Key className="h-6 w-6 text-blue-500" />
              <h1 className="text-2xl font-bold text-foreground">Configure Groq API</h1>
            </div>
            <p className="text-muted-foreground text-sm">
              Enter your Groq API key to start querying the ARIA database. Get a free key at{" "}
              <a
                href="https://console.groq.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:underline"
              >
                console.groq.com
              </a>
            </p>
          </div>
          <form onSubmit={handleConfigureKey} className="space-y-4">
            <div>
              <label htmlFor="key" className="block text-sm font-medium text-foreground mb-2">
                Groq API Key
              </label>
              <Input
                id="key"
                type="password"
                placeholder="gsk_..."
                value={groqKey}
                onChange={(e) => setGroqKey(e.target.value)}
                className="w-full"
              />
            </div>
            <Button type="submit" disabled={!groqKey.trim()} className="w-full">
              Continue
            </Button>
          </form>
        </Card>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="mb-2 flex items-center gap-2">
            <Database className="h-8 w-8 text-blue-500" />
            <h1 className="text-3xl font-bold text-foreground">ARIA RAG System</h1>
          </div>
          <p className="text-muted-foreground">
            Query 53,000+ industrial accidents with AI-powered analysis and evidence-based recommendations
          </p>
        </div>
      </div>

      {/* Main Content */}
      <div className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="grid gap-8 lg:grid-cols-3">
          {/* Query Input */}
          <div className="lg:col-span-2">
            <Card className="p-6">
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="query" className="block text-sm font-medium text-foreground mb-2">
                    Ask about accidents or incidents
                  </label>
                  <Textarea
                    id="query"
                    placeholder="E.g., What are the most common causes of chemical accidents? Or: What preventive measures reduce manufacturing incidents?"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    className="min-h-24"
                    disabled={isLoading}
                  />
                </div>
                <div className="flex gap-2">
                  <Button type="submit" disabled={isLoading || !query.trim()} className="flex-1 gap-2">
                    <Search className="h-4 w-4" />
                    {isLoading ? "Analyzing database..." : "Search & Analyze"}
                  </Button>
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => {
                      setKeyConfigured(false)
                      setGroqKey("")
                    }}
                  >
                    Change Key
                  </Button>
                </div>
              </form>
            </Card>

            {/* Results */}
            {results && (
              <div className="mt-6">
                <ResultsDisplay results={results} isLoading={isLoading} />
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Info Card */}
            <Card className="p-4 border-blue-500/20 bg-blue-500/5">
              <div className="flex gap-3">
                <AlertCircle className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-foreground text-sm">About ARIA</h3>
                  <p className="text-xs text-muted-foreground mt-1">
                    Comprehensive database of 53,000+ industrial accidents and incidents from France. Our RAG system
                    uses semantic search and AI analysis to provide evidence-based insights.
                  </p>
                </div>
              </div>
            </Card>

            {/* Features Card */}
            <Card className="p-4">
              <h3 className="font-semibold text-foreground text-sm mb-3 flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                RAG Capabilities
              </h3>
              <ul className="space-y-2 text-xs text-muted-foreground">
                <li className="flex gap-2">
                  <span className="text-blue-500 font-bold">•</span>
                  <span>Semantic search across incidents</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-500 font-bold">•</span>
                  <span>AI-powered contextual analysis</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-500 font-bold">•</span>
                  <span>Incident pattern identification</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-500 font-bold">•</span>
                  <span>Evidence-based recommendations</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-blue-500 font-bold">•</span>
                  <span>Cited sources & similarity scores</span>
                </li>
              </ul>
            </Card>

            {/* Sample Queries */}
            <Card className="p-4">
              <h3 className="font-semibold text-foreground text-sm mb-3">Try asking:</h3>
              <div className="space-y-2">
                {[
                  "What causes fires in warehouses?",
                  "Chemical exposure prevention measures",
                  "Common manufacturing incident patterns",
                  "Equipment failure risk factors",
                ].map((example, i) => (
                  <button
                    key={i}
                    onClick={() => setQuery(example)}
                    className="w-full text-left text-xs p-2 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
                  >
                    "{example}"
                  </button>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </main>
  )
}
