# Runtime directories

The container writes only to these mounted runtime paths:

- `/app/output`: generated `brief.json`, `brief.html`, and `brief.pdf`
- `/app/logs`: command logs and validation metadata
- `/app/tmp`: temporary files
- `/app/state`: push sent/failed markers for idempotency and retries

On ECS these paths are mounted from:

- `/var/lib/ai-tech-daily-brief/output` -> `/app/output`
- `/var/log/ai-tech-daily-brief` -> `/app/logs`
- `/var/lib/ai-tech-daily-brief/state` -> `/app/state`

The production entrypoint does not read from `~/.codex/skills` and uses only files copied into the image.
