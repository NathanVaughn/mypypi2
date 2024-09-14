# syntax=docker/dockerfile:1
# ========================================
# Export the poetry lock file to a requirements.txt file

FROM docker.io/library/python:3.12-alpine AS poetry-exporter

WORKDIR /work

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install poetry poetry-plugin-export

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry export -o requirements.txt

# ========================================
# Build the final image

FROM docker.io/library/python:3.12-alpine

WORKDIR /app

COPY --from=poetry-exporter /work/requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install pip wheel --upgrade \
 && python -m pip install -r requirements.txt

COPY app app

CMD ["gunicorn", "--bind=0.0.0.0:80", "app.wsgi:create_app()"]