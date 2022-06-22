FROM python:3.10

WORKDIR /src

ENV POETRY_VERSION=1.1.13

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml /src/

RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

COPY docker-entrypoint.sh app /src/

ENTRYPOINT [ "./docker-entrypoint.sh" ]
