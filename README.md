# O5 Council

**O5 Council** is an open-source Python desktop application that treats AI work as a structured council rather than a one-model chat. A user submits a planning, research, policy, or drafting task, and five configurable models routed through **OpenRouter** deliberate across multiple rounds before producing a final synthesis.

The project is designed as a practical desktop MVP. It focuses on transparency, configurable model selection, and a visible critique-and-revision workflow so the user can inspect how each council member moved toward consensus.

## Core Idea

Instead of asking one model for a final answer, O5 Council asks five models to evaluate the same task from different roles. Each model returns its own initial position, critiques the others in subsequent rounds, and reports a machine-readable consensus signal. Once the council converges or reaches its round limit, the application produces a final report that captures both agreement and dissent.

| Capability | Description |
| --- | --- |
| Five-member council | Each member can use a different OpenRouter model and role |
| Multi-round deliberation | Members revise their views after reviewing the prior round |
| Consensus tracking | The engine checks majority support and readiness to converge |
| Final synthesis | The chair model produces a structured Markdown report |
| Desktop interface | A modern PySide6 UI exposes settings, transcripts, and exports |

## Technology Stack

The application is built with **Python 3.11+**, **PySide6**, and **httpx**. Requests are sent directly from the desktop client to OpenRouter, so there is no required backend service. Local settings are stored in a JSON configuration file under the user data directory.

| Layer | Choice |
| --- | --- |
| UI framework | PySide6 |
| HTTP client | httpx |
| Packaging metadata | `pyproject.toml` |
| Export format | Markdown |
| Distribution approach | `pip` install plus a simple launch script |

## Repository Layout

| Path | Purpose |
| --- | --- |
| `o5_council/app.py` | Application entry point |
| `o5_council/openrouter_client.py` | OpenRouter request handling |
| `o5_council/council_engine.py` | Multi-round council orchestration |
| `o5_council/workers.py` | Background worker integration for the UI |
| `o5_council/ui/main_window.py` | Main desktop interface |
| `docs/architecture.md` | Detailed architectural rationale |
| `scripts/install.sh` | Simple local installation helper |

## Installation

The simplest path is to clone the repository and run the install script. The script creates a virtual environment, installs the package in editable mode, and places the launcher inside that environment.

```bash
git clone https://github.com/skizap/O5-Council.git
cd O5-Council
bash scripts/install.sh
```

After installation, launch the app with:

```bash
source .venv/bin/activate
o5-council
```

## Manual Installation

If you prefer to manage the environment yourself, use the following commands.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
o5-council
```

## Running the Application

When the application opens, provide your **OpenRouter API key**, choose the five models you want to use, set the maximum rounds and consensus target, and then submit a task. The right-hand side of the window will display a live activity log, one transcript tab per council member, and the final synthesis once the run is complete.

| Input Area | What You Control |
| --- | --- |
| OpenRouter Connection | API key, referer URL, app title |
| Deliberation Settings | Task mode, maximum rounds, consensus target, request timeout |
| Council Members | Name, role, model, and temperature for each of the five agents |
| Task Composer | Primary request and optional contextual constraints |

## Current MVP Scope

The current version intentionally focuses on a transparent deliberation workflow. It does not yet perform native web browsing, file ingestion, retrieval augmentation, or external tool execution. Those features can be added later without replacing the current architecture.

| Included Now | Planned Later |
| --- | --- |
| Five configurable council members | Web research tools |
| Consensus and round tracking | File and document ingestion |
| Final Markdown synthesis | Streaming responses |
| Desktop export workflow | Persistent run history |

## OpenRouter Notes

O5 Council is designed around the [OpenRouter quickstart documentation](https://openrouter.ai/docs/quickstart). It uses the standard chat-completions endpoint and sends optional attribution headers so the application can identify itself cleanly when requests are made.

## License

This repository is released under the **MIT License**.
