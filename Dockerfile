FROM python:3.11-slim

# Install Node.js (>=18) and essential tools
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    nodejs npm \
    curl \
  && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -s /bin/bash appuser

# Copy uv from official image
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first for caching
COPY package.json package-lock.json ./
COPY frontend/package.json frontend/package-lock.json ./frontend/
COPY backend/pyproject.toml backend/uv.lock ./backend/

# Install dependencies (Node + Python)
RUN npm ci \
  && npm ci --prefix frontend \
  && cd backend && uv sync --frozen

# Copy source code
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Healthcheck for backend API
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/api/graph/project/list || exit 1

EXPOSE 3000 5001

# Start both frontend and backend (production mode)
CMD ["npm", "run", "dev"]