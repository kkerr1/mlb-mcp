# Use Python 3.12 slim as base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_CACHE_DIR=/tmp/uv-cache \
    PORT=8000

# Install uv directly (most dependencies should be available in the base image)
RUN pip install uv

# Set work directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Create a minimal package structure for uv sync
RUN mkdir -p mlb_stats_mcp && touch mlb_stats_mcp/__init__.py

# Install dependencies
RUN uv sync --frozen

# Copy the entire project
COPY mlb_stats_mcp /app/mlb_stats_mcp

# Create logs directory
RUN mkdir -p /app/logs

# Install the package in development mode system-wide
RUN uv pip install --system -e .

# Patch data for pybaseball
RUN uv run python mlb_stats_mcp/utils/scripts/data_download.py

# Expose port for HTTP transport
EXPOSE 8000

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Run the MCP server with HTTP transport
CMD ["python", "-m", "mlb_stats_mcp.server", "--http"]
