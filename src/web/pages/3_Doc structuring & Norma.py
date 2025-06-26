import streamlit as st

st.set_page_config(page_title="Doc Structuring & Normalisation", page_icon="🗂️", initial_sidebar_state="expanded")

st.title("🗂️ Document Structuring & Normalisation")

st.markdown('''
## Guidelines: Document Structuring & Vectorization

**1. Document Structuring (Chunking):**
- Each insurance document (PDF) is automatically divided into smaller, meaningful sections called "chunks."
- These chunks are typically based on logical document structure, such as sections, articles, or paragraphs.
- The goal is to ensure each chunk contains a coherent piece of information, making it easier to search and compare specific topics across different insurers.

**2. Metadata Enrichment:**
- For every chunk, we extract and attach key metadata, such as:
  - Insurer name (e.g., AXA, Generali)
  - Product type (car, travel, etc.)
  - Section and subsection titles
  - Language and version information
- This metadata allows for precise filtering and comparison during search and analysis.

**3. Vectorization:**
- Each chunk of text is transformed into a numerical "vector" using advanced AI language models.
- These vectors capture the semantic meaning of the text, enabling highly relevant and context-aware search.
- All vectors, along with their metadata, are stored in a specialized vector database.

**4. Search & Retrieval:**
- When a user asks a question, their query is also converted into a vector.
- The system finds and ranks the most relevant chunks from all documents, regardless of insurer or product, based on semantic similarity.
- This approach ensures that users receive the most precise and contextually appropriate answers, even for complex or nuanced queries.

---

**Summary:**  
This process enables robust, multilingual, and fine-grained search and comparison across all insurance documents, supporting both regulatory compliance and business intelligence.
''')

# ... existing code ... 