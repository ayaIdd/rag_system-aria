# ARIA RAG System Setup Script
# This script sets up the RAG system with sample data

set -e

echo "[v0] Starting ARIA RAG System setup..."

# Create necessary directories
echo "[v0] Creating data directories..."
mkdir -p public/data

# Install Python dependencies if needed
if ! command -v python3 &> /dev/null; then
    echo "[v0] Warning: Python3 not found. Some data processing features will be unavailable."
else
    echo "[v0] Python3 found at $(which python3)"
    echo "[v0] Installing Python dependencies..."
    pip install requests --quiet || echo "[v0] Warning: Could not install requests"
fi

# Run data pipeline
echo "[v0] Running data pipeline..."
if command -v python3 &> /dev/null; then
    python3 scripts/fetch_aria_data.py || echo "[v0] Warning: Data fetch failed, using sample data"
    python3 scripts/process_incidents.py || echo "[v0] Warning: Data processing failed"
    python3 scripts/generate_embeddings.py || echo "[v0] Warning: Embedding generation failed"
else
    echo "[v0] Warning: Skipping Python scripts (Python3 not available)"
    echo "[v0] Creating sample data directory..."
    mkdir -p public/data
fi

# Check if data files exist
if [ -f "public/data/aria_dataset.csv" ]; then
    echo "[v0] Dataset found: $(wc -l < public/data/aria_dataset.csv) records"
fi

if [ -f "public/data/aria_index.json" ]; then
    echo "[v0] Index file created successfully"
fi

if [ -f "public/data/aria_vectors.json" ]; then
    echo "[v0] Vector store created successfully"
fi

echo "[v0] Setup complete! You can now run: npm run dev"
