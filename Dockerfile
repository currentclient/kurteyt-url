# > Builds local fastapi app
FROM python:3.12

# Needs to be app to overrite default app from fastapi image
WORKDIR /app/

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./pyproject.toml ./poetry.lock* /app/

# Install libs
RUN poetry install --no-root

# Docker compose mounts the app into this for us, so dont think i need it
# # Put module into app
# COPY module-app /app

ENV PYTHONPATH=/app
