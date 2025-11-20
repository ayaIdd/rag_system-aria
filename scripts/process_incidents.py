import json
import csv
from pathlib import Path
from typing import List, Dict
import hashlib

def load_incidents(filepath: str = 'public/data/aria_dataset.csv') -> List[Dict]:
    """Load incident data from CSV"""
    print(f"[v0] Loading incidents from {filepath}")
    
    incidents = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Add a content hash for similarity checking
                content = f"{row.get('description', '')} {row.get('causes', '')}"
                row['content_hash'] = hashlib.md5(content.encode()).hexdigest()[:8]
                incidents.append(row)
    except FileNotFoundError:
        print(f"[v0] File not found: {filepath}")
        return []
    
    print(f"[v0] Loaded {len(incidents)} incidents")
    return incidents

def extract_metadata(incidents: List[Dict]) -> Dict:
    """Extract metadata from incidents for quick lookups"""
    print("[v0] Extracting metadata...")
    
    metadata = {
        'total_incidents': len(incidents),
        'industries': set(),
        'incident_types': set(),
        'severity_levels': set(),
        'date_range': {'earliest': None, 'latest': None},
        'locations': set(),
    }
    
    for incident in incidents:
        if 'industry' in incident:
            metadata['industries'].add(incident['industry'])
        if 'incident_type' in incident:
            metadata['incident_types'].add(incident['incident_type'])
        if 'severity' in incident:
            metadata['severity_levels'].add(incident['severity'])
        if 'location' in incident:
            metadata['locations'].add(incident['location'])
        if 'date' in incident:
            date = incident['date']
            if not metadata['date_range']['earliest'] or date < metadata['date_range']['earliest']:
                metadata['date_range']['earliest'] = date
            if not metadata['date_range']['latest'] or date > metadata['date_range']['latest']:
                metadata['date_range']['latest'] = date
    
    # Convert sets to lists for JSON serialization
    metadata['industries'] = sorted(list(metadata['industries']))
    metadata['incident_types'] = sorted(list(metadata['incident_types']))
    metadata['severity_levels'] = sorted(list(metadata['severity_levels']))
    metadata['locations'] = sorted(list(metadata['locations']))
    
    print(f"[v0] Metadata extracted:")
    print(f"[v0]   - Industries: {len(metadata['industries'])}")
    print(f"[v0]   - Incident Types: {len(metadata['incident_types'])}")
    print(f"[v0]   - Severity Levels: {len(metadata['severity_levels'])}")
    print(f"[v0]   - Locations: {len(metadata['locations'])}")
    
    return metadata

def create_embeddings_index(incidents: List[Dict]) -> List[Dict]:
    """Create index entries for embedding generation"""
    print("[v0] Creating embeddings index...")
    
    index_entries = []
    for incident in incidents:
        # Combine all text fields for embedding
        text_content = []
        
        if 'description' in incident:
            text_content.append(f"Description: {incident['description']}")
        if 'causes' in incident:
            text_content.append(f"Causes: {incident['causes']}")
        if 'preventive_measures' in incident:
            text_content.append(f"Prevention: {incident['preventive_measures']}")
        if 'incident_type' in incident:
            text_content.append(f"Type: {incident['incident_type']}")
        if 'industry' in incident:
            text_content.append(f"Industry: {incident['industry']}")
        
        full_text = " ".join(text_content)
        
        index_entries.append({
            'id': incident.get('id', ''),
            'content': full_text,
            'metadata': {
                'date': incident.get('date', ''),
                'location': incident.get('location', ''),
                'industry': incident.get('industry', ''),
                'incident_type': incident.get('incident_type', ''),
                'severity': incident.get('severity', ''),
                'source': f"ARIA-{incident.get('id', 'Unknown')}"
            }
        })
    
    print(f"[v0] Created {len(index_entries)} index entries")
    return index_entries

def save_processed_data(index_entries: List[Dict], metadata: Dict):
    """Save processed data for RAG system"""
    print("[v0] Saving processed data...")
    
    output_dir = Path('public/data')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save index
    index_path = output_dir / 'aria_index.json'
    with open(index_path, 'w', encoding='utf-8') as f:
        json.dump(index_entries, f, ensure_ascii=False, indent=2)
    print(f"[v0] Index saved to {index_path}")
    
    # Save metadata
    metadata_path = output_dir / 'aria_metadata.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"[v0] Metadata saved to {metadata_path}")

if __name__ == '__main__':
    # Load incidents
    incidents = load_incidents()
    
    if incidents:
        # Extract metadata
        metadata = extract_metadata(incidents)
        
        # Create embeddings index
        index_entries = create_embeddings_index(incidents)
        
        # Save processed data
        save_processed_data(index_entries, metadata)
        
        print("[v0] Data processing complete!")
    else:
        print("[v0] No incidents loaded. Please run fetch_aria_data.py first.")
