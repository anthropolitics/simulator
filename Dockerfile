FROM python:3.13-slim
COPY --from=ghcr.io/astral-sh/uv:0.11.32 /uv /bin/uv
WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev
EXPOSE 8000
# Un seul processus web, qui lance ses deux processus de calcul. Traefik transmet l'adresse IP du visiteur, utilisée par la limite de calculs.
CMD ["/app/.venv/bin/uvicorn", "simulator.api:app", "--host", "0.0.0.0", "--port", "8000", "--forwarded-allow-ips", "*"]
