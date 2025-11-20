import json
import math
from pathlib import Path
from typing import List, Dict

def simple_embedding(text: str, dimension: int = 384) -> List[float]:
    """
    Generate a simple embedding using TF-IDF-like approach
    For production, use proper embedding models like OpenAI, Sentence Transformers, etc.
    """
    text_lower = text.lower()
    words = text_lower.split()
    
    # Initialize embedding vector
    embedding = [0.0] * dimension
    
    # Simple hash-based feature extraction
    for word in words:
        if len(word) > 2:  # Skip short words
            # Hash word to dimension index
            word_hash = sum(ord(c) for c in word)
            idx = word_hash % dimension
            
            # TF-like score
            embedding[idx] += 1.0 / (len(word) * len(words) + 1)
    
    # Normalize
    magnitude = math.sqrt(sum(x**2 for x in embedding))
    if magnitude > 0:
        embedding = [x / magnitude for x in embedding]
    
    return embedding

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if len(vec1) != len(vec2):
        return 0.0
    
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    mag1 = math.sqrt(sum(a**2 for a in vec1))
    mag2 = math.sqrt(sum(b**2 for b in vec2))
    
    if mag1 == 0 or mag2 == 0:
        return 0.0
    
    return dot_product / (mag1 * mag2)

def load_index(filepath: str = 'public/data/aria_index.json') -> List[Dict]:
    """Load the processed index"""
    print(f"[v0] Loading index from {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[v0] Index file not found: {filepath}")
        return []

def generate_vector_store(index_entries: List[Dict]) -> List[Dict]:
    """Generate embeddings for all index entries"""
    print("[v0] Generating embeddings for all documents...")
    
    vector_store = []
    total = len(index_entries)
    
    for i, entry in enumerate(index_entries):
        if (i + 1) % max(1, total // 10) == 0 or i == 0:
            print(f"[v0] Processing: {i + 1}/{total}")
        
        # Generate embedding for content
        embedding = simple_embedding(entry['content'])
        
        vector_store.append({
            'id': entry['id'],
            'content': entry['content'],
            'embedding': embedding,
            'metadata': entry['metadata'],
            'embedding_dimension': len(embedding),
        })
    
    print(f"[v0] Generated {len(vector_store)} embeddings")
    return vector_store

def save_vector_store(vector_store: List[Dict]):
    """Save vector store to disk"""
    print("[v0] Saving vector store...")
    
    output_dir = Path('public/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / 'aria_vectors.json'
    
    # Create a metadata-only version for quick access (without full embeddings)
    metadata_only = []
    for entry in vector_store:
        metadata_only.append({
            'id': entry['id'],
            'metadata': entry['metadata'],
        })
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(vector_store, f, ensure_ascii=False, indent=1)
    
    metadata_path = output_dir / 'aria_vectors_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata_only, f, ensure_ascii=False, indent=2)
    
    print(f"[v0] Vector store saved to {output_path}")
    print(f"[v0] Vector store size: {len(vector_store)} documents")

def create_search_index(vector_store: List[Dict]) -> Dict:
    """Create reverse index for fast text search"""
    print("[v0] Creating search index...")
    
    search_index = {
        'keywords': {},
        'industries': {},
        'incident_types': {},
        'severity_levels': {},
    }
    
    for doc in vector_store:
        # Index keywords from content
        words = doc['content'].lower().split()
        for word in words:
            if len(word) > 3:  # Only index meaningful words
                if word not in search_index['keywords']:
                    search_index['keywords'][word] = []
                search_index['keywords'][word].append(doc['id'])
        
        # Index by metadata
        industry = doc['metadata'].get('industry', '')
        if industry:
            if industry not in search_index['industries']:
                search_index['industries'][industry] = []
            search_index['industries'][industry].append(doc['id'])
        
        incident_type = doc['metadata'].get('incident_type', '')
        if incident_type:
            if incident_type not in search_index['incident_types']:
                search_index['incident_types'][incident_type] = []
            search_index['incident_types'][incident_type].append(doc['id'])
        
        severity = doc['metadata'].get('severity', '')
        if severity:
            if severity not in search_index['severity_levels']:
                search_index['severity_levels'][severity] = []
            search_index['severity_levels'][severity].append(doc['id'])
    
    print(f"[v0] Indexed {len(search_index['keywords'])} keywords")
    print(f"[v0] Indexed {len(search_index['industries'])} industries")
    print(f"[v0] Indexed {len(search_index['incident_types'])} incident types")
    
    output_path = Path('public/data/aria_search_index.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(search_index, f, ensure_ascii=False, indent=2)
    
    print(f"[v0] Search index saved to {output_path}")

if __name__ == '__main__':
    index_entries = load_index()
    
    if index_entries:
        vector_store = generate_vector_store(index_entries)
        save_vector_store(vector_store)
        create_search_index(vector_store)
        print("[v0] Embeddings generation complete!")
    else:
        print("[v0] No index found. Please run process_incidents.py first.")
