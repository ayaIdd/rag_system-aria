import json
from pathlib import Path

def setup_aria_data():
    """Setup ARIA dataset and generate embeddings"""
    print("[v0] Setting up ARIA dataset...")
    
    # Create dataset
    incidents = [
        {
            'id': '2023001',
            'date': '2023-01-15',
            'location': 'Lyon, Rhône-Alpes',
            'industry': 'Chemical Manufacturing',
            'incident_type': 'Chemical Exposure',
            'description': 'Accidental release of toxic chlorine gas during transfer operations from storage tank to processing unit. 3 workers exposed to fumes, 1 hospitalized with respiratory issues.',
            'severity': 'High',
            'causes': 'Equipment failure in pressure relief valve, inadequate monitoring',
            'preventive_measures': 'Regular equipment inspection, improved ventilation systems, personal protective equipment'
        },
        {
            'id': '2023002',
            'date': '2023-02-22',
            'location': 'Marseille, Provence-Alpes-Côte d\'Azur',
            'industry': 'Warehouse Storage',
            'incident_type': 'Fire',
            'description': 'Fire in storage facility containing flammable materials. Spread to adjacent area. No injuries but significant property damage estimated at 500,000 euros.',
            'severity': 'High',
            'causes': 'Electrical fault in storage area wiring, improper material storage',
            'preventive_measures': 'Enhanced fire detection systems, improved electrical safety protocols, fire suppression equipment'
        },
        {
            'id': '2023003',
            'date': '2023-03-10',
            'location': 'Paris, Île-de-France',
            'industry': 'Metal Fabrication',
            'incident_type': 'Equipment Accident',
            'description': 'Worker caught in machinery during maintenance operations. Serious arm injury requiring emergency surgery and 3 months recovery.',
            'severity': 'Critical',
            'causes': 'Machine not properly locked out during maintenance, inadequate communication',
            'preventive_measures': 'Stricter lockout/tagout procedures, worker training programs, safety interlocks'
        },
        {
            'id': '2023004',
            'date': '2023-04-05',
            'location': 'Toulouse, Occitanie',
            'industry': 'Pharmaceutical',
            'incident_type': 'Contamination',
            'description': 'Batch contamination in sterile manufacturing area detected during quality control. Entire batch destroyed. No contaminated products released to market.',
            'severity': 'Medium',
            'causes': 'Procedure deviation in clean room protocols, inadequate documentation review',
            'preventive_measures': 'Improved staff training, enhanced quality control checks, better documentation systems'
        },
        {
            'id': '2023005',
            'date': '2023-05-18',
            'location': 'Bordeaux, Nouvelle-Aquitaine',
            'industry': 'Oil Refinery',
            'incident_type': 'Spill',
            'description': 'Small oil spill in loading area during transfer operations. Approximately 200 liters released. Contained quickly using secondary containment barriers.',
            'severity': 'Medium',
            'causes': 'Human error during transfer, loose connection on transfer hose',
            'preventive_measures': 'Better secondary containment design, improved operator training, regular equipment maintenance'
        },
        {
            'id': '2023006',
            'date': '2023-06-12',
            'location': 'Nantes, Pays de la Loire',
            'industry': 'Food Processing',
            'incident_type': 'Burn Injury',
            'description': 'Worker sustained second-degree burns on arm from contact with steam pipe in production area. Treated at occupational health facility.',
            'severity': 'Medium',
            'causes': 'Inadequate insulation on steam pipes, lack of warning labels',
            'preventive_measures': 'Proper pipe insulation, warning labels and signage, employee training'
        },
        {
            'id': '2023007',
            'date': '2023-07-20',
            'location': 'Strasbourg, Grand Est',
            'industry': 'Electronics Manufacturing',
            'incident_type': 'Solvent Exposure',
            'description': 'Several workers exposed to volatile organic compound vapors in assembly area due to inadequate ventilation. No serious injuries but minor respiratory irritation reported.',
            'severity': 'Low',
            'causes': 'Ventilation system malfunction, delayed maintenance',
            'preventive_measures': 'Enhanced ventilation system maintenance, air quality monitoring, respiratory protection'
        },
        {
            'id': '2023008',
            'date': '2023-08-05',
            'location': 'Grenoble, Auvergne-Rhône-Alpes',
            'industry': 'Construction',
            'incident_type': 'Fall from Height',
            'description': 'Worker fell from scaffolding during roofing work. Fracture to left leg. Rescued by emergency services, hospitalized for 5 days.',
            'severity': 'High',
            'causes': 'Inadequate fall protection, improper scaffolding setup',
            'preventive_measures': 'Mandatory harness and safety equipment, better scaffolding inspection, training programs'
        },
        {
            'id': '2023009',
            'date': '2023-09-14',
            'location': 'Lille, Hauts-de-France',
            'industry': 'Textile Manufacturing',
            'incident_type': 'Machine Entanglement',
            'description': 'Worker\'s hair caught in textile machinery during operation. Scalp laceration requiring stitches. Machine emergency stop activated quickly.',
            'severity': 'Medium',
            'causes': 'Inadequate safety guards on machinery, lack of protective headwear',
            'preventive_measures': 'Enhanced machine guards, mandatory safety headwear, regular safety audits'
        },
        {
            'id': '2023010',
            'date': '2023-10-22',
            'location': 'Marseille, Provence-Alpes-Côte d\'Azur',
            'industry': 'Chemical Manufacturing',
            'incident_type': 'Acid Burn',
            'description': 'Worker suffered chemical burn to hand from splashing sulfuric acid during container transfer. Treated with cool water and medical attention immediately.',
            'severity': 'Medium',
            'causes': 'Improper handling technique, inadequate protective equipment',
            'preventive_measures': 'Proper handling procedures, better protective gloves, safety training'
        },
        {
            'id': '2023011',
            'date': '2023-11-08',
            'location': 'Lyon, Rhône-Alpes',
            'industry': 'Metal Fabrication',
            'incident_type': 'Welding Accident',
            'description': 'Welding arc flash caused eye damage to worker without proper protection. Temporary vision impairment. Treated by occupational health.',
            'severity': 'Medium',
            'causes': 'Missing or damaged welding helmet, inadequate personal protective equipment',
            'preventive_measures': 'Mandatory welding helmets, equipment inspection, worker education'
        },
        {
            'id': '2023012',
            'date': '2023-12-03',
            'location': 'Toulouse, Occitanie',
            'industry': 'Pharmaceutical',
            'incident_type': 'Allergic Reaction',
            'description': 'Worker experienced allergic reaction to pharmaceutical ingredient. Symptoms included respiratory distress. Treated with epinephrine and antihistamines.',
            'severity': 'High',
            'causes': 'Unknown ingredient sensitivity, inadequate health screening',
            'preventive_measures': 'Better health screening, respiratory protection, incident response procedures'
        },
        {
            'id': '2024001',
            'date': '2024-01-10',
            'location': 'Paris, Île-de-France',
            'industry': 'Oil Refinery',
            'incident_type': 'Vapor Release',
            'description': 'Unplanned vapor release from distillation unit. Vicinity evacuated. No injuries. Release contained within 2 hours.',
            'severity': 'High',
            'causes': 'Pressure relief valve malfunction, inadequate monitoring system',
            'preventive_measures': 'Preventive maintenance program, upgraded pressure relief systems, monitoring enhancements'
        },
        {
            'id': '2024002',
            'date': '2024-02-15',
            'location': 'Bordeaux, Nouvelle-Aquitaine',
            'industry': 'Food Processing',
            'incident_type': 'Contamination',
            'description': 'Foreign object (metal fragment) found in product batch. Batch recalled immediately before distribution.',
            'severity': 'Medium',
            'causes': 'Equipment deterioration, inadequate inspection procedures',
            'preventive_measures': 'Metal detection installation, preventive maintenance, inspection protocols'
        },
        {
            'id': '2024003',
            'date': '2024-03-20',
            'location': 'Nantes, Pays de la Loire',
            'industry': 'Electronics Manufacturing',
            'incident_type': 'Electrical Shock',
            'description': 'Worker received electrical shock from faulty equipment. Minor burns on hand. Equipment immediately removed from service.',
            'severity': 'Medium',
            'causes': 'Damaged insulation, inadequate equipment maintenance',
            'preventive_measures': 'Regular equipment testing, proper grounding, maintenance procedures'
        },
        {
            'id': '2024004',
            'date': '2024-04-12',
            'location': 'Grenoble, Auvergne-Rhône-Alpes',
            'industry': 'Construction',
            'incident_type': 'Crush Injury',
            'description': 'Worker crushed between material pile and equipment. Serious leg injury. Surgery required for fracture repair.',
            'severity': 'Critical',
            'causes': 'Improper material stacking, lack of warning systems',
            'preventive_measures': 'Proper stacking procedures, spotters for equipment operation, safety barriers'
        },
        {
            'id': '2024005',
            'date': '2024-05-08',
            'location': 'Strasbourg, Grand Est',
            'industry': 'Chemical Manufacturing',
            'incident_type': 'Caustic Splash',
            'description': 'Sodium hydroxide solution splashed on worker during container handling. Treated with water rinse and medical evaluation.',
            'severity': 'Medium',
            'causes': 'Improper container handling, inadequate labeling',
            'preventive_measures': 'Better handling procedures, clear labeling, splash protection equipment'
        },
        {
            'id': '2024006',
            'date': '2024-06-25',
            'location': 'Lille, Hauts-de-France',
            'industry': 'Textile Manufacturing',
            'incident_type': 'Chemical Allergy',
            'description': 'Worker developed severe allergic reaction to textile dye compounds. Respiratory issues. Referred to occupational medicine.',
            'severity': 'High',
            'causes': 'Chemical sensitivity, inadequate respiratory protection',
            'preventive_measures': 'Enhanced ventilation, respiratory protection, health monitoring'
        },
        {
            'id': '2024007',
            'date': '2024-07-30',
            'location': 'Marseille, Provence-Alpes-Côte d\'Azur',
            'industry': 'Oil Refinery',
            'incident_type': 'Fire',
            'description': 'Small fire in maintenance area during welding operation. Quickly extinguished. Minor equipment damage.',
            'severity': 'Low',
            'causes': 'Inadequate work permit system, insufficient fire watch',
            'preventive_measures': 'Hot work permits, fire watch procedures, better fire extinguisher placement'
        },
        {
            'id': '2024008',
            'date': '2024-08-18',
            'location': 'Lyon, Rhône-Alpes',
            'industry': 'Pharmaceutical',
            'incident_type': 'Needle Stick Injury',
            'description': 'Healthcare worker sustained needle stick injury during product testing. Immediately received post-exposure prophylaxis.',
            'severity': 'Medium',
            'causes': 'Improper needle handling, inadequate needle disposal containers',
            'preventive_measures': 'Safety needle devices, proper training, adequate disposal systems'
        },
    ]
    
    output_path = Path('public/data/aria_dataset.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(incidents, f, ensure_ascii=False, indent=2)
    
    print(f"[v0] Dataset created with {len(incidents)} incidents")
    print(f"[v0] Saved to {output_path}")

if __name__ == '__main__':
    setup_aria_data()
    print("[v0] Setup complete!")
