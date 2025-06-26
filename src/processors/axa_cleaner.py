# -*- coding: utf-8 -*-
import re
from pathlib import Path
from datetime import datetime


def clean_axa_text(text: str) -> str:
    """
    Nettoie le texte extrait des documents AXA en supprimant les pieds de page
    et autres éléments non pertinents.
    """
    lines = text.split('\n')
    cleaned_lines = []

    # Pattern du pied de page à supprimer
    footer_pattern_text = "Motor Vehicle Insurance. GIC Version 10.2023"

    # Pattern Regex pour les numéros de page seuls (ex: "2", "3", etc.)
    page_number_pattern = re.compile(r'^\s*\d+\s*$')

    for line in lines:
        line_stripped = line.strip()

        # Vérifier si la ligne contient le texte du pied de page
        is_footer = footer_pattern_text.lower() in line_stripped.lower()
        
        # Vérifier si la ligne est uniquement un numéro de page
        is_page_number = page_number_pattern.match(line_stripped)

        if not is_footer and not is_page_number:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def main():
    """
    Fonction principale pour nettoyer le texte.
    Lit le dernier fichier texte d'AXA, le nettoie et le sauvegarde.
    """
    # Configuration des chemins
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    # Dossiers d'entrée et de sortie
    input_dir = project_root / "data" / "processed" / "axa" / "text"
    output_dir = project_root / "data" / "processed" / "axa" / "cleaned_text"
    
    # Créer le dossier de sortie s'il n'existe pas
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Trouver le fichier le plus récent dans le dossier d'entrée
    input_files = list(input_dir.glob("axa_text_*.txt"))
    if not input_files:
        print("Aucun fichier d'entrée à nettoyer trouvé pour AXA.")
        return
    
    latest_file = max(input_files, key=lambda x: x.stat().st_mtime)
    
    try:
        print(f"Nettoyage du fichier AXA : {latest_file}")
        
        # Lire le contenu du fichier
        with open(latest_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Nettoyer le texte
        cleaned_text = clean_axa_text(text_content)
        
        # Sauvegarder le texte nettoyé
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_stem = latest_file.stem
        output_file_name = f"cleaned_{original_stem}_{timestamp}.txt"
        output_file_path = output_dir / output_file_name
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        print(f"\nTexte AXA nettoyé sauvegardé dans : {output_file_path}")
        
    except Exception as e:
        print(f"Erreur lors du nettoyage du fichier AXA : {str(e)}")


if __name__ == "__main__":
    main() 