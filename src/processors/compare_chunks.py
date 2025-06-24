import json
from pathlib import Path
from datetime import datetime
from tabulate import tabulate

def load_latest_chunks(directory, prefix):
    """Charge le fichier de chunks le plus récent pour un préfixe donné."""
    # Chercher les fichiers avec le préfixe spécifique
    chunk_files = list(directory.glob(f"{prefix}_chunks_*.json"))
    
    # Si aucun fichier trouvé avec le préfixe spécifique, chercher les fichiers "chunks_*.json"
    if not chunk_files and prefix == "generali":
        chunk_files = list(directory.glob("chunks_*.json"))
    
    if not chunk_files:
        print(f"Aucun fichier de chunks trouvé pour {prefix}")
        return None
    
    # Trier par date de modification (le plus récent en premier)
    latest_file = max(chunk_files, key=lambda x: x.stat().st_mtime)
    print(f"Fichier chargé pour {prefix}: {latest_file.name}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def prepare_table_data(chunks, document_type):
    """Prépare les données pour le tableau selon le type de document."""
    table_data = []
    headers = []
    
    if document_type == "generali":
        headers = ["Section", "Sous-section ID", "Sous-section Titre", "Page"]
        for chunk in chunks:
            table_data.append([
                chunk['general_section'],
                chunk['subsection_id'],
                chunk['subsection_title'],
                chunk['page_number']
            ])
    else:  # AXA
        headers = ["Section ID", "Titre", "Page"]
        for chunk in chunks:
            table_data.append([
                chunk['section_id'],
                chunk['section_title'],
                chunk['page_number']
            ])
    
    return headers, table_data

def display_metadata(chunks, document_name):
    """Affiche les métadonnées sous forme de tableau."""
    print(f"\nMétadonnées pour {document_name}:")
    print("=" * 80)
    
    headers, table_data = prepare_table_data(chunks, "generali" if document_name == "Generali" else "axa")
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def main():
    # Configuration des chemins
    current_dir = Path(__file__).parent
    chunks_dir = current_dir / "extracted_chunks"
    
    # Vérification que le dossier existe
    if not chunks_dir.exists():
        print(f"Erreur: Le dossier {chunks_dir} n'existe pas.")
        return
    
    # Chargement des chunks
    generali_chunks = load_latest_chunks(chunks_dir, "generali")
    axa_chunks = load_latest_chunks(chunks_dir, "axa")
    
    if not generali_chunks or not axa_chunks:
        print("Erreur: Impossible de trouver les fichiers de chunks.")
        return
    
    # Affichage des métadonnées pour chaque document
    display_metadata(generali_chunks, "Generali")
    display_metadata(axa_chunks, "AXA")
    
    # Affichage des statistiques
    print("\nStatistiques:")
    print(f"Nombre de chunks Generali: {len(generali_chunks)}")
    print(f"Nombre de chunks AXA: {len(axa_chunks)}")

if __name__ == "__main__":
    main() 