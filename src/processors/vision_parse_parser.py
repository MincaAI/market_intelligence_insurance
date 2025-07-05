from vision_parse import VisionParser
from langchain_text_splitters import MarkdownHeaderTextSplitter
# Initialize parser
parser = VisionParser(
    model_name="gpt-4o",  # For local models, you don't need to provide the api key
    # api_key="",
    temperature=0.4,
    top_p=0.5,
    image_mode="url",  # Image mode can be "url", "base64" or None
    detailed_extraction=False,  # Set to True for more detailed extraction
    enable_concurrency=True,  # Set to True for parallel processing
)

# Convert PDF to markdown
pdf_path = "/Users/vo.anh.huy/Personal/market_intelligence_insurance/data/documents/axa/car/17601EN-AXA-Motor_vehicle_insurance-GIP-2023-10D (2).pdf"  # local path to your pdf file
markdown_pages = parser.convert_pdf(pdf_path)

raw_text = "\n".join(markdown_pages)

# Process results
# for i, page_content in enumerate(markdown_pages):
#     print(f"\n--- Page {i+1} ---\n{page_content}")


text_chunks = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Section"),
    ],
)

chunked_text = text_chunks.split_text(raw_text)

# Write all chunked_text results to a .txt file
output_path = "chunked_text_output.txt"
with open(output_path, "w", encoding="utf-8") as f:
    for i, chunk in enumerate(chunked_text):
        f.write(f"--- Chunk {i+1} ---\n")
        f.write(chunk.page_content)
        f.write("\n\n")

print(f"All chunks written to {output_path}")
