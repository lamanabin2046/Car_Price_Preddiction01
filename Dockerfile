# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Install system dependencies (git + build tools, so pip installs don't fail)
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment inside the container
RUN python -m venv /opt/venv

# Make sure the virtual environment's bin directory is in PATH
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install dependencies + ipykernel inside virtual environment
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install ipykernel notebook

# Copy all other project files
COPY . .

# Register the virtual environment as a Jupyter kernel globally inside container
RUN python -m ipykernel install --name=venv --display-name "Python (venv)"

# Expose Dash default port
EXPOSE 8050 8888

# Default command: run Dash app using the virtual environment's Python
CMD ["python", "app.py"]
