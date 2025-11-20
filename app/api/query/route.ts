import { generateText } from "ai"
import { createGroq } from "@ai-sdk/groq"
import { buildSystemPrompt, buildUserPrompt, formatContextSize } from "@/lib/rag-utils"

interface RetrievedDoc {
  id: string
  content: string
  similarity: number
  metadata: {
    date: string
    location: string
    industry: string
    incident_type: string
    severity: string
    source: string
  }
}

async function retrieveRelevantDocuments(query: string): Promise<RetrievedDoc[]> {
  try {
    const baseUrl = process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : "http://localhost:3000"

    const response = await fetch(`${baseUrl}/api/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, limit: 8, threshold: 0.05 }),
    })

    if (!response.ok) {
      console.error("[v0] Search API error:", response.status)
      return []
    }

    const data = await response.json()
    return data.results || []
  } catch (error) {
    console.error("[v0] Error retrieving documents:", error)
    return []
  }
}

function extractKeyInsights(answer: string): string[] {
  const insights: string[] = []
  const lines = answer.split("\n")

  for (const line of lines) {
    if (/^\d+\.|^[-•*]/.test(line.trim())) {
      const insight = line.replace(/^\d+\.|^[-•*]/, "").trim()
      if (insight.length > 20) {
        insights.push(insight)
      }
    }
  }

  return insights
}

export async function POST(request: Request) {
  try {
    const { query, groqKey } = await request.json()

    if (!groqKey || groqKey.trim().length === 0) {
      return Response.json({ error: "Groq API key is required" }, { status: 400 })
    }

    if (!query || query.trim().length === 0) {
      return Response.json({ error: "Query cannot be empty" }, { status: 400 })
    }

    const startTime = Date.now()

    const retrievedDocs = await retrieveRelevantDocuments(query)
    console.log(`[v0] Retrieved ${retrievedDocs.length} documents`)

    const groq = createGroq({
      apiKey: groqKey,
    })

    const systemPrompt = buildSystemPrompt()
    const userPrompt = buildUserPrompt(query, {
      documents: retrievedDocs,
      query,
    })

    const { text } = await generateText({
      model: groq("llama-3.1-8b-instant"),
      system: systemPrompt,
      prompt: userPrompt,
      temperature: 0.7,
      maxTokens: 2000,
    })

    const queryTime = Date.now() - startTime

    const sources = retrievedDocs.map((doc) => ({
      id: doc.metadata.source,
      type: doc.metadata.incident_type,
      location: doc.metadata.location,
      date: doc.metadata.date,
      similarity: (doc.similarity * 100).toFixed(1),
    }))

    const insights = extractKeyInsights(text)

    return Response.json({
      answer: text,
      sources,
      insights,
      metadata: {
        resultCount: sources.length,
        queryTime,
        method: "rag-with-semantic-search",
        documentsRetrieved: retrievedDocs.length,
        contextSize: formatContextSize(retrievedDocs),
      },
    })
  } catch (error) {
    console.error("[v0] Query error:", error)
    return Response.json({ error: "Failed to process query. Please try again." }, { status: 500 })
  }
}
