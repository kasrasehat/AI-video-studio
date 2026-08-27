# full-ai-video-system

An agent-driven film studio: give it a story idea, choose live action, animation, or a hybrid, and direct it through gated production stages. It produces a coherent film with speaking characters from short AI-generated clips (Seedance via Higgsfield, with Kling/Veo and other routed models for suitable non-dialogue scenes).

You are the **Director**: the agent writes, plans, directs, generates and edits, but every creative stage stops at your approval gate — story, scenes, direction, locked characters/voices, storyboards, clips, final cut. Live-action and hybrid projects use the `seedance-clean` prompt profile; animation retains the established `seedance-prompting` profile.

## Setup

1. **Python** via uv (the system Anaconda 3.8 on this machine has a broken user-site `attr` shadow — use the venv):
   ```
   uv venv .venv --python 3.11
   uv pip install -r requirements.txt --python .venv/Scripts/python.exe
   ```
   Run tools as `.venv/Scripts/python scripts/checkpoint.py …` and tests as `.venv/Scripts/python -m pytest`.
2. **ffmpeg** on PATH (assembly & QC).
3. **Keys:** copy `.env.template` → `.env` and fill in Higgsfield (video+images), ElevenLabs (voice samples, music, SFX), Google (Nano Banana), OpenAI (optional).
4. **MCP:** `.mcp.json` configures the Higgsfield MCP server (reads keys from `.env`).

## Usage (Claude Code)

```
/new-film            # start a production — the agent interviews you, then walks the pipeline
/resume <slug>       # continue a production from its last checkpoint
/status <slug>       # stage-by-stage progress table
/gallery <slug>      # open the HTML gallery to compare variants (characters, storyboards…)
```

Under Cursor/Codex the same flows work sequentially — see `AGENT_GUIDE.md` → harness matrix.

## Try it without spending anything

```
python scripts/checkpoint.py init my-test --title "Test film" --dry-run
```

then tell the agent to run the pipeline: `dry_run` swaps every generation call for fixture placeholders while exercising all artifacts, QA loops and gates.

## Verify the scaffold

```
pytest
```

## Layout

See `PROJECT_CONTEXT.md`. Rules of engagement for agents: `AGENT_GUIDE.md`. Pipeline definition: `pipeline.yaml`. Per-production state: `projects/<slug>/`.
