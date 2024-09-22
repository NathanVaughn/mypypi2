# syntax=docker/dockerfile:1
FROM docker.io/library/python:3.12-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

# Install the dependencies
COPY pyproject.toml uv.lock ./
RUN --mount=type=cache,target=/root/.cache/ /bin/uv sync --frozen

# Copy the application code
COPY app app
COPY docker/docker-entrypoint.py ./

EXPOSE 80
CMD ["uv", "run", "docker-entrypoint.py"]