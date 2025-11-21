import os
import json
import csv
import time
import numpy as np
import faiss
from pathlib import Path
from typing import List

# Try to load dotenv
try:
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    print("✅ Loaded .env.local")
except ImportError:
    print("⚠️  python-dotenv not installed")
    print("Run: pip install python-dotenv")
except Exception as e:
    print(f"⚠️  Error loading .env.local: {e}")

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    print("✅ sentence-transformers imported")
except ImportError:
    print("❌ sentence-transformers not installed")
    print("Run: pip install sentence-transformers")
    exit(1)

# Configuration
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("\n" + "="*70)
print("🔍 ENVIRONMENT CHECK")
print("="*70)
print(f"Model: {MODEL_NAME}")
print(f"Working directory: {os.getcwd()}")
print("="*70 + "\n")

MAX_CHUNK_LENGTH = 512
OVERLAP = 50

def chunk_text(text: str, max_length: int = MAX_CHUNK_LENGTH, overlap: int = OVERLAP) -> List[str]:
    """Split long text into overlapping chunks."""
    words = text.split()
    if len(words) <= max_length:
        return [text]
    
    chunks = []
    start = 0
    while start < len(words):
        end = start + max_length
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start = end - overlap
    
    return chunks

def average_pool_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """Average multiple chunk embeddings."""
    return np.mean(embeddings, axis=0)

def generate_embeddings():
    print("🤖 Loading Sentence Transformer Model Locally\n")
    
    # Initialize the model locally
    try:
        model = SentenceTransformer(MODEL_NAME)
        embedding_dimension = model.get_sentence_embedding_dimension()
        print(f"✅ Model loaded! Embedding dimension: {embedding_dimension}")
        print("🚀 Starting local embedding generation...\n")
        
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        return
    
    csv_path = Path("public/data/aria_df.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV file not found at: {csv_path}")
        print(f"Current directory: {os.getcwd()}")
        print(f"Looking for: {csv_path.absolute()}")
        return
    
    print(f"📊 Reading CSV from: {csv_path}")
    
    incidents = []
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                incidents.append(row)
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return
    
    total_incidents = len(incidents)
    print(f"Found {total_incidents} incidents")
    
    if total_incidents == 0:
        print("❌ No incidents found in CSV!")
        return
    
    # Show sample incident
    print(f"\nSample incident:")
    print(f"  Title: {incidents[0].get('Titre', 'N/A')[:60]}...")
    print(f"  Date: {incidents[0].get('Date', 'N/A')}")
    print()
    
    # Ask for confirmation
    response = input(f"Process {total_incidents} incidents? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    print("\n🚀 Starting embedding generation...\n")
    
    # Preallocate arrays using detected dimension
    embeddings_array = np.zeros((total_incidents, embedding_dimension), dtype='float32')
    metadata_list = []
    
    processed = 0
    skipped = 0
    total_chunks = 0
    errors = 0
    
    start_time = time.time()
    last_log_time = start_time
    
    # Process all texts first for batch encoding
    all_texts = []
    text_indices = []
    
    for i, row in enumerate(incidents):
        titre = row.get('Titre', '').strip()
        contenu = row.get('Contenu', '').strip()
        date = row.get('Date', '').strip()
        
        if not titre or not contenu:
            skipped += 1
            continue
        
        full_text = f"{titre}\n\n{contenu}"
        
        # Chunk text
        chunks = chunk_text(full_text, MAX_CHUNK_LENGTH, OVERLAP)
        total_chunks += len(chunks)
        
        # Store chunks for batch processing
        for chunk in chunks:
            all_texts.append(chunk)
            text_indices.append((i, len(chunks), titre, date, full_text))
    
    print(f"📝 Processing {len(all_texts)} chunks in batches...")
    
    # Process in batches to avoid memory issues
    batch_size = 32
    chunk_embeddings_dict = {}
    
    for batch_start in range(0, len(all_texts), batch_size):
        batch_end = min(batch_start + batch_size, len(all_texts))
        batch_texts = all_texts[batch_start:batch_end]
        
        try:
            # Get embeddings for batch
            batch_embeddings = model.encode(batch_texts, convert_to_numpy=True, show_progress_bar=False)
            
            # Store embeddings by original document index
            for idx, embedding in zip(range(batch_start, batch_end), batch_embeddings):
                doc_idx, num_chunks, titre, date, full_text = text_indices[idx]
                
                if doc_idx not in chunk_embeddings_dict:
                    chunk_embeddings_dict[doc_idx] = []
                
                chunk_embeddings_dict[doc_idx].append(embedding)
            
            processed_batch = len([k for k in chunk_embeddings_dict.keys()])
            
            # Progress logging
            current_time = time.time()
            if current_time - last_log_time >= 5:
                elapsed = current_time - start_time
                rate = processed_batch / elapsed if elapsed > 0 else 0
                eta = (total_incidents - processed_batch) / rate if rate > 0 else 0
                print(f"✅ {processed_batch}/{total_incidents} | "
                      f"{rate:.2f} docs/sec | "
                      f"ETA: {eta/60:.1f}min")
                last_log_time = current_time
                
        except Exception as e:
            print(f"❌ Batch error: {str(e)[:100]}")
            errors += 1
    
    # Average embeddings for each document
    for doc_idx, embeddings_list in chunk_embeddings_dict.items():
        if len(embeddings_list) > 1:
            doc_embedding = average_pool_embeddings(np.array(embeddings_list))
        else:
            doc_embedding = embeddings_list[0]
        
        embeddings_array[processed] = doc_embedding
        
        _, num_chunks, titre, date, full_text = text_indices[next(i for i, x in enumerate(text_indices) if x[0] == doc_idx)]
        
        metadata_list.append({
            "id": f"ARIA_{str(doc_idx).zfill(4)}",
            "content": full_text,
            "chunks": num_chunks,
            "metadata": {
                "date": date or "Date inconnue",
                "title": titre,
                "source": f"ARIA_{str(doc_idx).zfill(4)}"
            }
        })
        
        processed += 1
    
    if processed == 0:
        print("\n❌ No embeddings generated!")
        return
    
    embeddings_array = embeddings_array[:processed]
    
    lib_dir = Path("lib")
    lib_dir.mkdir(exist_ok=True)
    
    print("\n📦 Building FAISS index...")
    
    faiss.normalize_L2(embeddings_array)
    index = faiss.IndexFlatIP(embedding_dimension)
    index.add(embeddings_array)
    
    faiss_path = lib_dir / "faiss_index.bin"
    faiss.write_index(index, str(faiss_path))
    print(f"✅ FAISS index: {faiss_path}")
    
    metadata_path = lib_dir / "incident-metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump({
            "incidents": metadata_list,
            "dimension": embedding_dimension,
            "total": processed,
            "model": MODEL_NAME,
            "generated_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }, f, ensure_ascii=False, indent=2)
    print(f"✅ Metadata: {metadata_path}")
    
    total_time = time.time() - start_time
    
    print("\n" + "="*70)
    print(f"✅ SUCCESS! Generated {processed} embeddings")
    print(f"📊 Processed: {processed} | Skipped: {skipped} | Errors: {errors}")
    print(f"⏱️  Time: {total_time/60:.1f} minutes")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        generate_embeddings()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()