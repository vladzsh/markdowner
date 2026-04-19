# markdowner

CLI що перетворює URL / audio / video у структуровані `.md` файли для LLM Wiki.

Пайплайн: **ingest → transcribe → clean → emit**.

Повна специфікація та motivation — в Obsidian: `Notes/Markdowner — ідея утиліти.md`.

## Install

```bash
uv sync
```

## Usage

```bash
# URL (YouTube / Vimeo / подкаст)
uv run markdowner https://youtube.com/watch?v=XXX

# Локальний файл
uv run markdowner ./recording.m4a

# З cleanup (opt-in, може галюцинувати)
uv run markdowner --clean <input>
```

Output — `.md` з YAML-frontmatter, готовий під drop у `~/Documents/Obsidian/Life/Raw/<Topic>/`.

## Dev

```bash
uv run pytest
uv run ruff check
```

## Status

Skeleton. Логіка модулів — TODO. Див. MVP scope у Obsidian-нотатці.
