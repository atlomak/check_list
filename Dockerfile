FROM python:3.11 as base
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base as src
COPY src/ /code/src
COPY tests/ /code/tests

FROM src as unittests
RUN ["pytest","--ignore=tests/database/"]