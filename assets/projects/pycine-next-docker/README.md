# pycine-next

Example of a FastApi project using `uv` and deployed in a docker container.

## Project setup (local)

Install dependencies with uv
```bash
uv init pycine-next
uv add fastapi
uv add requests uvicorn pydantic-settings
```

### run (local)

```bash
python main.py
```

## Dockerfile (uv based)

- [Docs](https://docs.astral.sh/uv/guides/integration/docker/#available-images)
- [Project example](https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile)

### Dockerfile

Place this file in project root:

```dockerfile
FROM python:3.13-slim-bookworm
# pin uv version (recommended)
COPY --from=ghcr.io/astral-sh/uv:0.6.3 /uv /uvx /bin/
# or use the latest:
# COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen
CMD ["uv", "run", "main.py"]

```

### .dockerignore

```
.venv
```

### build image

```bash
sudo docker build -t pycine-next .
```

check image was created:
```bash
sudo docker images
```
outupt:

```console
REPOSITORY    TAG       IMAGE ID       CREATED          SIZE
pycine-next   latest    724f22b7d04a   10 minutes ago   175MB
```

### docker run

Start the container on port 8000

```bash
sudo docker run -it --rm --publish 8000:8000 pycine-next
```

### test

in terminal make a http request:

```bash
# PUT request
http PUT 127.0.0.1:8000
# GET request
http GET 127.0.0.1:8000
```

output: 

```console
HTTP/1.1 200 OK
content-length: 219
content-type: application/json
date: Thu, 27 Feb 2025 21:40:36 GMT
server: uvicorn

{
    "body": "",
    "headers": {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "connection": "keep-alive",
        "content-length": "0",
        "host": "127.0.0.1:8000",
        "user-agent": "HTTPie/3.2.2"
    },
    "message": "request received",
    "method": "PUT"
}
```

## Docker compose

- create the file `compose.yml`

```yaml
services:
  web:
    build: .
    ports:
      - "8000:8000"
    develop:
      watch:
        - action: sync
          path: .
          target: /app
          ignore:
            - .venv/
        - action: rebuild
          path: ./uv.lock
```

Start the `run.sh` script, which will call: `docker run` with mount option.

```bash
sudo ./run.sh
```

check if the container is running:

```bash
sudo docker ps
```

----

## Dockerfile (pip based)

Dockerfile example using pip instead of uv:

```dockerfile
FROM python:3.13-slim
WORKDIR /pycine-next/
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
ENTRYPOINT [ "python", "main.py" ]
```
