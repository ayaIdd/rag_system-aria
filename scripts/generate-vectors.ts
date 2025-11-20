import fs from "fs"
import path from "path"

interface Incident {
  id: string
  date: string
  location: string
  industry: string
  incident_type: string
  description: string
  severity: string
  causes: string
  preventive_measures: string
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

export function generateVectors() {
  console.log("[v0] Generating vector embeddings for ARIA incidents...")

  const dataPath = path.join(process.cwd(), "public/data/aria_dataset.json")

  if (!fs.existsSync(dataPath)) {
    console.error("[v0] Dataset not found at", dataPath)
    return
  }

  const rawData = fs.readFileSync(dataPath, "utf-8")
  const incidents: Incident[] = JSON.parse(rawData)

  const vectorStore: any[] = []

  for (const incident of incidents) {
    const fullText = `
      Description: ${incident.description}
      Causes: ${incident.causes}
      Prevention: ${incident.preventive_measures}
      Type: ${incident.incident_type}
      Industry: ${incident.industry}
      Location: ${incident.location}
      Severity: ${incident.severity}
    `

    const embedding = simpleEmbedding(fullText)

    vectorStore.push({
      id: incident.id,
      content: fullText.trim(),
      embedding,
      metadata: {
        date: incident.date,
        location: incident.location,
        industry: incident.industry,
        incident_type: incident.incident_type,
        severity: incident.severity,
        source: `ARIA-${incident.id}`,
      },
      embedding_dimension: embedding.length,
    })
  }

  const outputPath = path.join(process.cwd(), "public/data/aria_vectors_embedded.json")
  const outputDir = path.dirname(outputPath)

  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true })
  }

  fs.writeFileSync(outputPath, JSON.stringify(vectorStore, null, 2))

  console.log(`[v0] Generated embeddings for ${vectorStore.length} incidents`)
  console.log(`[v0] Saved to ${outputPath}`)
}

if (require.main === module) {
  generateVectors()
}
