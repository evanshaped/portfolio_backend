import os
import re
from ..models import SearchSession, Corpus, SearchFailure, RegexMatch, CustomRegex

def search_corpus_chunks_for_pattern(search_id, context_radius_ideal=63):
    search = SearchSession.objects.get(search_id=search_id)
    try:
        search_corpus_chunks_for_pattern_aux(search, context_radius_ideal)
    except Exception as e:
        search.is_completed = True
        search.failed_chunks = -1
        search.completed_chunks = -1
        search.save()
        raise

def search_corpus_chunks_for_pattern_aux(search: SearchSession, context_radius_ideal):
    # When running the following lines, I get "AttributeError: 'DeferredAttribute' object has no attribute 'max_length'"
    # Maybe there is a different way to programmatically identify these values from the models or database,
    # but its not a priority. For now I'm setting them manually
    # context_radius_max = min(RegexMatch.context_before.max_length, RegexMatch.context_after.max_length)
    # match_text_length_max = RegexMatch.match_text.max_length
    context_radius_max = 127
    match_text_length_max = 63
    chunks_path = search.corpus.get_chunks_path()
    regex_pattern = search.get_regex()
    if not regex_pattern:
        raise Exception("No regex pattern found for search")
    if len(regex_pattern) < 10:
        raise Exception("Regex too short")

    def save_match_to_database(match: re.Match[str], line):
        match_text_length = match.end() - match.start()
        if match_text_length > match_text_length_max:
            raise Exception(f"Regex match of length {match_text_length} exceeds max length of {match_text_length_max}")
        context_radius = min(context_radius_ideal, context_radius_max)
        text_before = line[max(0,match.start()-context_radius):match.start()]
        text_match = line[match.start():match.end()]
        text_after = line[match.end():min(len(line),match.end()+context_radius)]
        RegexMatch.objects.create(
            searchsession=search,
            context_before=text_before,
            match_text=text_match,
            context_after=text_after
        )

    def match_regex_in_line(line):
        matches = re.finditer(regex_pattern, line)
        matches_count = 0
        for match in matches:
            save_match_to_database(match, line)
            matches_count += 1
        return matches_count

    for chunk_file_name in os.listdir(chunks_path):
        try:
            chunk_path = os.path.join(chunks_path, chunk_file_name)
            chunk_matches = 0
            with open(chunk_path, 'r', encoding='utf-8') as chunk_f:
                content = chunk_f.read()
            lines = content.split('\n')
            del content
            for line_num, line in enumerate(lines):
                chunk_matches += match_regex_in_line(line)
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