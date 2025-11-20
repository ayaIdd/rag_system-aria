import os
import json
import csv
import time
from groq import Groq
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

def generate_embeddings():
    # Initialize Groq client
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("❌ GROQ_API_KEY not found in environment variables")
        print("Make sure .env.local exists with your API key")
        return
    
    print(f"🔑 Using API key: {api_key[:20]}...")
    
    client = Groq(api_key=api_key)
    
    # Read CSV file - UPDATED to aria_df.csv
    csv_path = Path("public/data/aria_df.csv")
    
    if not csv_path.exists():
        print(f"❌ CSV file not found at: {csv_path}")
        print("Please place your aria_df.csv file in public/data/")
        return
    
    print(f"📊 Reading CSV from: {csv_path}")
    
    incidents = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            incidents.append(row)
    
    print(f"Found {len(incidents)} incidents in aria_df.csv")
    
    results = []
    processed = 0
    skipped = 0
    
    for i, row in enumerate(incidents):
        # Get columns (adjust if your CSV has different column names)
        titre = row.get('Titre', '').strip()
        contenu = row.get('Contenu', '').strip()
        date = row.get('Date', '').strip()
        
        if not titre or not contenu:
            print(f"⚠️  Skipping row {i}: Missing title or content")
            skipped += 1
            continue
        
        try:
            # Combine title and content
            text_to_embed = f"{titre}\n\n{contenu}"
            
            print(f"Processing {i+1}/{len(incidents)}: {titre[:60]}...")
            
            # Generate embedding with Groq
            response = client.embeddings.create(
                model="nomic-embed-text-v1.5",
                input=text_to_embed
            )
            
            embedding = response.data[0].embedding
            
            results.append({
                "id": f"ARIA_{str(i).zfill(4)}",
                "content": text_to_embed,
                "embedding": embedding,
                "metadata": {
                    "date": date or "Date inconnue",
                    "title": titre,
                    "source": f"ARIA_{str(i).zfill(4)}"
                },
                "embedding_dimension": len(embedding)
            })
            
            processed += 1
            
            if processed % 25 == 0:
                print(f"✅ Processed {processed}/{len(incidents)} incidents...")
            
            # Small delay to avoid rate limiting
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error on row {i}: {str(e)}")
            if "rate limit" in str(e).lower():
                print("⏳ Rate limited, waiting 5 seconds...")
                time.sleep(5)
    
    if not results:
        print("❌ No embeddings generated!")
        return
    
    # Create lib directory if it doesn't exist
    lib_dir = Path("lib")
    lib_dir.mkdir(exist_ok=True)
    
    # Generate TypeScript file
    ts_content = f"""// Auto-generated from aria_df.csv
// Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
// Total incidents: {len(results)}
// Embedding model: nomic-embed-text-v1.5
// Embedding dimension: {results[0]['embedding_dimension'] if results else 'N/A'}

export interface VectorEntry {{
  id: string
  content: string
  embedding: number[]
  metadata: {{
    date: string
    title: string
    source: string
  }}
  embedding_dimension: number
}}

export const INCIDENT_DATA: VectorEntry[] = {json.dumps(results, indent=2, ensure_ascii=False)}
"""
    
    output_path = lib_dir / "incident-data.ts"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ts_content)
    
    file_size = output_path.stat().st_size / 1024 / 1024
    
    print("\n" + "="*60)
    print(f"✅ SUCCESS! Generated embeddings for {len(results)} incidents")
    print(f"📁 Saved to: {output_path}")
    print(f"💾 File size: {file_size:.2f} MB")
    print(f"📊 Skipped: {skipped} rows")
    print(f"🎯 Embedding dimension: {results[0]['embedding_dimension'] if results else 'N/A'}")
    print("="*60 + "\n")
    print("Next steps:")
    print("1. Start your dev server: npm run dev")
    print("2. The app will now use your aria_df data!")

if __name__ == "__main__":
    generate_embeddings()