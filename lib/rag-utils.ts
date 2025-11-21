export function buildSystemPrompt(): string {
  return `You are an industrial safety expert analyzing the ARIA incident database. 
  Provide detailed, evidence-based analysis of industrial accidents and safety incidents.

  Key requirements:
  - Base your analysis ONLY on the provided incident documents
  - Identify patterns, root causes, and prevention strategies
  - Provide specific recommendations based on the evidence
  - Cite specific incidents when making claims
  - Focus on practical, actionable insights for safety professionals

  Format your response with clear sections and bullet points for readability.`
}

export function buildUserPrompt(query: string, context: { documents: any[], query: string }): string {
  const { documents } = context
  
  let contextText = ""
  documents.forEach((doc, index) => {
    contextText += `\n--- Incident ${index + 1} ---
Source: ${doc.metadata.source}
Date: ${doc.metadata.date}
Title: ${doc.metadata.title}
Relevance: ${(doc.similarity * 100).toFixed(1)}%
Content: ${doc.content}\n`
  })

  return `Query: ${query}

Relevant Industrial Incidents:
${contextText}

Please analyze these incidents and provide:
1. Key patterns and common factors
2. Root cause analysis
3. Prevention recommendations
4. Safety improvement suggestions
5. Any regulatory or procedural insights`
}

export function formatContextSize(documents: any[]): string {
  const totalChars = documents.reduce((sum, doc) => sum + doc.content.length, 0)
  return `${documents.length} documents (${Math.round(totalChars / 1000)}KB)`
}