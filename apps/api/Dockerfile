FROM python:3.12-slim
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir .
COPY app app
RUN mkdir -p data workspace && chown -R app:app /app
USER app
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]

