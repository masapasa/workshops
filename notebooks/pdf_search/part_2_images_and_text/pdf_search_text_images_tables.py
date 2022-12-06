import os
import warnings
warnings.filterwarnings('ignore')  # ignore all those pesky warnings
from docarray import DocumentArray, Document
docs = DocumentArray.from_files("data/*.pdf")
for doc in docs:
  doc.load_uri_to_blob()
from jina import Flow, Client
flow = (
    Flow()
    .add(
        uses="jinahub://PDFTableExtractor/latest", # Extract tables
        install_requirements=True,
        name="index_table_extractor"
    )
    .add(
        uses="jinahub://PDFSegmenter", # Extract images/text
        install_requirements=True,
        name="index_segmenter"
    )
    .add(
        uses="jinahub://ElementTypeTagger", # Tag Documents based on modality (image/text/table)
        uses_with={"traversal_paths": "@c"},
        name="index_tagger",
    )
    .add(
        uses="jinahub://SpacySentencizer", # Sentencize long text into sentences
        uses_with={"traversal_paths": "@c"},
        install_requirements=True,
        name="index_sentencizer",
    )
    .add(
        uses="jinahub://TagsCopier", # Recursively copy tags
        uses_with={"traversal_paths": "@c"},
        name="index_tags_copier"
    )
    .add(
        uses="jinahub://ChunkFlattener", # Flatten all chunks to doc.chunks
        name="index_flattener"
    )
    .add(
        uses="jinahub://ImagePreprocessor-skip-non-images", # Process images in PDF chunks
        uses_with={"traversal_paths": "@c"},
        install_requirements=True,
        name="index_image_processor"
    )
    .add(
        uses="jinahub://ImagePreprocessor-skip-non-images", # Process search query image
        uses_with={"traversal_paths": "@r"},
        install_requirements=True,
        name="search_image_processor"
    )
    .add(
        uses="jinahub://CLIPEncoder/latest-gpu", # Encode using CLIP - chunk level
        uses_with={"traversal_paths": "@c"},
        install_requirements=True,
        name="index_encoder"
    )
    .add(
        uses="jinahub://CLIPEncoder/latest-gpu", # Encode using CLIP - root level
        install_requirements=True,
        name="search_encoder"
    )
    .add(
        uses="jinahub://AnnLiteIndexer", # Store vectors and metadata on disk
        uses_with={
            "index_traversal_paths": "@c",
            "search_traversal_paths": "@c",
            "columns": [("element_type", "str")],
            "n_dim": 512
            },
        install_requirements=True,
        name="all_indexer"
    )
)
with flow:
    flow.index(docs)
    flow.block()
#   client = Client(port=flow.port)
#   docs = client.post("/index", docs, request_size=1, show_progress=True, target_executor="(index_*|all_*)")
#   flow.block()