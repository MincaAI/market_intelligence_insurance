# -*- coding: utf-8 -*-
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Ce mapping reste utile
PART_TITLES = {
    "A": "Part A - Underlying Provisions of the Insurance Contract",
    "B": "Part B - Liability insurance: Damage caused by your vehicle",
    "C": "Part C - Accidental damage insurance: Damage to your vehicle",
    "D": "Part D - Services and add-ons",
    "E": "Part E - Definitions"
}

SECTIONS_MAP_TRAVEL_EN = {
    "A": "Underlying Provisions of the Insurance Contract",
    "B": "Cancellation Costs",
    "C": "Personal Assistance",
    "D": "Roadside Assistance",
    "E": "Medical Treatment Costs Abroad",
    "F": "Rental Car Deductible",
    "G": "Luggage",
    "H": "Travel Legal Protection",
    "I": "Claims",
    "J": "Compensation",
    "K": "Definitions"
}

# Add a regex to match 'Part X' where X is A-K
PART_SECTION_PATTERN = re.compile(r'^Part ([A-K])\b', re.IGNORECASE)

def extract_chunks_from_text(text: str, pdf_name: str) -> List[Dict[str, Any]]:
    """
    Extrait les chunks du texte AXA en identifiant d'abord un marqueur "Partie X",
    puis son titre sur la ligne suivante, et enfin les sous-sections associées.
    """
    chunks = []
    lines = text.split('\n')
    
    current_part_letter = ''
    current_part_title = "FRAMEWORK CONDITIONS OF THE INSURANCE CONTRACT"
    current_chunk = None
    buffer = []
    
    # Regex pour marquer le début d'une nouvelle partie (ex: "Partie B")
    part_marker_pattern = re.compile(r'^\s*(Partie|Part)\s*([A-K])\s*$', re.IGNORECASE)
    # Regex pour un ID de sous-section (ex: "B1")
    subsection_id_pattern = re.compile(r'^([A-K])(\d{1,2})$')

    last_section_number = 0

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # 1. On cherche d'abord un marqueur de partie ("Partie B")
        part_match = part_marker_pattern.match(line)
        if part_match and (i + 1 < len(lines)):
            # Sauvegarder le chunk courant avant de passer à la nouvelle partie
            if current_chunk and buffer:
                current_chunk['content'] = '\n'.join(buffer).strip()
                chunks.append(current_chunk)
                current_chunk = None
                buffer = []
            # C'est une nouvelle partie. On lit le titre sur la ligne suivante.
            current_part_letter = part_match.group(2)
            current_part_title = lines[i+1].strip()
            # On réinitialise la numérotation pour la nouvelle partie
            last_section_number = 0
            i += 2  # On a consommé "Partie B" et son titre
            continue

        # 2. On cherche une sous-section (B1, B2...)
        subsection_match = subsection_id_pattern.match(line)
        if subsection_match:
            part_letter = subsection_match.group(1)
            section_number = int(subsection_match.group(2))

            # Continuité : la lettre de section doit être celle en cours et le numéro doit être supérieur
            is_continuing_part = (part_letter == current_part_letter and section_number > last_section_number)
            
            # Cas spécial pour la partie A qui n'est pas précédée par "Partie A"
            is_first_part = (current_part_letter == '' and part_letter == 'A')
            if is_first_part:
                current_part_letter = 'A'
                # Le titre de la partie A est manquant dans le texte, nous le définissons manuellement.
                current_part_title = "Underlying Provisions of the Insurance Contract"


            if (is_continuing_part or is_first_part) and (i + 1 < len(lines)):
                subsection_title = lines[i+1].strip()
                
                # Sauvegarder le chunk précédent
                if current_chunk and buffer:
                    current_chunk['content'] = '\n'.join(buffer).strip()
                    chunks.append(current_chunk)
                
                # Commencer le nouveau chunk
                buffer = []
                current_chunk = {
                    "pdf_name": pdf_name,
                    "section": f"Partie {current_part_letter} - {current_part_title}",
                    "subsection": f"{part_letter}{section_number} - {subsection_title}"
                }

                last_section_number = section_number
                
                i += 2 # On a consommé l'ID (B1) et le titre de la sous-section
                continue

        # Detect 'Part X' section headers
        part_match = PART_SECTION_PATTERN.match(line)
        if part_match:
            # Save previous chunk
            if buffer and current_part_letter:
                chunks.append({
                    "pdf_name": pdf_name,
                    "section": f"Part {current_part_letter} - {current_part_title}",
                    "content": "\n".join(buffer).strip()
                })
                buffer = []
            section_letter = part_match.group(1).upper()
            section_title = SECTIONS_MAP_TRAVEL_EN.get(section_letter, f"Part {section_letter}")
            current_part_letter = section_letter
            current_part_title = section_title
            continue

        if current_chunk:
            buffer.append(line)
        
        i += 1
    
    if current_chunk and buffer:
        current_chunk['content'] = '\n'.join(buffer).strip()
        chunks.append(current_chunk)
    # Cas où la dernière section (ex: Part E) n'a pas de sous-section
    elif current_part_letter and buffer:
        chunk = {
            "pdf_name": pdf_name,
            "section": f"Part {current_part_letter} - {current_part_title}",
            "subsection": "Definitions",
            "content": "\n".join(buffer).strip()
        }
        chunks.append(chunk)
        
    return chunks


def save_chunks_to_json(chunks: List[Dict[str, Any]], output_path: Path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

def display_chunk_summary(chunks: List[Dict[str, Any]]):
    print("\n" + "="*80)
    print("           RÉSUMÉ DES CHUNKS AXA GÉNÉRÉS")
    print("="*80)
    if not chunks:
        print("Aucun chunk n'a été généré.")
        return
    last_section = None
    for chunk in chunks:
        section = chunk.get('section', 'Section non définie')
        subsection = chunk.get('subsection', 'Sous-section non définie')
        if section != last_section:
            print(f"\n{section}")
            last_section = section
        print(f"  - {subsection}")
    print("\n" + "="*80)

def main():
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    input_dir = project_root / "data" / "processed" / "axa" / "cleaned_text"
    output_dir = project_root / "data" / "processed" / "axa" / "chunks"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    input_files = list(input_dir.glob("cleaned_axa_text_*.txt"))
    if not input_files:
        print("Aucun fichier texte nettoyé pour AXA trouvé.")
        return
    
    latest_file = max(input_files, key=lambda x: x.stat().st_mtime)
    
    try:
        print(f"Génération des chunks pour AXA : {latest_file}")
        with open(latest_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        pdf_name = "17601EN-AXA-Motor_vehicle_insurance-GIP-2023-10D (2).pdf"
        chunks = extract_chunks_from_text(text_content, pdf_name)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"axa_chunks_{timestamp}.json"
        save_chunks_to_json(chunks, output_file)
        
        print(f"\nChunks AXA générés et sauvegardés dans : {output_file}")
        print(f"Nombre de chunks générés : {len(chunks)}")
        
        display_chunk_summary(chunks)
        
    except Exception as e:
        print(f"Erreur lors de la génération des chunks AXA : {str(e)}")

if __name__ == "__main__":
    main() 