# ARIA RAG System - Industrial Accident Database Query Engine

A production-ready Retrieval-Augmented Generation (RAG) system for querying the French ARIA database containing 53,000+ industrial accidents and incidents.

## Features

- **Semantic Search**: AI-powered vector similarity search across incident database
- **RAG Architecture**: Retrieves relevant incidents before generating responses
- **Context-Aware Analysis**: LLM generates responses based on actual incident data
- **Evidence-Based**: All answers are grounded in real incidents with citations
- **High Performance**: Optimized vector operations and caching

## Tech Stack

- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS
- **Backend**: Node.js API routes, Python data pipeline
- **AI**: Vercel AI SDK, OpenAI GPT-4o-mini
- **Data**: Vector embeddings, JSON-based vector store
- **Deployment**: Vercel

## Quick Start

### Prerequisites

- Node.js 18+
- Python 3.8+
- OpenAI API key (via Vercel AI Gateway)

### Installation

1. Clone the repository
\`\`\`bash
git clone <repository-url>
cd aria-rag-system
\`\`\`

2. Install dependencies
\`\`\`bash
npm install
\`\`\`

3. Set up environment variables
Create a `.env.local` file (see `.env.example`):
\`\`\`
# OpenAI API Key (optional - uses Vercel AI Gateway by default)
# OPENAI_API_KEY=your_key_here

# Development environment
NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL=http://localhost:3000
\`\`\`

4. Run the setup script
\`\`\`bash
chmod +x scripts/setup.sh
./scripts/setup.sh
\`\`\`

This will:
- Create necessary directories
- Fetch the ARIA dataset from data.gouv.fr
- Process and index incidents
- Generate vector embeddings

5. Start the development server
\`\`\`bash
npm run dev
\`\`\`

Visit `http://localhost:3000` to access the RAG system.

## Data Pipeline

The system processes data through several stages:

### 1. Data Fetch (`scripts/fetch_aria_data.py`)
- Downloads ARIA dataset from data.gouv.fr
- Falls back to sample data if download fails
- Stores raw CSV in `public/data/aria_dataset.csv`

### 2. Processing (`scripts/process_incidents.py`)
- Parses CSV and extracts metadata
- Creates normalized index entries
- Generates `public/data/aria_index.json`

### 3. Embeddings (`scripts/generate_embeddings.py`)
- Generates vector embeddings for each incident
- Creates vector store: `public/data/aria_vectors.json`
- Creates search index: `public/data/aria_search_index.json`

## API Endpoints

### POST `/api/query`
Main RAG endpoint for querying with LLM analysis.

**Request:**
\`\`\`json
{
  "query": "What causes chemical exposure incidents?"
}
\`\`\`

**Response:**
\`\`\`json
{
  "answer": "Based on the ARIA database...",
  "sources": [
    {
      "id": "ARIA-1001",
      "type": "Chemical Exposure",
      "location": "Lyon, France",
      "date": "2023-01-15",
      "similarity": "92.5"
    }
  ],
  "metadata": {
    "queryTime": 245,
    "documentsRetrieved": 5,
    "method": "rag-with-semantic-search"
  }
}
\`\`\`

### POST `/api/search`
Semantic search endpoint (vector similarity).

**Request:**
\`\`\`json
{
  "query": "chemical exposure",
  "limit": 5,
  "threshold": 0.1
}
\`\`\`

### POST `/api/retrieve`
Basic text-based document retrieval.

**Request:**
\`\`\`json
{
  "query": "fire prevention",
  "limit": 10
}
\`\`\`

## Development

### File Structure

\`\`\`
├── app/
│   ├── api/
│   │   ├── query/route.ts        # RAG query endpoint
│   │   ├── search/route.ts       # Semantic search endpoint
│   │   └── retrieve/route.ts     # Text retrieval endpoint
│   ├── layout.tsx
│   ├── globals.css
│   └── page.tsx
├── components/
│   ├── ui/                       # shadcn/ui components
│   ├── query-interface.tsx
│   └── results-display.tsx
├── lib/
│   └── rag-utils.ts             # RAG utility functions
├── scripts/
│   ├── fetch_aria_data.py       # Download dataset
│   ├── process_incidents.py     # Process and index
│   ├── generate_embeddings.py   # Create embeddings
│   ├── setup.sh                 # Installation script
│   └── test-rag.ts              # End-to-end tests
├── public/
│   └── data/                    # Generated data files
└── README.md
\`\`\`

### Running Tests

\`\`\`bash
# Run E2E tests
npx ts-node scripts/test-rag.ts

# With custom test URL
TEST_URL=https://your-domain.com npx ts-node scripts/test-rag.ts
\`\`\`

## Deployment

### Vercel Deployment

1. Push to GitHub
2. Import project in Vercel dashboard
3. Environment variables are configured automatically via integrations
4. Deploy!

\`\`\`bash
vercel --prod
\`\`\`

### Data Pipeline in Production

**Option 1: Pre-computed Data (Recommended)**
- Run data pipeline locally
- Commit processed files to `public/data/`
- Deploy with pre-computed vectors

**Option 2: Dynamic Pipeline**
- Use serverless functions to run pipeline on deploy
- Requires more configuration and longer build time

## Performance Considerations

- **Query Time**: Typical 200-400ms for semantic search + LLM
- **Vector Store Size**: ~10-20MB for 53,000 incidents
- **Memory**: ~500MB for loaded vector embeddings
- **Scaling**: Vector store can handle 100,000+ incidents

## Troubleshooting

### "Vector store not loaded"
- Run `./scripts/setup.sh` to generate embeddings
- Check that `public/data/aria_vectors.json` exists

### "Failed to retrieve documents"
- Verify `public/data/aria_vectors.json` is accessible
- Check API endpoint connectivity

### "Query timeout"
- Increase timeout in `/api/query`
- Reduce number of retrieved documents
- Optimize vector operations

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | No | Vercel AI Gateway | OpenAI API key |
| `NEXT_PUBLIC_DEV_SUPABASE_REDIRECT_URL` | No | http://localhost:3000 | Dev redirect URL |

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues or questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub
