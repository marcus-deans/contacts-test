FROM python:3.9

# WORKDIR /src

# ENV POETRY_VERSION=1.1.13

# RUN pip install "poetry==$POETRY_VERSION"

# COPY poetry.lock pyproject.toml /src/

# RUN poetry config virtualenvs.create false \
#   && poetry install --no-interaction --no-ansi

# COPY docker-entrypoint.sh app /src/

# ENTRYPOINT [ "./docker-entrypoint.sh" ]


ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_VERSION=1.1.13 \
    YOUR_ENV=development

RUN apk add --no-cache python3-dev gcc libc-dev musl-dev openblas gfortran build-base postgresql-libs postgresql-dev libffi-dev curl

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/install-poetry.py | python -
ENV PATH "/root/.local/bin:$PATH"


# install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi
# RUN poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") --no-interaction --no-ansi
