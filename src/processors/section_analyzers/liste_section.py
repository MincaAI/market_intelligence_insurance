import os
import json

EXTRACTED_CHUNKS_DIR = os.path.join(os.path.dirname(__file__), 'extracted_chunks')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'sections_list')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def extract_sections_from_file(filepath, is_axa):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    sections = set()
    for chunk in data:
        part = chunk.get('part') or ''
        if is_axa:
            section_id = chunk.get('section_id')
            section_title = chunk.get('section_title')
        else:
            section_id = chunk.get('section_id')
            section_title = chunk.get('section_title')
        page_number = chunk.get('page_number')
        if (section_id or section_title) and page_number is not None:
            sections.add((page_number, part, section_id, section_title))
    # Sort by page number, then section id
    return sorted(sections)


def main():
    for filename in os.listdir(EXTRACTED_CHUNKS_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(EXTRACTED_CHUNKS_DIR, filename)
            is_axa = filename.lower().startswith('axa')
            sections = extract_sections_from_file(filepath, is_axa)
            # Write to TXT file
            output_txt = os.path.join(OUTPUT_DIR, f'sections_{filename[:-5]}.txt')
            with open(output_txt, 'w', encoding='utf-8') as f:
                for page_number, part, section_id, section_title in sections:
                    id_str = section_id or ''
                    title_str = section_title or ''
                    part_str = part or ''
                    if is_axa:
                        f.write(f'- {part_str} - {id_str} - {title_str} - p{page_number}\n')
                    else:
                        f.write(f'- {part_str} - {id_str} - {title_str} - p{page_number}\n')
            print(f"Sections texte enregistrées dans {output_txt} ({len(sections)} sections)")

if __name__ == '__main__':
    main() 