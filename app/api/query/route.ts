import { buildSystemPrompt, buildUserPrompt, formatContextSize } from "@/lib/rag-utils"

interface RetrievedDoc {
  id: string
  content: string
  similarity: number
  metadata: {
    date: string
    title: string
    source: string
  }
}

async function retrieveRelevantDocuments(query: string): Promise<RetrievedDoc[]> {
  try {
    const baseUrl = "http://localhost:8000"

    const response = await fetch(`${baseUrl}/search`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        query, 
        limit: 8, 
        threshold: 0.1
      }),
    })

    if (!response.ok) {
      console.error("[Search API] Error:", response.status, await response.text())
      return []
    }

    const data = await response.json()
    
    return data.results.map((doc: any) => ({
      id: doc.id,
      content: doc.content,
      similarity: doc.similarity,
      metadata: {
        date: doc.date,
        title: doc.title,
        source: doc.source,
        location: "Unknown",
        industry: "Industrial",
        incident_type: "Accident",
        severity: "Unknown"
      }
    }))
  } catch (error) {
    console.error("[Search API] Error retrieving documents:", error)
    return []
  }
}

async function generateWithGroq(query: string, context: string, groqKey: string): Promise<string> {
  const systemPrompt = buildSystemPrompt()
  const userPrompt = buildUserPrompt(query, { documents: [], query })

  const messages = [
    { role: "system", content: systemPrompt },
    { role: "user", content: `Context: ${context}\n\nQuestion: ${query}` }
  ]

  try {
    const response = await fetch('https://api.groq.com/openai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${groqKey}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        model: 'meta-llama/llama-4-scout-17b-16e-instruct', // This model definitely works with Groq API
        temperature: 0.7,
        max_tokens: 2000,
        stream: false
      })
    })

    if (!response.ok) {
      const error = await response.text()
      throw new Error(`Groq API error: ${response.status} - ${error}`)
    }

    const data = await response.json()
    return data.choices[0].message.content
  } catch (error) {
    console.error('Groq API call failed:', error)
    throw error
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

  return insights.length > 0 ? insights : [
    "Analysis based on similar historical incidents",
    "Patterns identified from industrial accident data", 
    "Evidence-based recommendations for prevention"
  ]
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

    // Check if search service is available
    try {
      const healthCheck = await fetch("http://localhost:8000/health")
      if (!healthCheck.ok) {
        return Response.json({ 
          error: "Search service unavailable. Please ensure the embedding service is running." 
        }, { status: 503 })
      }
    } catch (error) {
      return Response.json({ 
        error: "Search service not reachable. Start it with: python search_api.py" 
      }, { status: 503 })
    }

    const retrievedDocs = await retrieveRelevantDocuments(query)
    console.log(`[RAG] Retrieved ${retrievedDocs.length} documents for: "${query}"`)

    if (retrievedDocs.length === 0) {
      return Response.json({
        answer: "No relevant incidents found in the database for your query. Try rephrasing or asking about different types of industrial accidents.",
        sources: [],
        insights: ["No matching documents found", "Try broader search terms", "Consider different incident types"],
        metadata: {
          resultCount: 0,
          queryTime: Date.now() - startTime,
          method: "semantic-search-no-results",
          documentsRetrieved: 0,
          contextSize: "0 documents",
        },
      })
    }

    // Build context from retrieved documents
    const context = retrievedDocs.map((doc, index) => 
      `INCIDENT ${index + 1}:
Title: ${doc.metadata.title}
Date: ${doc.metadata.date}
Source: ${doc.metadata.source}
Relevance: ${(doc.similarity * 100).toFixed(1)}%
Content: ${doc.content}`
    ).join('\n\n')

    // Generate answer using Groq API directly
    const answer = await generateWithGroq(query, context, groqKey)

    const queryTime = Date.now() - startTime

    const sources = retrievedDocs.map((doc) => ({
      id: doc.metadata.source,
      type: doc.metadata.incident_type,
      location: doc.metadata.location,
      date: doc.metadata.date,
      title: doc.metadata.title,
      similarity: (doc.similarity * 100).toFixed(1) + "%",
    }))

    const insights = extractKeyInsights(answer)

    console.log(`[RAG] Query completed in ${queryTime}ms with ${sources.length} sources`)

    return Response.json({
      answer,
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
  } catch (error: any) {
    console.error("[RAG] Query error:", error)
    
    return Response.json({ 
      error: error?.message || "Failed to process query. Please try again." 
    }, { status: 500 })
  }
}