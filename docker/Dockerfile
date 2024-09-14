# syntax=docker/dockerfile:1
# ========================================
# Export the poetry lock file to a requirements.txt file

FROM docker.io/library/python:3.12-alpine AS poetry-exporter

WORKDIR /work

# Install poetry and the export plugin
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install poetry poetry-plugin-export

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

# Export the lock file to a requirements.txt file
RUN poetry export -o requirements.txt

# ========================================
# Build the final image

FROM docker.io/library/python:3.12-alpine

WORKDIR /app

# Install the dependencies
COPY --from=poetry-exporter /work/requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install pip wheel --upgrade \
 && python -m pip install -r requirements.txt

# Copy the application code
COPY app app
COPY docker/docker-entrypoint.py docker-entrypoint.py
COPY docker/gunicorn-config.py gunicorn-config.py

EXPOSE 80
CMD ["python", "docker-entrypoint.py"]