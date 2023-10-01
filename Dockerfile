FROM python:3.11-buster as base

FROM base AS python-deps

RUN pip install pipenv
RUN apt-get update && apt-get install -y --no-install-recommends gcc

COPY Pipfile .
COPY Pipfile.lock .
RUN PIPENV_VENV_IN_PROJECT=1 pipenv install --deploy

FROM base AS runtime

COPY --from=python-deps /.venv /.venv

ENV PATH="/.venv/bin:$PATH"

COPY . .

ENV PYTHONPATH "./"
ENV ENV=prod

CMD python app/main.py