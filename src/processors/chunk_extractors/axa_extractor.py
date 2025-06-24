# -*- coding: utf-8 -*-
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime


def extract_text_axa(pdf_path: str) -> str:
    """
    Extrait le texte brut d'un document PDF AXA, en gérant correctement l'ordre de lecture
    visuel des blocs de texte.
    """
    doc = fitz.open(pdf_path)
    full_text = []

    # Parcourir les pages à partir de la page 8 (index 7)
    for page_num in range(7, len(doc)):
        page = doc[page_num]
        
        # Obtenir les blocs de texte avec leurs coordonnées
        blocks = page.get_text("blocks")

        if not blocks:
            continue

        page_width = page.rect.width
        mid_x = page_width / 2

        # Séparer les blocs en colonnes gauche et droite
        left_blocks = [b for b in blocks if b[0] < mid_x]
        right_blocks = [b for b in blocks if b[0] >= mid_x]

        # Trier chaque colonne individuellement par position verticale
        left_sorted = sorted(left_blocks, key=lambda b: b[1])
        right_sorted = sorted(right_blocks, key=lambda b: b[1])

        # Assembler les colonnes dans l'ordre de lecture correct
        blocks_sorted = left_sorted + right_sorted
        
        # Concaténer le texte des blocs triés
        page_text = "\n".join(b[4].strip() for b in blocks_sorted if b[4].strip())
        full_text.append(page_text)

    return "\n\n".join(full_text)


def main():
    """
    Fonction principale pour extraire le texte d'un document AXA et le sauvegarder.
    """
    # Configuration des chemins
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    documents_dir = project_root / "data" / "documents"
    output_dir = project_root / "data" / "processed" / "axa" / "text"
    
    # Créer le dossier de sortie s'il n'existe pas
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Chemin vers le document AVB d'AXA
    # Note: Assurez-vous que ce nom de fichier correspond bien à votre document.
    document_path = documents_dir / "axa" / "car" / "17601FR-AXA-Assurance_vehicules_automobiles-CGA-2023-10D (1).pdf"
    
    # Vérification que le document existe
    if not document_path.exists():
        print(f"Erreur: Le document {document_path} n'existe pas.")
        return
    
    try:
        print("Début de l'extraction de texte du document AXA...")
        print(f"Document source : {document_path}")
        
        # Extraction du texte
        text = extract_text_axa(str(document_path))
        
        # Sauvegarde du texte brut
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"axa_text_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\nTexte brut sauvegardé dans : {output_file}")
        
    except Exception as e:
        print(f"Erreur lors de l'extraction : {str(e)}")


if __name__ == "__main__":
    main() 