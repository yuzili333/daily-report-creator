# Runtime directories

The container writes only to these mounted runtime paths:

- `/app/output`: generated `brief.json`, `brief.html`, and `brief.pdf`
- `/app/logs`: command logs and validation metadata
- `/app/tmp`: temporary files

On ECS these paths are mounted from:

- `/var/lib/ai-tech-daily-brief/output` -> `/app/output`
- `/var/log/ai-tech-daily-brief` -> `/app/logs`

The production entrypoint does not read from `~/.codex/skills` and uses only files copied into the image.
