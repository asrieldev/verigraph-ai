FROM python:3.12-slim
RUN pip install --no-cache-dir pytest==8.3.4 semgrep==1.99.0
RUN useradd --create-home --uid 10001 verifier
USER verifier
WORKDIR /workspace
ENTRYPOINT ["/bin/sh","-lc"]

