# Use Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install uv for faster package management
RUN pip install uv

# Copy dependency files (pyproject.toml and uv.lock for reproducible builds)
COPY pyproject.toml uv.lock .python-version ./

# Install dependencies using uv sync (creates .venv in container)
RUN uv sync --frozen --no-dev

# Copy application code
COPY main.py ./

# Expose port 1000
EXPOSE 1000

# Run the FastAPI application using the virtual environment created by uv
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "1000"]
