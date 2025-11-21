import { readFileSync } from 'fs'
import { join } from 'path'

const API_BASE_URL = process.env.SEARCH_API_URL || 'http://localhost:8000'

export interface SearchResult {
  id: string
  title: string
  date: string
  content: string
  similarity: number
  source: string
}

export interface SearchResponse {
  query: string
  results: SearchResult[]
  total: number
  processing_time: number
  method: string
}

export interface SystemStats {
  total_incidents: number
  embedding_dimension: number
  model: string
  generated_at: string
}

class SearchService {
  private apiBase: string

  constructor(apiBase: string = API_BASE_URL) {
    this.apiBase = apiBase
  }

  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.apiBase}/health`)
      return response.ok
    } catch (error) {
      console.error('Health check failed:', error)
      return false
    }
  }

  async search(
    query: string, 
    limit: number = 8, 
    threshold: number = 0.05
  ): Promise<SearchResponse> {
    try {
      const response = await fetch(`${this.apiBase}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          limit,
          threshold
        })
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || `Search failed: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('Search error:', error)
      throw error
    }
  }

  async getStats(): Promise<SystemStats> {
    try {
      const response = await fetch(`${this.apiBase}/stats`)
      if (!response.ok) {
        throw new Error(`Failed to get stats: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Stats error:', error)
      throw error
    }
  }
}

// Singleton instance
export const searchService = new SearchService()

// Legacy function for backward compatibility
export async function POST(request: Request) {
  try {
    const { query, limit = 8, threshold = 0.05 } = await request.json()

    if (!query?.trim()) {
      return Response.json({ error: "Query required" }, { status: 400 })
    }

    // Check if search service is healthy
    const isHealthy = await searchService.healthCheck()
    if (!isHealthy) {
      return Response.json({ 
        error: "Search service unavailable. Please ensure the Python API is running."
      }, { status: 503 })
    }

    console.log(`[Search] Query: "${query}"`)

    const result = await searchService.search(query, limit, threshold)

    console.log(`[Search] Found ${result.total} results in ${result.processing_time.toFixed(3)}s`)

    return Response.json({
      ...result,
      timestamp: new Date().toISOString(),
    })
  } catch (error: any) {
    console.error("[Search] Error:", error)
    return Response.json({ 
      error: error?.message || "Search failed" 
    }, { status: 500 })
  }
}