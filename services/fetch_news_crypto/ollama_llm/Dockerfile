# Use official Ollama base image
FROM ollama/ollama:latest

# Install curl (for health checks or wait loop)
RUN apt-get update && apt-get install -y curl && apt-get clean

# Clear original entrypoint
ENTRYPOINT []

# Start Ollama and pull llama3 before running it
CMD ["/bin/sh", "-c", "\
  ollama serve & \
  until curl -s http://localhost:11434 > /dev/null; do sleep 1; done; \
  ollama pull llama3; \
  pkill -f 'ollama serve'; \
  exec ollama serve"]

