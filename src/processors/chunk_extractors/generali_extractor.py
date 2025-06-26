# -*- coding: utf-8 -*-
import fitz  # PyMuPDF
from pathlib import Path
from datetime import datetime


def extract_text_generali(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = []

    for page_num in range(3, len(doc)):  # Commencer à la page 4
        page = doc[page_num]
        blocks = page.get_text("blocks")

        if not blocks:
            continue

        page_width = page.rect.width
        mid_x = page_width / 2

        # Séparer blocs gauche et droite
        left_blocks = [b for b in blocks if b[0] < mid_x]
        right_blocks = [b for b in blocks if b[0] >= mid_x]

        left_sorted = sorted(left_blocks, key=lambda b: b[1])
        right_sorted = sorted(right_blocks, key=lambda b: b[1])

        blocks_sorted = left_sorted + right_sorted
        page_text = "\n".join(b[4].strip() for b in blocks_sorted)
        full_text.append(page_text)

    return "\n\n".join(full_text)


def main():
    # Configuration des chemins
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent.parent
    documents_dir = project_root / "data" / "documents"
    output_dir = project_root / "data" / "processed" / "generali" / "text"
    
    # Chemin vers le document AVB de Generali
    document_path = documents_dir / "generali" / "car" / "avb-vehicle-insurance-en (1).pdf"
    
    # Vérification que le document existe
    if not document_path.exists():
        print(f"Erreur: Le document {document_path} n'existe pas.")
        return
    
    try:
        print("Début du traitement du document AVB de Generali...")
        print(f"Document source : {document_path}")
        
        # Extraction du texte
        text = extract_text_generali(str(document_path))
        
        # Création du dossier de sortie s'il n'existe pas
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Sauvegarde du texte
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_dir / f"generali_text_{timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)
        
        print(f"\nTexte sauvegardé dans : {output_file}")
        print("\nContenu du texte :")
        print("=" * 80)
        print(text[:2000])  # Afficher les 2000 premiers caractères
        print("..." if len(text) > 2000 else "")
        print("=" * 80)
        
    except Exception as e:
        print(f"Erreur lors du traitement du document : {str(e)}")


if __name__ == "__main__":
    main() 