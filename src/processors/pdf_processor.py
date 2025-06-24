import fitz  # PyMuPDF
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DocumentChunk:
    """Classe pour représenter un chunk de document avec sa structure."""
    general_section: str
    subsection_id: str
    subsection_title: str
    content: str
    page_number: int
    document_name: str
    insurer: str
    extraction_date: str

class PDFDocumentProcessor:
    """Classe pour traiter les documents PDF et extraire leur contenu structuré."""
    
    def __init__(self, pdf_path: str, insurer: str):
        self.pdf_path = pdf_path
        self.document_name = Path(pdf_path).stem
        self.insurer = insurer
        self.doc = fitz.open(pdf_path)
        
    def extract_text(self) -> List[Dict[str, Any]]:
        """Extrait le texte du document PDF avec les numéros de page."""
        pages_content = []
        for page_num, page in enumerate(self.doc, start=1):
            text = page.get_text()
            pages_content.append({
                "page_number": page_num,
                "text": text
            })
        return pages_content

    def extract_chunks(self) -> List[DocumentChunk]:
        """Extrait les chunks structurés du document."""
        pages_content = self.extract_text()
        chunks = []
        
        general_section = None
        buffer = ""
        current_sub_id = None
        current_sub_title = None
        current_page = 1

        for page_data in pages_content:
            current_page = page_data["page_number"]
            lines = page_data["text"].split("\n")
            
            for line in lines:
                line = line.strip()

                # Titre principal (ex: "A. Généralités")
                match_section = re.match(r"^([A-Z]\.?)\s+(.+)", line)
                if match_section:
                    general_section = line
                    continue

                # Sous-paragraphe (ex: "24. Couverture d'assurance")
                match_sub = re.match(r"^(\d{1,3}\.)\s+(.+)", line)
                if match_sub:
                    # Sauvegarde du chunk précédent si existant
                    if current_sub_id and buffer.strip():
                        chunks.append(DocumentChunk(
                            general_section=general_section,
                            subsection_id=current_sub_id,
                            subsection_title=current_sub_title,
                            content=buffer.strip(),
                            page_number=current_page,
                            document_name=self.document_name,
                            insurer=self.insurer,
                            extraction_date=datetime.now().isoformat()
                        ))
                        buffer = ""

                    current_sub_id = match_sub.group(1)
                    current_sub_title = match_sub.group(2)
                    continue

                # Sinon, on accumule le texte
                if current_sub_id:
                    buffer += line + " "

        # Dernier chunk
        if current_sub_id and buffer.strip():
            chunks.append(DocumentChunk(
                general_section=general_section,
                subsection_id=current_sub_id,
                subsection_title=current_sub_title,
                content=buffer.strip(),
                page_number=current_page,
                document_name=self.document_name,
                insurer=self.insurer,
                extraction_date=datetime.now().isoformat()
            ))

        return chunks

    def process_document(self) -> List[Dict[str, Any]]:
        """Traite le document et retourne les chunks sous forme de dictionnaires."""
        chunks = self.extract_chunks()
        return [
            {
                "general_section": chunk.general_section,
                "subsection_id": chunk.subsection_id,
                "subsection_title": chunk.subsection_title,
                "content": chunk.content,
                "page_number": chunk.page_number,
                "document_name": chunk.document_name,
                "insurer": chunk.insurer,
                "extraction_date": chunk.extraction_date
            }
            for chunk in chunks
        ]

    def display_chunks(self, chunks: List[Dict[str, Any]] = None) -> None:
        """Affiche les chunks de manière lisible."""
        if chunks is None:
            chunks = self.process_document()
            
        for i, chunk in enumerate(chunks, 1):
            print(f"\n{'='*80}")
            print(f"CHUNK {i}")
            print(f"{'='*80}")
            print(f"Document: {chunk['document_name']}")
            print(f"Assureur: {chunk['insurer']}")
            print(f"Page: {chunk['page_number']}")
            print(f"Date d'extraction: {chunk['extraction_date']}")
            print(f"\nSection: {chunk['general_section']}")
            print(f"Sous-section: {chunk['subsection_id']} {chunk['subsection_title']}")
            print(f"\nContenu:")
            print(f"{'-'*40}")
            print(chunk['content'])
            print(f"{'-'*40}\n")

    def __del__(self):
        """Ferme le document PDF proprement."""
        if hasattr(self, 'doc'):
            self.doc.close() 