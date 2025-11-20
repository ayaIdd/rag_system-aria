# Deployment Guide

## Prerequisites

- GitHub account
- Vercel account
- OpenAI API key (optional - uses Vercel AI Gateway by default)

## Step 1: Prepare Data

Run the data pipeline locally before deployment:

\`\`\`bash
chmod +x scripts/setup.sh
./scripts/setup.sh
\`\`\`

This generates:
- `public/data/aria_vectors.json` - Vector embeddings
- `public/data/aria_search_index.json` - Search index
- `public/data/aria_metadata.json` - Metadata

## Step 2: Commit to GitHub

\`\`\`bash
git add public/data/
git commit -m "Add pre-computed embeddings"
git push origin main
\`\`\`

## Step 3: Deploy to Vercel

### Option A: Using Vercel CLI

\`\`\`bash
vercel --prod
\`\`\`

### Option B: Using Vercel Dashboard

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Select your GitHub repository
4. Configure environment variables:
   - `OPENAI_API_KEY` (optional)
5. Click "Deploy"

## Step 4: Verify Deployment

Check health endpoint:

\`\`\`bash
curl https://your-app.vercel.app/api/health
\`\`\`

Expected response:
\`\`\`json
{
  "status": "healthy",
  "components": {
    "vectorStore": "ready",
    "searchIndex": "ready",
    "metadata": "ready"
  }
}
\`\`\`

## Step 5: Test RAG System

Visit your deployment URL and try a query:
- "What causes chemical accidents?"
- "Prevention measures for warehouse fires"

## Production Checklist

- [ ] Data files committed to repository
- [ ] Environment variables configured
- [ ] Health endpoint returns "healthy"
- [ ] Sample queries tested
- [ ] Performance monitored
- [ ] Error logs checked
- [ ] SSL certificate configured
- [ ] Custom domain (optional)

## Monitoring

### View Logs

\`\`\`bash
vercel logs --prod
\`\`\`

### Monitor Performance

- Check Vercel Analytics dashboard
- Monitor query response times
- Track error rates

## Scaling

For larger datasets (>100k incidents):

1. Split vector store into shards
2. Implement pagination in search results
3. Add caching layer (Redis)
4. Use CDN for static data files

## Troubleshooting

### 503 Service Unavailable

Check health endpoint:
\`\`\`bash
curl https://your-app.vercel.app/api/health
\`\`\`

Likely cause: Missing data files. Re-run setup and redeploy.

### Slow Queries

- Check vector store size
- Verify search threshold
- Monitor API response times
- Consider pagination

### Memory Issues

- Split vector store
- Implement lazy loading
- Use compression for embeddings

## Support

For deployment issues:
1. Check Vercel logs
2. Verify environment variables
3. Test health endpoint
4. Review error messages
