# LOCAL_SETUP.md — Local Development Configuration

## Python Environment
- Python: 3.11+
- Package manager: uv
- Virtual env: `.venv/` (created by uv)

## Local Model Setup
- **Primary model**: Google Gemini 2.5 Pro via google-cloud API
- **Local judge model**: TBD (will document when ablation sweep runs)
- **Local open-weight model**: TBD (for ablation comparison)

## Dependencies
```bash
uv sync
uv run python -m kit check
uv run python -m kit artifacts
```

## Dev Evaluation
```bash
uv run python eval/run.py
```

## Stage 2 Environment Simulation
- CPU limit: 2 cores
- Memory limit: 4 GB
- Disk: 1 GB /tmp + $HOME writable, /opt/harness read-only
- Network: WebSocket only, no external API keys
- Time: 6 hours per task

