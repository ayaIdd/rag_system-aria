# ARIA RAG System - Industrial Incident Intelligence

A production-ready RAG (Retrieval Augmented Generation) system for querying and analyzing 53,000+ industrial accidents from the ARIA database. Provides AI-powered semantic search and evidence-based safety recommendations.


## 🚀 Features

- **Semantic Search**: FAISS-powered vector similarity search across incident reports
- **AI Analysis**: Groq LLM integration for intelligent incident analysis
- **Real-time Querying**: Fast, responsive search interface
- **Evidence-based Insights**: Source citations with similarity scores
- **Modern UI**: Built with Next.js 14, Tailwind CSS, and shadcn/ui
- **Production Ready**: FastAPI backend with health monitoring


## 🛠️ Quick Start

### Prerequisites

- Node.js 18+ 
- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com))

### Installation

1. **Clone and install dependencies:**
   \`\`\`bash
   npm install
   pip install -r requirements.txt
   \`\`\`

2. **Set up environment variables:**
   \`\`\`bash
   cp .env.local.example .env.local
   \`\`\`
   Add your Groq API key:
   \`\`\`env
   GROQ_API_KEY=gsk_your_key_here
   \`\`\`

3. **Generate embeddings (first time only):**
   \`\`\`bash
   python scripts/generate_embeddings.py
   \`\`\`

## 🚀 Running the System

**Start the Python search API:**
\`\`\`bash
python scripts/search_api.py
\`\`\`
API will be available at: http://localhost:8000

**Start the Next.js frontend:**
\`\`\`bash
npm run dev
\`\`\`
App will be available at: http://localhost:3000

Open your browser and start querying!

## 💡 Usage Examples

Try these sample queries:

- "What causes fires in warehouses?"
- "Chemical exposure prevention measures"
- "Common manufacturing incident patterns"
- "Equipment failure risk factors"

The system will:

1. Perform semantic search across 53,000+ incidents
2. Retrieve the most relevant documents
3. Generate AI-powered analysis with Groq LLM
4. Provide evidence-based recommendations with sources

## 🔧 Technical Architecture

### Frontend (Next.js 14)
- Framework: Next.js 14 with App Router
- Styling: Tailwind CSS + shadcn/ui
- State Management: React hooks
- Type Safety: TypeScript

### Backend (Python)
- Search API: FastAPI with FAISS vector database
- Embeddings: sentence-transformers/all-MiniLM-L6-v2
- Vector Store: FAISS for similarity search
- Performance: ~22 documents/second processing

### AI Integration
- LLM Provider: Groq (llama3-8b-8192)
- RAG Pipeline: Semantic search + contextual generation
- Response Time: Sub-100ms search + ~2s AI analysis

## 📊 Performance

- Embedding Generation: 1,500 documents in 1.2 minutes
- Search Speed: ~22 documents/second processing
- Query Response: < 3 seconds end-to-end
- Accuracy: Semantic similarity with configurable thresholds

## 🚀 Deployment

### Vercel (Frontend)
\`\`\`bash
npm run build
vercel deploy
\`\`\`

## 📡 API Endpoints

### Search API (Python - Port 8000)
- `GET /health` - Health check
- `POST /search` - Semantic search
- `GET /stats` - System statistics

### RAG API (Next.js - Port 3000)
- `POST /api/query` - Main RAG query endpoint
- `GET /api/health` - Application health
