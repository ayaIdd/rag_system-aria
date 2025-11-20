export interface RAGContext {
  documents: Array<{
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
  }>
  query: string
}

export interface RAGResponse {
  answer: string
  sources: Array<{
    id: string
    type: string
    location: string
    date: string
    similarity: string
  }>
  metadata: {
    resultCount: number
    queryTime: number
    method: string
    documentsRetrieved: number
  }
}

export function buildSystemPrompt(): string {
  return `You are an expert safety analyst specializing in industrial accidents and incident prevention, with deep knowledge of the French ARIA database.

Your responsibilities:
1. Analyze queries about industrial incidents, safety practices, and risk prevention
2. Provide evidence-based responses grounded in real incident data
3. Identify patterns and common causes of accidents
4. Recommend preventive measures based on historical incidents
5. Always cite specific incident sources with dates and locations

Response Guidelines:
- Be precise and factual, avoiding speculation
- Structure responses clearly with numbered points or sections
- Include practical recommendations where applicable
- Highlight severity levels and risk factors
- Connect similar incidents to show patterns
- Suggest preventive measures based on learned lessons`
}

export function buildUserPrompt(query: string, context: RAGContext): string {
  const documentContent = context.documents
    .map((doc, idx) => {
      return `[Reference ${idx + 1}] Source: ${doc.metadata.source}
Date: ${doc.metadata.date} | Location: ${doc.metadata.location}
Industry: ${doc.metadata.industry} | Type: ${doc.metadata.incident_type}
Severity: ${doc.metadata.severity} | Similarity: ${(doc.similarity * 100).toFixed(1)}%

Content:
${doc.content}
---`
    })
    .join("\n\n")

  return `User Query: "${query}"

${
  context.documents.length > 0
    ? `Available Incident References:
${documentContent}

Based on the references above, please:`
    : `No specific incident references found in the database. Please provide a response based on general industrial safety knowledge:`
}

1. Answer the query directly and comprehensively
2. Reference specific incidents by their source ID when relevant
3. Identify patterns across multiple incidents if applicable
4. Provide concrete preventive recommendations
5. Assess risk levels if the question relates to safety hazards
6. Suggest best practices based on the incident data

Maintain a professional, analytical tone throughout your response.`
}

export function formatContextSize(documents: any[]): string {
  const contentSize = documents.reduce((sum, doc) => sum + doc.content.length, 0)
  return `${contentSize} characters of incident data`
}

// Additional utility functions can be added here
