from ..models import Corpus
import os

def validate_corpus_chunks(corpus: Corpus, size_tolerance = 0.01):
    chunks_path = corpus.get_chunks_path()
    total_chunks = corpus.total_chunks
    max_chunk_size_mb = corpus.chunk_size_mb * (1 + size_tolerance)
    if not os.path.exists(chunks_path):
        raise Exception(f"Error validating corpus chunks. Directory {chunks_path} does not exist")
    num_chunks = 0
    for item in os.listdir(chunks_path):
        item_path = os.path.join(chunks_path, item)
        if not os.path.isfile(item_path):
            raise Exception(f"Error validating corpus chunks. Item {item} is not a file")
        if not str(item).endswith(".txt"):
            raise Exception(f"Error validating corpus chunks. Item {item} is not a .txt file")
        item_size_mb = os.path.getsize(item_path) / 1024 / 1024
        if item_size_mb > max_chunk_size_mb:
            raise Exception(f"Error validating corpus chunks. Item {item} has size {item_size_mb:.2f} MB > max {max_chunk_size_mb:.2f}")
        num_chunks += 1
    if num_chunks != total_chunks:
        raise Exception(f"Error validating corpus chunks. Counted {num_chunks} chunks (expected {total_chunks})")