FROM python:3.13-slim-bookworm
# pin uv version (recommended)
COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /uvx /bin/
# latest:
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen
CMD ["uv", "run", "main.py"]
