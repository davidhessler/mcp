FROM public.ecr.aws/docker/library/python:3.13-slim as builder

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_PREFERENCE=only-system \
    UV_FROZEN=true \
    PATH="/root/.local/bin:$PATH"

RUN mkdir -p /root/.local

WORKDIR /app

# Install uv and dependencies in single layer
RUN apt-get update && apt-get install -y --no-install-recommends curl && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/uv \
    /root/.local/bin/uv sync --frozen --no-install-project --no-dev --no-editable

COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    /root/.local/bin/uv sync --frozen --no-dev --no-editable

FROM public.ecr.aws/sam/build-python3.13@sha256:0df1547849c376aa21f9c726c0d71c4974415ed4405256f8d79f8c25716a9c63

ENV PATH="/app/.venv/bin:$PATH"

# Install lsof for the healthcheck
# Install other tools as needed for the MCP server
# Add non-root user and ability to change directory into /root
RUN dnf update -y && \
    dnf install -y lsof && \
    dnf clean all -y && \
    rm -rf /var/cache/dnf && \
#    groupadd --force --system app && \
#    useradd app -g app -d /app && \
    chmod o+x /root

COPY --from=builder --chown=app:app /root/.local /root/.local
COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chmod=755 ./docker-healthcheck.sh /usr/local/bin/

#USER app
WORKDIR /app

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD ["docker-healthcheck.sh"]

ENTRYPOINT ["awslabs.aws_sra_mcp_server"]