import fs from "fs"
import path from "path"

interface IndexEntry {
  id: string
  content: string
  metadata: {
    date: string
    location: string
    industry: string
    incident_type: string
    severity: string
    source: string
  }
}

function loadIndex(): IndexEntry[] {
  try {
    const indexPath = path.join(process.cwd(), "public/data/aria_index.json")
    const data = fs.readFileSync(indexPath, "utf-8")
    return JSON.parse(data)
  } catch (error) {
    console.error("Error loading index:", error)
    return []
  }
}

function simpleTextSimilarity(query: string, text: string): number {
  const queryWords = query.toLowerCase().split(/\s+/)
  const textLower = text.toLowerCase()

  let matches = 0
  for (const word of queryWords) {
    if (word.length > 2 && textLower.includes(word)) {
      matches++
    }
  }

  return matches / Math.max(queryWords.length, 1)
}

export async function POST(request: Request) {
  try {
    const { query, limit = 5 } = await request.json()

    if (!query || query.trim().length === 0) {
      return Response.json({ error: "Query cannot be empty" }, { status: 400 })
    }

    const index = loadIndex()

    if (index.length === 0) {
      return Response.json({ error: "Index not loaded. Please run the data pipeline first." }, { status: 500 })
    }

    // Score and rank results based on text similarity
    const results = index
      .map((entry) => ({
        ...entry,
        score: simpleTextSimilarity(query, entry.content),
      }))
      .filter((entry) => entry.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)

    return Response.json({
      query,
      results,
      totalResults: results.length,
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Retrieval error:", error)
    return Response.json({ error: "Failed to retrieve documents" }, { status: 500 })
  }
}
