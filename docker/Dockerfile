# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Install the dependencies
RUN --mount=type=cache,target=/var/cache/apk \
    ln -s /var/cache/apk /etc/apk/cache \
 && apk add postgresql-dev
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the application code
COPY app app
COPY docker/docker-entrypoint.py ./

EXPOSE 80
CMD ["uv", "run", "docker-entrypoint.py"]