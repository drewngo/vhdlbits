# The VHDLBits cloud grader. Built from the repo root by grader/deploy.sh (Cloud Build).
FROM debian:trixie-slim
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends python3 ghdl procps \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY check.py ./
COPY grader/server.py grader/
COPY problems problems
COPY solutions solutions
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
# Runs as root so it can hand each submission to user nobody; see grader/server.py.
CMD ["python3", "/app/grader/server.py"]
