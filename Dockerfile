FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
# Install everything except GDAL first, then install GDAL matching the system version
RUN pip install --no-cache-dir $(grep -v "^GDAL" requirements.txt | tr '\n' ' ') && \
    pip install --no-cache-dir GDAL=="$(gdal-config --version)"

COPY . .

EXPOSE 8000
CMD ["gunicorn", "radoninohio.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
