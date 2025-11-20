import fs from "fs"
import path from "path"

interface VectorEntry {
  id: string
  content: string
  embedding: number[]
  metadata: {
    date: string
    location: string
    industry: string
    incident_type: string
    severity: string
    source: string
  }
  embedding_dimension: number
}

function loadVectorStore(): VectorEntry[] {
  try {
    const vectorPath = path.join(process.cwd(), "public/data/aria_vectors.json")
    const data = fs.readFileSync(vectorPath, "utf-8")
    return JSON.parse(data)
  } catch (error) {
    console.error("Error loading vector store:", error)
    return []
  }
}

function cosineSimilarity(vec1: number[], vec2: number[]): number {
  if (vec1.length !== vec2.length) return 0

  let dotProduct = 0
  let mag1 = 0
  let mag2 = 0

  for (let i = 0; i < vec1.length; i++) {
    dotProduct += vec1[i] * vec2[i]
    mag1 += vec1[i] * vec1[i]
    mag2 += vec2[i] * vec2[i]
  }

  mag1 = Math.sqrt(mag1)
  mag2 = Math.sqrt(mag2)

  if (mag1 === 0 || mag2 === 0) return 0

  return dotProduct / (mag1 * mag2)
}

function simpleEmbedding(text: string, dimension = 384): number[] {
  const textLower = text.toLowerCase()
  const words = textLower.split(/\s+/)

  const embedding = new Array(dimension).fill(0)

  for (const word of words) {
    if (word.length > 2) {
      const wordHash = word.split("").reduce((sum, c) => sum + c.charCodeAt(0), 0)
      const idx = wordHash % dimension

      embedding[idx] += 1.0 / (word.length * words.length + 1)
    }
  }

  // Normalize
  const magnitude = Math.sqrt(embedding.reduce((sum, x) => sum + x * x, 0))
  if (magnitude > 0) {
    return embedding.map((x) => x / magnitude)
  }

  return embedding
}

export async function POST(request: Request) {
  try {
    const { query, limit = 5, threshold = 0.1 } = await request.json()

    if (!query || query.trim().length === 0) {
      return Response.json({ error: "Query cannot be empty" }, { status: 400 })
    }

    const vectorStore = loadVectorStore()

    if (vectorStore.length === 0) {
      return Response.json({ error: "Vector store not loaded. Please run embeddings generation." }, { status: 500 })
    }

    // Generate embedding for query
    const queryEmbedding = simpleEmbedding(query, vectorStore[0].embedding_dimension || 384)

    // Search using cosine similarity
    const results = vectorStore
      .map((doc) => ({
        ...doc,
        similarity: cosineSimilarity(queryEmbedding, doc.embedding),
      }))
      .filter((doc) => doc.similarity >= threshold)
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, limit)
      .map(({ embedding, embedding_dimension, ...rest }) => rest)

    return Response.json({
      query,
      results,
      totalResults: results.length,
      method: "semantic-search",
      timestamp: new Date().toISOString(),
    })
  } catch (error) {
    console.error("Search error:", error)
    return Response.json({ error: "Failed to perform semantic search" }, { status: 500 })
  }
}
