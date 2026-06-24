FROM mcr.microsoft.com/playwright/python:v1.49.1-noble

ENV TZ=Asia/Shanghai \
    PYTHONUNBUFFERED=1 \
    OUTPUT_ROOT=/app/output \
    LOG_ROOT=/app/logs \
    TMP_ROOT=/app/tmp \
    STATE_ROOT=/app/state

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      fonts-noto-cjk \
      fonts-noto-color-emoji \
      tzdata \
    && ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime \
    && echo Asia/Shanghai >/etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY package.json ./
RUN npm install --omit=dev

RUN groupadd --system --gid 10001 ai-brief \
    && useradd --system --uid 10001 --gid ai-brief --home-dir /app --shell /usr/sbin/nologin ai-brief

COPY app ./app
COPY config ./config
COPY references ./references
COPY runtime ./runtime
COPY deploy/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN mkdir -p /app/output /app/logs /app/tmp /app/state \
    && chown -R ai-brief:ai-brief /app \
    && chmod +x /usr/local/bin/entrypoint.sh

USER ai-brief

ENTRYPOINT ["entrypoint.sh"]
CMD ["validate-env"]
