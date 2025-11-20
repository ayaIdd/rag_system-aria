interface TestCase {
  name: string
  query: string
  expectedMinResults: number
  expectedMaxTime: number
}

const testCases: TestCase[] = [
  {
    name: "Chemical incident search",
    query: "What causes chemical exposure incidents?",
    expectedMinResults: 1,
    expectedMaxTime: 5000,
  },
  {
    name: "Fire prevention query",
    query: "How can warehouse fires be prevented?",
    expectedMinResults: 1,
    expectedMaxTime: 5000,
  },
  {
    name: "Equipment safety analysis",
    query: "What are common equipment failure causes?",
    expectedMinResults: 1,
    expectedMaxTime: 5000,
  },
  {
    name: "Industry-specific incidents",
    query: "Manufacturing safety incidents and prevention",
    expectedMinResults: 0,
    expectedMaxTime: 5000,
  },
  {
    name: "General safety query",
    query: "workplace safety best practices",
    expectedMinResults: 0,
    expectedMaxTime: 5000,
  },
]

async function testQuery(query: string): Promise<any> {
  const baseUrl = process.env.TEST_URL || "http://localhost:3000"

  try {
    const response = await fetch(`${baseUrl}/api/query`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`[v0] Test query failed: ${error}`)
    throw error
  }
}

async function testHealth(): Promise<any> {
  const baseUrl = process.env.TEST_URL || "http://localhost:3000"

  try {
    const response = await fetch(`${baseUrl}/api/health`)
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.status}`)
    }
    return await response.json()
  } catch (error) {
    console.error(`[v0] Health check failed: ${error}`)
    throw error
  }
}

async function runTests() {
  console.log("[v0] Starting RAG System Tests\n")

  // Health check
  console.log("[v0] Checking system health...")
  try {
    const health = await testHealth()
    console.log(`[v0] Health: ${health.status}`)
    console.log(
      `[v0] Components: Vector Store=${health.components.vectorStore}, Search Index=${health.components.searchIndex}`,
    )
    console.log(`[v0] Data: ${health.data.vectorsLoaded} vectors loaded\n`)

    if (health.status !== "healthy") {
      console.warn("[v0] Warning: System not fully healthy")
    }
  } catch (error) {
    console.error(`[v0] Health check failed: ${error}`)
    console.log("[v0] Continuing with tests anyway...\n")
  }

  let passed = 0
  let failed = 0

  for (const testCase of testCases) {
    console.log(`[v0] Running test: ${testCase.name}`)
    console.log(`     Query: "${testCase.query}"`)

    try {
      const startTime = Date.now()
      const result = await testQuery(testCase.query)
      const elapsed = Date.now() - startTime

      const errors: string[] = []

      if (!result.answer) {
        errors.push("Missing answer field")
      }

      if (!Array.isArray(result.sources)) {
        errors.push("Sources is not an array")
      } else if (result.sources.length < testCase.expectedMinResults) {
        errors.push(`Expected at least ${testCase.expectedMinResults} sources, got ${result.sources.length}`)
      }

      if (elapsed > testCase.expectedMaxTime) {
        errors.push(`Query took ${elapsed}ms, expected max ${testCase.expectedMaxTime}ms`)
      }

      if (!result.metadata) {
        errors.push("Missing metadata")
      }

      if (errors.length === 0) {
        console.log(`     ✓ PASSED (${elapsed}ms, ${result.sources?.length || 0} sources)\n`)
        passed++
      } else {
        console.log(`     ✗ FAILED`)
        errors.forEach((error) => console.log(`       - ${error}`))
        console.log()
        failed++
      }
    } catch (error) {
      console.log(`     ✗ ERROR: ${error}\n`)
      failed++
    }
  }

  console.log(`[v0] Test Results: ${passed} passed, ${failed} failed`)

  if (failed === 0) {
    console.log("[v0] All tests passed!")
  }

  process.exit(failed > 0 ? 1 : 0)
}

runTests().catch((error) => {
  console.error("[v0] Test runner error:", error)
  process.exit(1)
})
