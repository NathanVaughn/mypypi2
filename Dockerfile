# ========================================
# Export the poetry lock file to a requirements.txt file

FROM docker.io/library/python:3.12 AS poetry-exporter

WORKDIR /work

RUN python -m pip install poetry poetry-plugin-export

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

RUN poetry export -o requirements.txt

# ========================================
# Build the final image

FROM docker.io/library/python:3.12

WORKDIR /app

COPY --from=poetry-exporter /work/requirements.txt requirements.txt
RUN python -m pip install pip wheel --upgrade \
 && python -m pip install -r requirements.txt

COPY app app

CMD ["gunicorn", "--bind=0.0.0.0:80", "app.wsgi:create_app()"]