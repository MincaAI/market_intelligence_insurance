import unittest
from pathlib import Path
import json
import os
from openai import OpenAI
import re
from dotenv import load_dotenv

class TestGeneraliParser(unittest.TestCase):
    
    def setUp(self):
        # Charger les variables d'environnement
        load_dotenv()
        
        # Définir la clé API OpenAI
        api_key = "sk-Ue2Hs0Hs0Hs0Hs0Hs0Hs0Hs0Hs0Hs0Hs0Hs0H"  # Remplacez par votre clé API
        self.client = OpenAI(api_key=api_key)
        
        self.project_root = Path(__file__).parent.parent
        self.input_dir = self.project_root / "data" / "processed" / "generali" / "text"
        self.output_dir = self.project_root / "data" / "processed" / "generali" / "chunks"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def get_latest_text_file(self):
        """Récupère le fichier texte le plus récent du dossier input."""
        input_files = list(self.input_dir.glob("generali_text_*.txt"))
        if not input_files:
            raise FileNotFoundError("Aucun fichier texte trouvé dans le dossier input")
        return max(input_files, key=lambda x: x.stat().st_mtime)

    def extract_page_number(self, text_block):
        """Extrait le numéro de page d'un bloc de texte."""
        match = re.search(r"PAGE (\d+)", text_block)
        return int(match.group(1)) if match else None

    def parse_text_with_llm(self, text_content):
        """Parse le texte avec le LLM pour extraire les chunks structurés."""
        
        system_prompt = """Tu es un expert en analyse de documents d'assurance en français.
        Analyse ce texte d'assurance et structure-le en sections logiques.

        Pour chaque section, tu dois :
        1. Identifier la section principale et la sous-section
        2. Extraire le contenu complet
        3. Détecter et reconstruire les tableaux si présents
        4. Noter le numéro de page

        Format de sortie JSON attendu :
        {
            "chunks": [
                {
                    "main_section": "Titre de la section principale",
                    "sub_section": "Titre de la sous-section",
                    "page_number": X,
                    "content": "Contenu complet incluant les tableaux reconstruits"
                }
            ]
        }

        Instructions spéciales :
        - Si tu détectes un tableau, reconstruis-le proprement dans le content
        - Garde la hiérarchie des sections (principale/sous-sections)
        - Assure-toi d'inclure tous les numéros de page
        - Conserve le texte exact, sans reformulation
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Correction du modèle
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_content}
                ],
                temperature=0.0
            )
            
            # Extraire et parser la réponse JSON
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"Erreur lors du parsing avec le LLM : {str(e)}")
            return None

    def test_parse_generali_text(self):
        """Test principal pour parser le texte Generali."""
        try:
            # Récupérer le dernier fichier texte
            latest_file = self.get_latest_text_file()
            print(f"Traitement du fichier : {latest_file}")

            # Lire le contenu
            with open(latest_file, 'r', encoding='utf-8') as f:
                text_content = f.read()

            # Diviser le texte en blocs par page
            page_blocks = re.split(r'={80}\nPAGE \d+\n={80}', text_content)
            
            all_chunks = []
            
            # Traiter chaque bloc de page
            for block in page_blocks:
                if not block.strip():
                    continue
                    
                page_num = self.extract_page_number(block)
                if page_num is None:
                    continue

                # Parser le bloc avec le LLM
                result = self.parse_text_with_llm(block)
                if result and 'chunks' in result:
                    # Ajouter le numéro de page à chaque chunk
                    for chunk in result['chunks']:
                        chunk['page_number'] = page_num
                    all_chunks.extend(result['chunks'])

            # Sauvegarder les résultats
            output_file = self.output_dir / f"generali_parsed_chunks_{latest_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump({"chunks": all_chunks}, f, ensure_ascii=False, indent=2)

            print(f"\nChunks sauvegardés dans : {output_file}")
            print("\nAperçu des chunks :")
            print("=" * 80)
            print(json.dumps(all_chunks[:2], ensure_ascii=False, indent=2))
            
            # Vérifications
            self.assertTrue(len(all_chunks) > 0, "Aucun chunk n'a été extrait")
            for chunk in all_chunks:
                self.assertIn('main_section', chunk, "main_section manquante")
                self.assertIn('page_number', chunk, "page_number manquant")
                self.assertIn('content', chunk, "content manquant")

        except Exception as e:
            self.fail(f"Test échoué avec l'erreur : {str(e)}")

if __name__ == '__main__':
    unittest.main() 