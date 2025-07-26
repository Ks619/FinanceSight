# Use a lightweight Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set PYTHONPATH so Python can locate the aggregator package
ENV PYTHONPATH=/app

# Copy all project files (main.py, utils.py, tests/, etc.)
COPY . .

# Run pytest in verbose mode, targeting the tests/ directory
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

CMD ["pytest", "tests", "--asyncio-mode=strict", "-v"]
