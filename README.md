# ai-tech-daily-brief

ECS-ready package for generating and sending the daily AI technology brief.

## Layout

- `app/`: production runtime code for collection, HTML/PDF generation, validation, and SMTP delivery
- `config/`: non-sensitive runtime configuration template
- `deploy/`: Dockerfile, ECS bootstrap script, and systemd units
- `references/`: ranking, source, and visual rules copied into the deployable package
- `runtime/`: runtime directory contract
- `scripts/`: local compatibility wrapper

The production runtime is self-contained. It does not depend on `~/.codex/skills`, launchd, Codex, or Gmail connector access.

## Build and publish

Use explicit version tags only. Do not use `latest` for production.

```bash
VERSION=v2026.06.23-1
ACR_IMAGE=registry.cn-hangzhou.aliyuncs.com/YOUR_NAMESPACE/ai-tech-daily-brief:${VERSION}

docker build -f deploy/Dockerfile -t ai-tech-daily-brief:${VERSION} .
docker tag ai-tech-daily-brief:${VERSION} "${ACR_IMAGE}"
docker push "${ACR_IMAGE}"
```

Set the same image reference in `/etc/ai-tech-daily-brief/env`:

```bash
AI_TECH_DAILY_BRIEF_IMAGE=registry.cn-hangzhou.aliyuncs.com/YOUR_NAMESPACE/ai-tech-daily-brief:v2026.06.23-1
```

## ECS setup

Run the bootstrap script as root on the ECS instance:

```bash
sudo ./deploy/bootstrap-ecs.sh
sudo vi /etc/ai-tech-daily-brief/env
```

Required runtime defaults:

- `SUMMARY_MODEL=Pro/moonshotai/Kimi-K2.6`
- `SUMMARY_MODEL_PROVIDER=moonshotai`
- `SMTP_HOST=smtp.163.com`
- `SMTP_PORT=465`
- `SMTP_USE_TLS=true`
- `MAIL_FROM` must match `SMTP_USERNAME`
- `SMTP_PASSWORD` must be the 163 SMTP authorization code, not the login password

## Validation

After editing `/etc/ai-tech-daily-brief/env`:

```bash
set -a
. /etc/ai-tech-daily-brief/env
set +a

docker pull "$AI_TECH_DAILY_BRIEF_IMAGE"
docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-env
docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-summary-model
docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-smtp
```

SMTP send tests:

```bash
docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-smtp --test-plain
docker run --rm --env-file /etc/ai-tech-daily-brief/env -v /var/lib/ai-tech-daily-brief/output:/app/output:ro "$AI_TECH_DAILY_BRIEF_IMAGE" validate-smtp --test-attachment /app/output/ai-tech-daily-brief-YYYY-MM-DD.pdf
```

## Manual run

```bash
docker run --rm --env-file /etc/ai-tech-daily-brief/env \
  -v /var/lib/ai-tech-daily-brief/output:/app/output \
  -v /var/log/ai-tech-daily-brief:/app/logs \
  "$AI_TECH_DAILY_BRIEF_IMAGE" collect

docker run --rm --env-file /etc/ai-tech-daily-brief/env \
  -v /var/lib/ai-tech-daily-brief/output:/app/output:ro \
  -v /var/log/ai-tech-daily-brief:/app/logs \
  "$AI_TECH_DAILY_BRIEF_IMAGE" push
```

`push` fails if today's PDF does not exist.

## Timers

```bash
sudo systemctl enable --now ai-tech-daily-brief-collect.timer
sudo systemctl enable --now ai-tech-daily-brief-push.timer
systemctl list-timers 'ai-tech-daily-brief-*'
```

Schedule:

- `collect`: daily 01:00 Asia/Shanghai
- `push`: daily 09:00 Asia/Shanghai

Logs:

- `/var/log/ai-tech-daily-brief/collect.log`
- `/var/log/ai-tech-daily-brief/collect.err.log`
- `/var/log/ai-tech-daily-brief/push.log`
- `/var/log/ai-tech-daily-brief/push.err.log`
