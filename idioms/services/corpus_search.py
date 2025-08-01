import os
import re
from ..models import SearchSession, Corpus, SearchFailure

def search_corpus_chunks_for_pattern(search_id):
    search = SearchSession.objects.get(search_id=search_id)
    try:
        search_corpus_chunks_for_pattern_aux(search)
    except Exception as e:
        search.is_completed = True
        search.failed_chunks = -1
        search.completed_chunks = -1
        search.save()
        raise

def search_corpus_chunks_for_pattern_aux(search: SearchSession):
    chunks_path = search.corpus.get_chunks_path()
    regex_pattern = search.get_regex()
    if not regex_pattern:
        raise Exception("No regex pattern found for search")
    if len(regex_pattern) < 10:
        raise Exception("Regex too short")

    for chunk_file_name in os.listdir(chunks_path):
        try:
            chunk_path = os.path.join(chunks_path, chunk_file_name)
            chunk_matches = 0
            with open(chunk_path, 'r', encoding='utf-8') as chunk_f:
                content = chunk_f.read()
            lines = content.split('\n')
            del content
            for line_num, line in enumerate(lines):
                matches = re.findall(regex_pattern, line)
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