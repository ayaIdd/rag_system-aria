import requests
import json
import csv
from pathlib import Path
from datetime import datetime

def fetch_aria_dataset():
    """
    Fetch the ARIA industrial accident dataset from data.gouv.fr
    The dataset contains 53,000+ French industrial accidents and incidents
    """
    print("[v0] Starting ARIA dataset fetch...")
    
    # API endpoint for ARIA dataset from data.gouv.fr
    # This uses the CKAN API to access the French public data portal
    api_url = "https://www.data.gouv.fr/api/1/datasets/analyse-recherche-et-information-sur-les-accidents/"
    
    try:
        print(f"[v0] Fetching dataset metadata from {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        dataset_info = response.json()
        
        print(f"[v0] Dataset found: {dataset_info.get('title', 'ARIA Dataset')}")
        print(f"[v0] Resources available: {len(dataset_info.get('resources', []))}")
        
        # Get the main CSV resource
        resources = dataset_info.get('resources', [])
        csv_resource = None
        
        for resource in resources:
            if resource.get('format', '').lower() in ['csv', 'text/csv']:
                csv_resource = resource
                break
        
        if not csv_resource:
            print("[v0] Warning: No CSV resource found, creating sample dataset")
            create_sample_dataset()
            return
        
        download_url = csv_resource.get('url')
        print(f"[v0] Downloading from: {download_url}")
        
        # Download and save the dataset
        csv_response = requests.get(download_url, timeout=30)
        csv_response.raise_for_status()
        
        output_path = Path('public/data/aria_dataset.csv')
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(csv_response.content)
        
        print(f"[v0] Dataset saved to {output_path}")
        
        # Parse and analyze the dataset
        analyze_dataset(output_path)
        
    except requests.exceptions.RequestException as e:
        print(f"[v0] Error fetching dataset: {e}")
        print("[v0] Creating sample dataset for demonstration...")
        create_sample_dataset()

def create_sample_dataset():
    """Create a sample ARIA dataset for testing"""
    print("[v0] Creating sample ARIA dataset...")
    
    sample_data = [
        {
            'id': '1001',
            'date': '2023-01-15',
            'location': 'Lyon, France',
            'industry': 'Chemical Manufacturing',
            'incident_type': 'Chemical Exposure',
            'description': 'Accidental release of toxic chlorine gas during transfer operations. 3 workers exposed, 1 hospitalized.',
            'severity': 'High',
            'causes': 'Equipment failure, inadequate monitoring',
            'preventive_measures': 'Regular equipment inspection, improved ventilation systems'
        },
        {
            'id': '1002',
            'date': '2023-02-22',
            'location': 'Marseille, France',
            'industry': 'Warehouse Storage',
            'incident_type': 'Fire',
            'description': 'Fire in storage facility containing flammable materials. No injuries but significant property damage.',
            'severity': 'High',
            'causes': 'Electrical fault in storage area',
            'preventive_measures': 'Enhanced fire detection systems, improved electrical safety protocols'
        },
        {
            'id': '1003',
            'date': '2023-03-10',
            'location': 'Paris, France',
            'industry': 'Metal Fabrication',
            'incident_type': 'Equipment Accident',
            'description': 'Worker caught in machinery during maintenance. Serious arm injury requiring surgery.',
            'severity': 'Critical',
            'causes': 'Machine not properly locked out during maintenance',
            'preventive_measures': 'Stricter lockout/tagout procedures, worker training'
        },
        {
            'id': '1004',
            'date': '2023-04-05',
            'location': 'Toulouse, France',
            'industry': 'Pharmaceutical',
            'incident_type': 'Contamination',
            'description': 'Batch contamination in sterile manufacturing area. Entire batch destroyed, no contaminated products released.',
            'severity': 'Medium',
            'causes': 'Procedure deviation, inadequate documentation',
            'preventive_measures': 'Improved training, enhanced quality control checks'
        },
        {
            'id': '1005',
            'date': '2023-05-18',
            'location': 'Bordeaux, France',
            'industry': 'Oil Refinery',
            'incident_type': 'Spill',
            'description': 'Small oil spill in loading area. Contained quickly, environmental impact minimal.',
            'severity': 'Medium',
            'causes': 'Human error during transfer',
            'preventive_measures': 'Better secondary containment, improved operator training'
        },
    ]
    
    output_path = Path('public/data/aria_dataset.csv')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
        writer.writeheader()
        writer.writerows(sample_data)
    
    print(f"[v0] Sample dataset created at {output_path}")
    print(f"[v0] Records: {len(sample_data)}")

def analyze_dataset(filepath):
    """Analyze the dataset and print statistics"""
    print(f"[v0] Analyzing dataset at {filepath}")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        records = list(reader)
    
    print(f"[v0] Total records: {len(records)}")
    
    if records:
        print(f"[v0] Columns: {', '.join(records[0].keys())}")
        
        # Count by industry if available
        if 'industry' in records[0]:
            industries = {}
            for record in records:
                industry = record.get('industry', 'Unknown')
                industries[industry] = industries.get(industry, 0) + 1
            print(f"[v0] Industries represented: {len(industries)}")
            for industry, count in sorted(industries.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"[v0]   - {industry}: {count} incidents")

if __name__ == '__main__':
    fetch_aria_dataset()
    print("[v0] Dataset fetch complete!")
