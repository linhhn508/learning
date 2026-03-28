FROM python:3.12-slim

WORKDIR /web-service

RUN pip install uv

COPY pyproject.toml ./

RUN uv sync

COPY . .

CMD ["uv", "run", "--", "flask", "run", "-h", "0.0.0.0", "-p", "5000"]