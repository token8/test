# Laya decision server (upstream laya-serve, Jev wire protocol) for the decision panel.
# Build:  docker build -t laya-serve decision-layer/docker
# Run:    docker compose -f decision-layer/docker/compose.yaml up -d
FROM python:3.12-slim

ARG LAYA_VERSION=0.3.20
# CPU-only torch keeps the image near 1 GB instead of pulling CUDA wheels.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
 && pip install --no-cache-dir "laya[serve]==${LAYA_VERSION}" \
 && useradd --system --uid 10001 --home-dir /models laya \
 && mkdir -p /models && chown laya /models

USER laya
ENV HF_HOME=/models/hf \
    USE_TF=0 \
    LAYA_HOST=0.0.0.0 \
    LAYA_PORT=8771 \
    LAYA_MODELS=english,multilingual \
    LAYA_PRELOAD=1

EXPOSE 8771
HEALTHCHECK --interval=30s --timeout=5s --start-period=180s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8771/health', timeout=4).status == 200 else 1)"

CMD ["laya-serve"]
