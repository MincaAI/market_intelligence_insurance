import re
from pathlib import Path
from datetime import datetime


def clean_generali_text(text: str) -> str:
    """
    Nettoie le texte extrait des documents Generali en supprimant les pieds de page
    et autres éléments non pertinents.
    """
    lines = text.split('\n')
    cleaned_lines = []

    # Textes récurrents à supprimer (pieds de page) - recherche partielle
    footer_patterns = [
        "Generali Assurances Générales SA",
        "Gruppo Assicurativo Generali",
        "registre italien des groupes d'assurance",
        "generali.ch/protectiondesdonnees",
        "service clientèle"
    ]

    # Pattern Regex pour les numéros de page (ex: "8 / 29")
    page_number_pattern = re.compile(r'^\s*\d+\s*[/| ]\s*\d+\s*$')

    for line in lines:
        line_stripped = line.strip()

        # Vérifier si la ligne contient un des patterns du pied de page
        is_footer = any(pattern.lower() in line_stripped.lower() for pattern in footer_patterns)
        
        # Vérifier si la ligne correspond au pattern du numéro de page
        is_page_number = page_number_pattern.match(line_stripped)

        if not is_footer and not is_page_number:
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def main():
    """
    Fonction principale pour nettoyer le texte.
    Lit le dernier fichier texte de Generali, le nettoie et le sauvegarde.
    """
    # Configuration des chemins
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    # Dossiers d'entrée et de sortie
    input_dir = project_root / "data" / "processed" / "generali" / "text"
    output_dir = project_root / "data" / "processed" / "generali" / "cleaned_text"
    
    # Créer le dossier de sortie s'il n'existe pas
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Trouver le fichier le plus récent dans le dossier d'entrée
    input_files = list(input_dir.glob("generali_text_*.txt"))
    if not input_files:
        print("Aucun fichier d'entrée à nettoyer trouvé.")
        return
    
    latest_file = max(input_files, key=lambda x: x.stat().st_mtime)
    
    try:
        print(f"Nettoyage du fichier : {latest_file}")
        
        # Lire le contenu du fichier
        with open(latest_file, 'r', encoding='utf-8') as f:
            text_content = f.read()
        
        # Nettoyer le texte
        cleaned_text = clean_generali_text(text_content)
        
        # Sauvegarder le texte nettoyé
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        original_stem = latest_file.stem
        output_file_name = f"cleaned_{original_stem}_{timestamp}.txt"
        output_file_path = output_dir / output_file_name
        
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        print(f"\nTexte nettoyé sauvegardé dans : {output_file_path}")
        
    except Exception as e:
        print(f"Erreur lors du nettoyage : {str(e)}")


if __name__ == "__main__":
    main() 