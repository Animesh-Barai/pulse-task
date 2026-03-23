FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies and surgically purge the 4GB+ of bundled CUDA 12 runtimes.
# This forces the service to use your host's native CUDA 13.1 libraries.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y nvidia-cuda-nvrtc-cu12 nvidia-cuda-runtime-cu12 \
                         nvidia-cuda-cupti-cu12 nvidia-cudnn-cu12 \
                         nvidia-cublas-cu12 nvidia-cufft-cu12 \
                         nvidia-curand-cu12 nvidia-cusolver-cu12 \
                         nvidia-cusparse-cu12 nvidia-nccl-cu12 \
                         nvidia-nvtx-cu12 nvidia-nvjitlink-cu12 \
    && rm -rf /root/.cache/pip

# Copy application code
COPY . .

# Expose port
EXPOSE 8001

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
