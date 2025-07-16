import os
import re
from ..models import SearchSession, Corpus, SearchFailure

def search_corpus_chunks_for_pattern(search_id):
    search = SearchSession.objects.get(search_id=search_id)
    chunks_path = search.corpus.get_chunks_path()
    idiom_pattern = search.idiom_pattern

    for chunk_file_name in os.listdir(chunks_path):
        try:
            chunk_path = os.path.join(chunks_path, chunk_file_name)
            chunk_matches = 0
            with open(chunk_path, 'r', encoding='utf-8') as chunk_f:
                content = chunk_f.read()
            lines = content.split('\n')
            del content
            for line_num, line in enumerate(lines):
                matches = re.findall(idiom_pattern, line)
                chunk_matches += len(matches)
            del lines
            search.completed_chunks += 1
            search.total_matches += chunk_matches
            search.save()
        except Exception as e_message:
            search.failed_chunks += 1
            search.save()
            SearchFailure.objects.create(
                searchsession=search,
                chunk_name=chunk_file_name,
                failure_message=e_message,
            )
    search.is_completed = True
    search.save()