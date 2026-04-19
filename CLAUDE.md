# markdowner — Claude Code instructions

CLI інструмент. URL / audio / video → structured `.md` для LLM Wiki pipeline.
Повна специфікація: `~/Documents/Obsidian/Life/Notes/Markdowner — ідея утиліти.md`.

## Stack

- Python 3.12+
- `uv` для dependency management
- `typer` — CLI
- `yt-dlp` — ingest (Python API, не subprocess)
- `whisper-cli` — transcribe (subprocess, `ggml-large-v3-turbo.bin`)
- `jinja2` — emit templates
- `pytest` + `ruff` — dev

## Layout

```
src/markdowner/
├── cli.py          — typer entry-point
├── ingest.py       — yt-dlp + HTML fetch
├── transcribe.py   — whisper-cli subprocess wrapper
├── clean.py        — LLM noise-remover (opt-in)
├── emit.py         — Jinja → .md
└── templates/note.md.j2
```

## Commands

```bash
uv sync              # install deps
uv run markdowner <input>
uv run pytest        # tests
uv run ruff check    # lint
uv run ruff format   # format
```

## Конвенції

- Type hints обов'язкові (Python 3.12 syntax: `str | None`, `list[str]`)
- Docstrings Google-style, ВЖЕ у коді короткі (one-liner достатньо)
- Без зайвих коментарів — код має бути самодокументований
- Whisper модель — НЕ хардкодити шлях, читати з конфігу
- Config path: `~/.config/markdowner/config.toml`

## Git

- Remote: `git@github.com-personal:vladzsh/markdowner.git`
- Комміти БЕЗ `Co-Authored-By: Claude` (глобальне правило)
- Commit style: `type(scope): message` (conventional commits)
