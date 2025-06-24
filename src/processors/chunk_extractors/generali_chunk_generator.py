# -*- coding: utf-8 -*-
import re
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


SECTIONS_MAP_FR = {
    "A.": "DISPOSITIONS COMMUNES",
    "B.": "RESPONSABILITÉ CIVILE",
    "C.": "ASSURANCE CASCO",
    "D.": "ASSURANCE-ACCIDENTS",
    "E.": "SERVICE D'ASSISTANCE ET DE DÉPANNAGE 24H/24"
}

SECTIONS_MAP_EN = {
    "A.": "Benefits overview",
    "B.": "Common provisions",
    "C.": "General exclusions",
    "D.": "Services",
    "E.": "Cancellation costs"
}

SECTION_TITLES_PATTERN = re.compile(r"^([A-E])\.\s*$")


def extract_chunks_from_text(text: str, pdf_name: str, lang: str = "fr") -> List[Dict[str, Any]]:
    """
    Extrait les chunks du texte en utilisant des expressions régulières.
    Utilise le mapping de section en français ou anglais selon la langue détectée.
    
    Args:
        text (str): Le texte nettoyé à découper en chunks
        pdf_name (str): Nom du fichier PDF source
        lang (str): Langue du texte (par défaut 'fr')
        
    Returns:
        List[Dict[str, Any]]: Liste des chunks avec leurs métadonnées
    """
    SECTIONS_MAP = SECTIONS_MAP_EN if lang == "en" else SECTIONS_MAP_FR
    chunks = []
    current_section = None
    current_chunk = None
    current_page = 1
    expected_subsection_number = 1

    lines = text.split("\n")
    page_pattern = re.compile(r"(\d+)\s*/\s*\d+")
    section_code_pattern = re.compile(r"^([A-E])\.$")
    subsection_number_pattern = re.compile(r"^(\d{1,3})\.\s*(.*)")

    buffer = []
    waiting_section_code = None
    last_subsection_number = 0  # Garder une trace du dernier numéro de sous-section valide

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        page_match = page_pattern.search(line)
        if page_match:
            current_page = int(page_match.group(1))
            continue

        # Section avec code + titre direct (ex: B. RESPONSABILITÉ CIVILE)
        direct_section_match = re.match(r"^([A-E])\.\s+(.*)$", line)
        if direct_section_match:
            title_candidate = direct_section_match.group(2).strip()
            # Un vrai titre de section est en majuscules
            if title_candidate == title_candidate.upper() and len(title_candidate) > 5:
                if current_chunk:
                    current_chunk["content"] = "\n".join(buffer).strip()
                    chunks.append(current_chunk)
                    current_chunk = None
                    buffer = []

                section_code = f"{direct_section_match.group(1)}."
                section_title = title_candidate
                current_section = f"{section_code} {section_title}"
                continue
        
        section_code_match = section_code_pattern.match(line)
        if section_code_match:
            if current_chunk:
                current_chunk["content"] = "\n".join(buffer).strip()
                chunks.append(current_chunk)
                current_chunk = None
                buffer = []

            waiting_section_code = f"{section_code_match.group(1)}."
            continue

        if waiting_section_code:
            title_candidate = line.strip()
            # Un vrai titre de section est en majuscules
            if title_candidate == title_candidate.upper() and len(title_candidate) > 5:
                section_title = SECTIONS_MAP.get(waiting_section_code, title_candidate)
                current_section = f"{waiting_section_code} {section_title}"
                waiting_section_code = None
                continue
            # Si ce n'est pas un titre, c'est du contenu
            else:
                if buffer:
                    buffer.append(line)
                waiting_section_code = None # Annuler l'attente
                continue

        subsection_match = subsection_number_pattern.match(line)

        if subsection_match:
            subsection_number = int(subsection_match.group(1))
            
            # Règle de continuité : le numéro doit être supérieur au précédent.
            if subsection_number <= last_subsection_number:
                if buffer is not None:
                    buffer.append(line) # C'est du contenu, pas une nouvelle sous-section
                continue

            subsection_title = subsection_match.group(2).strip()

            # Récupérer la ligne suivante comme titre si vide
            if not subsection_title and i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line and not subsection_number_pattern.match(next_line):
                    subsection_title = next_line

            # Vérifie qu'il n'y a pas d'autres points (exclut les 1.1. ou 2.3.4)
            if not re.match(rf"^{subsection_number}\\.\\s*$", line) and "." in subsection_title:
                if buffer is not None:
                    buffer.append(line)
                continue

            if current_chunk:
                current_chunk["content"] = "\n".join(buffer).strip()
                chunks.append(current_chunk)

            full_subsection = f"{subsection_number}. {subsection_title}"
            buffer = [full_subsection]

            current_chunk = {
                "pdf": pdf_name,
                "section": current_section,
                "subsection": full_subsection,
                "page": current_page,
                "content": ""
            }

            last_subsection_number = subsection_number # Mettre à jour le dernier numéro valide
            continue

        if buffer is not None:
            buffer.append(line)

    if current_chunk:
        current_chunk["content"] = "\n".join(buffer).strip()
        chunks.append(current_chunk)

    return chunks


