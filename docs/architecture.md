# O5 Council Architecture

## Product Intent

**O5 Council** is a Python desktop application that lets a user submit a strategic question, planning request, or drafting task to a coordinated council of five AI models accessed through **OpenRouter**. Instead of receiving a single-model response, the user receives a structured deliberation: an initial pass from each council member, one or more critique-and-revision rounds, and a final synthesized answer that reflects areas of agreement, disagreement, and actionable recommendations.

The first implementation targets a practical open-source desktop MVP. The application must feel modern, remain easy to install, and preserve enough internal structure to support future additions such as web search, document ingestion, role-specialized agents, and export pipelines.

## Technology Stack

The application will use **Python 3.11+** with **PySide6** for the desktop interface. PySide6 provides a modern native-capable UI framework, robust threading primitives, and reliable packaging support for open-source desktop distribution. Network requests to OpenRouter will be performed with **httpx** so the app can support timeouts, streaming-friendly upgrades later, and straightforward request instrumentation. Local configuration will be stored in a lightweight JSON settings file inside the user data directory.

| Layer | Choice | Rationale |
| --- | --- | --- |
| Desktop UI | PySide6 | Modern widgets, polished layouts, strong cross-platform support |
| Styling | Qt Style Sheet theming | Simple and portable way to create a modern dark interface |
| HTTP client | httpx | Clean timeout handling and reliable API integration |
| Data modeling | dataclasses + typing | Lightweight, readable, and sufficient for an MVP |
| Persistence | JSON settings file | Easy setup for API key, model selections, and defaults |
| Packaging | PyInstaller | Familiar path for single-folder or single-file desktop builds |

## User Experience Model

The main window should present the application as a command center rather than a chat toy. The left side will hold task composition and run settings. The center will display live council activity and per-round status. The right side will expose final outputs and exports. The goal is to make the council’s process legible without overwhelming the user.

| UI Region | Purpose | Key Controls |
| --- | --- | --- |
| Task composer | Define the assignment | Prompt editor, task mode, optional context |
| Council configuration | Select the five participants | Model pickers, temperatures, per-agent role labels |
| Deliberation controls | Bound the work | Max rounds, consensus target, timeout, start and cancel |
| Live activity feed | Show what the council is doing | Status log, round tracker, progress state |
| Member transcript tabs | Inspect each model’s reasoning output | One tab per council member |
| Final synthesis panel | Present the answer | Consensus summary, final plan, export actions |

## Deliberation Workflow

The MVP will use a deterministic staged workflow rather than a free-form autonomous loop. This keeps cost, latency, and observability under control while still creating the feeling of five models working together.

1. The user submits a task and run settings.
2. The application sends the same brief plus a role-specific system prompt to each of the five selected models.
3. Each model returns an **initial position** containing its analysis, recommendations, assumptions, and unresolved risks.
4. The engine composes a **review packet** summarizing all five positions.
5. Each model receives the packet and is asked to critique the others, identify convergence points, and revise its own answer.
6. After each round, the engine evaluates textual convergence through structured self-report fields such as confidence, preferred option, and whether the model believes a workable consensus has emerged.
7. If the consensus threshold is met or the maximum rounds are reached, the engine calls a designated **synthesizer step** to draft the final response.
8. The final response is displayed together with round history and exportable Markdown.

## Consensus Strategy

Consensus will initially be implemented through explicit structured signals rather than opaque semantic similarity scoring. Each council member will be asked to return a short machine-readable footer or JSON block describing its preferred strategy label, confidence score, and whether it accepts the current emerging consensus. This allows the engine to compute whether the council has converged without relying on brittle heuristic embedding logic in the MVP.

| Signal | Type | Use |
| --- | --- | --- |
| preferred_option | Short string | Tracks which solution the member currently supports |
| confidence | Integer 0-100 | Measures conviction and stability |
| consensus_ready | Boolean | Indicates whether the member believes a final synthesis is justified |
| key_risks | Short list | Carries unresolved objections into the next round |

A run will be considered ready for synthesis when at least a configurable majority of members indicate `consensus_ready = true` and a majority share the same `preferred_option`, or when the round limit is reached and the engine must synthesize a balanced final answer with dissent clearly noted.

## Module Structure

The codebase should be organized so the deliberation engine is separate from the UI. This will make later testing easier and reduce the risk that interface work becomes entangled with network logic.

| Module | Responsibility |
| --- | --- |
| `o5_council/app.py` | Application entry point |
| `o5_council/config.py` | App constants and user-data paths |
| `o5_council/models.py` | Dataclasses for agents, rounds, and run results |
| `o5_council/settings_store.py` | Load and save local user settings |
| `o5_council/openrouter_client.py` | API communication with OpenRouter |
| `o5_council/council_engine.py` | Multi-round deliberation orchestration |
| `o5_council/ui/main_window.py` | Main application window and layout |
| `o5_council/ui/theme.py` | Dark theme styling |
| `o5_council/workers.py` | Background worker for non-blocking council runs |

## Data and Security Model

The user will provide an **OpenRouter API key** within the application settings panel. The key will be stored locally in the user settings file for convenience in the MVP, with clear documentation that local machine security applies. The application will not require any hosted backend. All model requests go directly from the desktop client to OpenRouter.

Because the app is intended for long-form planning and potentially sensitive drafting, the interface should clearly show which models are selected, what context is being sent, and whether the final result is a consensus or a compromise. The app should also make it easy to clear outputs and update the API key.

## MVP Boundaries

The first version should intentionally avoid overexpansion. Web browsing, retrieval augmentation, file attachments, live streaming, and agent tool use can be added later. The initial release should do one thing well: run a transparent five-model deliberation pipeline and produce a useful final answer.

| Included in MVP | Deferred |
| --- | --- |
| Five configurable council members | External web search integration |
| Multi-round critique and revision | File ingestion and retrieval |
| Consensus tracking | Voice interface |
| Final synthesis and exports | Persistent run history database |
| Install script and packaging | Advanced semantic agreement scoring |

## Implementation Notes

The design assumes that the council engine can run in a background worker thread so the interface remains responsive. The engine should emit progress updates after each major step, allowing the UI to update logs, per-member outputs, and round counters. The export format should be Markdown because it is readable, easy to version, and simple to convert later.

This architecture is intended to balance ambition with deliverability. It provides a credible first version of the O5 Council concept while leaving room for deeper research workflows and more autonomous deliberation in subsequent releases.
