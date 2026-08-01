# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Django 5.2 + DRF API behind idiomstats.com. This repo is one of three that make up the site — see
`../CLAUDE.md` in the parent workspace for how it fits with `portfolio_frontend` and
`portfolio_compose`, and for the DEV / DOCKER-DEV / production run modes. Nothing here is meant to be
served directly to browsers: nginx (in the frontend container) terminates TLS and proxies
`^/(admin|.*-api|api-auth)/` to gunicorn on `:8000`.

## Layout

- `djangobackend/` — project config. `settings.py`, `urls.py` (mounts `core-api/`, `idioms-api/`,
  `admin/`, `api-auth/`), `wsgi.py` (what gunicorn serves).
- `idioms/` — the real application: corpora, idioms, regex searches, matches.
- `core/` — Job / Project / Technology models at `/core-api/`. Vestigial portfolio content; the SPA
  has no live route that consumes it. Don't invest here without checking that's still intended.
- `corpora` — **symlink** to `../corpora/`. Untracked, gitignored. In the container this path is a
  bind mount instead.
- `portfolio-backend-env/` — local venv (Python 3.12). The container uses Python 3.11.7-slim, so the
  two Python versions differ; keep code compatible with 3.11.
- `db.sqlite3` — leftover. The sqlite `DATABASES` block is commented out; every mode uses Postgres.

`djangobackend/urls.py` builds a `core_router` at module level that is never added to `urlpatterns` —
the real routers live in each app's `urls.py`. Harmless, but don't mistake it for the live config.

## The search subsystem

This is the part worth understanding before changing anything in `idioms/`.

**Models** (`idioms/models.py`): `Corpus` describes chunk files on disk (`chunks_directory`
resolved against `settings.CORPUS_DIR` = `BASE_DIR/corpora/`, plus `total_chunks`, `chunk_size_mb`,
`total_word_count`). A search is either against a stored `Idiom` (which carries its own `regex`) or a
`CustomRegex` row created on the fly — `SearchSession` has a nullable FK to each and
`get_regex()` picks whichever is set. `RegexMatch` stores one row per hit with surrounding context;
`SearchFailure` records per-chunk errors.

**Flow** (`idioms/views.py:start_search` → `idioms/services/corpus_search.py`):

1. `start_search` requires `corpus_id` plus exactly one of `idiom_id` / `custom_regex_pattern`
   (supplying both is a 400).
2. `services/corpus_validation.py:validate_corpus_chunks` walks the chunk directory and rejects the
   search unless every entry is a `.txt` file within `chunk_size_mb * 1.01` and the file count
   equals `total_chunks`. **A `Corpus` row whose metadata drifts from disk makes every search against
   it fail with a 400.**
3. A daemon `threading.Thread` runs the search. There is no Celery, no queue, no shared cancellation
   — the search lives inside a gunicorn worker (3 workers, see `gunicorn.conf.py`) and dies with it.
   A container restart orphans in-flight sessions as permanently incomplete.
4. The worker reads each chunk fully into memory, splits on `\n`, `re.finditer`s each line, and saves
   matches. After each chunk it updates `completed_chunks`, `total_matches`, `p_hat`, `p_hat_sigma`
   and `save()`s — that DB row is the only progress channel the client has.
5. Per-chunk exceptions increment `failed_chunks` and create a `SearchFailure`; a failure *outside*
   the chunk loop sets `completed_chunks = failed_chunks = -1` and `is_completed = True` as a
   sentinel before re-raising.

**Validation is split across the HTTP/thread boundary, which shapes how errors surface.** Corpus
problems are caught synchronously and return 400. Pattern problems are not: the "regex too short"
guard (`len < 10`) lives in the *worker*, so `POST start_search/` returns 200 with a `search_id` and
the failure only appears as the `-1` sentinel on the next poll. The client has no error string to
show. Anything you want reported as a proper 400 must be checked in `start_search` itself.

Chunks are iterated with a bare `os.listdir` — **no `sorted()`** — so progress does not advance in
`chunk_000000 → chunk_0000NN` order. The `words_searched` estimate assumes uniform words-per-chunk
over whatever order the filesystem returns, which compounds the "last chunk is short" inaccuracy
already flagged in a TODO there.

**Client contract:** the SPA polls `GET /idioms-api/searchsessions/<search_id>/` (lookup is by the
`search_id` UUID, not pk) with `?include_match_ids=true`, which appends a `match_ids` list outside the
serializer. It then hydrates match text through `POST /idioms-api/bulk_matches/`, which returns
`{matches, missing_ids}` and tolerates ids that no longer exist.

**Hardcoded coupling to watch:** `corpus_search.py` duplicates the `RegexMatch` column widths as
local constants (`context_radius_max = 127`, `match_text_length_max = 63`) because reading
`max_length` off the model attribute raised `AttributeError` — there's a comment explaining this.
Widening those fields means editing the migration *and* those constants. A match longer than
`match_text_length_max` raises, which fails the whole chunk. `start_search` also overrides the
function's `context_radius_ideal` default of 63 — but **positionally**, via
`args=(search.search_id, 127)`, so inserting a parameter into
`search_corpus_chunks_for_pattern` silently rebinds that `127`.

`p_hat`/`p_hat_sigma` come from `calcFrequencyStatistic` — a Wald 1-sigma interval on a binomial
proportion. It divides by `words_searched`, which is estimated as
`completed_chunks / total_chunks * total_word_count`, so it is only as good as the `Corpus` metadata
(and is noted as inaccurate near the end of a search, where the last chunk is short).

## Throttling