def save_chunks_to_json(chunks: List[Dict[str, Any]], output_path: Path):
    """
    Sauvegarde les chunks dans un fichier JSON.
    
    Args:
        chunks (List[Dict[str, Any]]): Liste des chunks à sauvegarder
        output_path (Path): Chemin du fichier de sortie
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


def display_chunk_summary(chunks: List[Dict[str, Any]]):
    """
    Affiche un résumé lisible des sections et sous-sections des chunks générés.
    """
    print("\n" + "="*80)
    print("           RÉSUMÉ DES CHUNKS GÉNÉRÉS")
    print("="*80)
    
    if not chunks:
        print("Aucun chunk n'a été généré.")
        return

    # Utiliser un set pour éviter les doublons de sections/sous-sections si nécessaire,
    # mais ici on parcourt simplement pour l'affichage.
    
    last_section = None
    for chunk in chunks:
        section = chunk.get('section', 'Section non définie')
        subsection = chunk.get('subsection', 'Sous-section non définie')
        page = chunk.get('page', 'N/A')
        
        if section != last_section:
            print(f"\n{section}")
            last_section = section
            
        print(f"  - {subsection} (Page: {page})")
        
    print("\n" + "="*80)


def main():
    """
    Fonction principale pour générer les chunks.
    Lit le dernier fichier texte nettoyé, génère les chunks et les sauvegarde.
    """
    # Configuration des chemins
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    
    # Dossiers d'entrée et de sortie
    input_dir = project_root / "data" / "processed" / "generali" / "cleaned_text"
    output_dir = project_root / "data" / "processed" / "generali" / "chunks"
    
    # Créer le dossier de sortie s'il n'existe pas
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Trouver le fichier le plus récent dans le dossier d'entrée
    input_files = list(input_dir.glob("cleaned_generali_text_*.txt"))
    if not input_files:
        print("Aucun fichier texte nettoyé trouvé.")
        return
    
    latest_file = max(input_files, key=lambda x: x.stat().st_mtime)
    
    try:
        print(f"Génération des chunks pour : {latest_file}")
        
        # Lire le contenu du fichier nettoyé
        with open(latest_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Générer les chunks avec regex
        pdf_name = "avb-assurance-vehicules-fr.pdf"  # Nom du fichier PDF source
        chunks = extract_chunks_from_text(text_content, pdf_name)
        
        # Sauvegarder les chunks
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"generali_chunks_{timestamp}.json"
        save_chunks_to_json(chunks, output_file)
        
        print(f"\nChunks générés et sauvegardés dans : {output_file}")
        print(f"Nombre de chunks générés : {len(chunks)}")
        
        # Afficher un résumé des chunks
        display_chunk_summary(chunks)
        
    except Exception as e:
        print(f"Erreur lors de la génération des chunks : {str(e)}")


if __name__ == "__main__":
    main() 