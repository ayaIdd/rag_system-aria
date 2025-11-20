import fs from "fs"
import path from "path"

interface HealthStatus {
  status: "healthy" | "degraded" | "unhealthy"
  timestamp: string
  components: {
    vectorStore: "ready" | "missing"
    searchIndex: "ready" | "missing"
    metadata: "ready" | "missing"
  }
  data: {
    vectorsLoaded: number
    indices: number
  }
}

export async function GET(): Promise<Response> {
  const dataDir = path.join(process.cwd(), "public/data")

  const components = {
    vectorStore: fs.existsSync(path.join(dataDir, "aria_vectors.json")) ? "ready" : ("missing" as const),
    searchIndex: fs.existsSync(path.join(dataDir, "aria_search_index.json")) ? "ready" : ("missing" as const),
    metadata: fs.existsSync(path.join(dataDir, "aria_metadata.json")) ? "ready" : ("missing" as const),
  }

  const allReady = Object.values(components).every((c) => c === "ready")

  let vectorsLoaded = 0
  try {
    if (components.vectorStore === "ready") {
      const vectorPath = path.join(dataDir, "aria_vectors.json")
      const data = fs.readFileSync(vectorPath, "utf-8")
      const vectors = JSON.parse(data)
      vectorsLoaded = vectors.length
    }
  } catch (error) {
    console.error("[v0] Error reading vectors:", error)
  }

  const status: HealthStatus = {
    status: allReady ? "healthy" : "degraded",
    timestamp: new Date().toISOString(),
    components,
    data: {
      vectorsLoaded,
      indices: components.searchIndex === "ready" ? 1 : 0,
    },
  }

  return Response.json(status, {
    status: allReady ? 200 : 503,
  })
}
