# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.14-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install build dependencies for greenlet
RUN apk add --no-cache build-base

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Install the dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy the application code
COPY app app
COPY docker/docker-entrypoint.py ./

EXPOSE 80
CMD ["uv", "run", "docker-entrypoint.py"]