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

For image-file based ECS deployment, build and export a reusable artifact:

```bash
scripts/build-image.sh --version v2026.06.24-1
```

This creates:

```bash
dist/images/ai-tech-daily-brief-v2026.06.24-1.tar.gz
```

Upload the image artifact and deployment templates to ECS:

```bash
scripts/upload-image-to-ecs.sh \
  --host <ecs-ip-or-domain> \
  --user root \
  --artifact dist/images/ai-tech-daily-brief-v2026.06.24-1.tar.gz \
  --image ai-tech-daily-brief:v2026.06.24-1
```

Then load the image on ECS:

```bash
cd /opt/ai-tech-daily-brief
gzip -dc ai-tech-daily-brief-v2026.06.24-1.tar.gz | docker load
docker images | grep ai-tech-daily-brief
```

The registry workflow is still supported when an image registry is available:

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
- `SUMMARY_MODEL_API_KEY` must be a SiliconFlow API key
- `SUMMARY_MODEL_API_URL=https://api.siliconflow.cn/v1/chat/completions`
- `SUMMARY_MODEL_BASE_URL=https://api.siliconflow.cn/v1` is kept only for backward compatibility
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

docker images | grep ai-tech-daily-brief
docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-env
docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-summary-model
docker run --rm --env-file /etc/ai-tech-daily-brief/env "$AI_TECH_DAILY_BRIEF_IMAGE" validate-smtp
```

`validate-summary-model` prefers `SUMMARY_MODEL_API_URL`. If it is not set, it builds the endpoint from `SUMMARY_MODEL_BASE_URL` by appending `/chat/completions`.

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
