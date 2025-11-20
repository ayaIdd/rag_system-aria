"use client"

import type React from "react"

import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Search } from "lucide-react"

interface QueryInterfaceProps {
  query: string
  onChange: (query: string) => void
  onSubmit: (e: React.FormEvent) => void
  isLoading: boolean
}

export default function QueryInterface({ query, onChange, onSubmit, isLoading }: QueryInterfaceProps) {
  return (
    <Card className="p-6">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label htmlFor="query" className="block text-sm font-medium text-foreground mb-2">
            Ask about accidents or incidents
          </label>
          <textarea
            id="query"
            placeholder="E.g., What are the most common causes of chemical accidents?"
            value={query}
            onChange={(e) => onChange(e.target.value)}
            className="w-full min-h-24 px-4 py-2 rounded-md border border-input bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={isLoading}
          />
        </div>
        <Button type="submit" disabled={isLoading || !query.trim()} className="w-full gap-2">
          <Search className="h-4 w-4" />
          {isLoading ? "Searching..." : "Search Database"}
        </Button>
      </form>
    </Card>
  )
}