`idioms/throttles.py` defines four `AnonRateThrottle` subclasses; `settings.py` sets a global
`anon: 8/second`. `start_search` carries both a burst (10/min) and sustained (100/day) throttle —
these are deliberately tuned for a public demo and were loosened once already. Because DRF keys
`AnonRateThrottle` on IP, everything behind the nginx proxy shares scope unless `X-Forwarded-For`
handling is configured — worth checking before assuming per-user limits work.

`RandomIdiomAnonRateThrottle` guards `IdiomViewSet.random` (`GET /idioms-api/idioms/random/`), but
the frontend's "Choose Random Idiom" button picks client-side from the already-fetched list, so that
endpoint is currently unused.

**Throttle counters are per-worker.** `settings.py` puts a `CACHES` key *inside* the `REST_FRAMEWORK`
dict, where DRF ignores it, and defines no top-level `CACHES`. Django therefore falls back to
`LocMemCache`, which is per-process — with 3 gunicorn workers the effective rate limits are roughly
3× the nominal ones, and they reset on every deploy. Moving that `CACHES` block to module level (or
using Redis) is the fix if limits ever need to be real.

## Permissions

`DEFAULT_PERMISSION_CLASSES` is **`IsAuthenticatedOrReadOnly`**, not `AllowAny`. So anonymous reads
work everywhere and anonymous writes are blocked by default; the three public entry points opt out
explicitly with `@permission_classes([permissions.AllowAny])`: `start_search`, `bulk_matches`, and
`IdiomViewSet.random`. Anything new that anonymous users must POST to needs that decorator.

Half the viewsets are writable, half aren't: `Language`, `Corpus` and `Idiom` are `ModelViewSet`s
(admin-authenticated writes); `SearchSession`, `SearchFailure` and `CustomRegex` are
`ReadOnlyModelViewSet`s. All three `core` viewsets are `ModelViewSet`s.

## Two pieces of live dead code

Both look functional and aren't:

- **`SearchFailureViewSet` raises on any real data.** `serializer.py` declares
  `idiom_pattern = serializers.CharField(source='searchsession.idiom_pattern')`, but that field was
  dropped from `SearchSession` by migration `0008_remove_searchsession_idiom_pattern_and_more`.
  `GET /idioms-api/searchfailures/` returns `[]` today only because no rows exist; it will
  `AttributeError` as soon as one chunk fails — and `corpus_search.py` creates a `SearchFailure` on
  every chunk exception. Fix the serializer before using that endpoint to debug a failing search.
- **`CustomRegexViewSet` is never routed.** It's defined in `views.py` but `idioms/urls.py` registers
  only `languages`, `corpora`, `idioms`, `searchsessions`, `searchfailures`.

## Settings and environment

`settings.py` reads config two different ways depending on run mode, which is the single most
confusing thing about this repo:

- **Committed `main` (production, DOCKER-DEV):** `os.environ` only. Compose injects `SECRET_KEY`,
  `DEBUG`, `DB_*`, `ALLOWED_HOSTS`, `STATIC_ROOT`.
- **`DEV` stash applied:** `django-environ` reads `portfolio_backend/.env`, `DB_HOST` falls back to
  `localhost`, `ALLOWED_HOSTS` is hardcoded, and `django-environ` is added to `requirements.txt`.

So `git restore .` before building an image or committing, or the DEV settings ship to production.

(The hardcoded `CORS_ALLOWED_ORIGINS` / `CSRF_TRUSTED_ORIGINS` vs env-driven `ALLOWED_HOSTS` split is
covered in the root doc.) `corsheaders.middleware.CorsMiddleware` is first in `MIDDLEWARE`, as it
must be.

`LOGGING` sets the `django` and `django.server` loggers to `DEBUG` (Django's default is INFO), and
the console handler is filtered by `require_debug_true` — so with `DEBUG=False` in production the
console handler drops everything and only `mail_admins` remains for the `django` logger. Container
logs come mostly from gunicorn, which is configured with `loglevel = 'debug'`, access and error logs
to stdout/stderr, and `capture_output = True`.

## Container entry

`Dockerfile` (python:3.11.7-slim) installs `requirements.txt` plus `gunicorn`, copies the source, and
runs `deploy-entrypoint.sh`, which on every container start does:

```sh
python manage.py collectstatic --noinput   # into the shared django-static volume
python manage.py migrate --noinput
gunicorn -c /app/gunicorn.conf.py djangobackend.wsgi:application
```

Migrations therefore run automatically on deploy — there is no separate migrate step, and a bad
migration takes the container down on start.

## Commands

```bash
source /home/evanshaped/portfolio_site/portfolio_backend/portfolio-backend-env/bin/activate
python manage.py runserver          # shell alias: djman runserver
python manage.py makemigrations idioms
python manage.py migrate
python manage.py check
python manage.py createsuperuser
python manage.py test               # whole suite
python manage.py test idioms        # one app
python manage.py test idioms.tests.SomeTestCase.test_method
```

`core/tests.py` and `idioms/tests.py` are still empty stubs — `manage.py test` passes trivially. Any
test touching the search will need a `Corpus` row plus real chunk files on disk, since
`validate_corpus_chunks` hits the filesystem.

## Adding a corpus

Data, not code: put chunk files under `../corpora/<dir>/` (uniform `.txt`, ~10 MB each), then create
the `Corpus` row via Django admin with `chunks_directory`, `total_chunks`, `chunk_size_mb` and
`total_word_count` matching what's on disk. Everything in `idioms/admin.py` is registered with a bare
`admin.site.register([...])`, so the admin gives you plain default forms. On the droplet the chunk
files have to be copied over separately (they're gitignored) — `scp` was used previously.

## Agent skills

### Issue tracker

Issues live in this repo's GitHub Issues, managed via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default label vocabulary (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`) used as-is. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout: `CONTEXT.md` + `docs/adr/` at the repo root. See `docs/agents/domain.md`.
