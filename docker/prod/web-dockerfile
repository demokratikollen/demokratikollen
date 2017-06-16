FROM python:3.6

# Install needed packages.
RUN apt-get update && apt-get install -y \
    git \
    mongodb-clients \
    postgresql-client \
 && rm -rf /var/lib/apt/lists/*

# Update pip/setuptools
RUN pip install --no-cache-dir -U pip setuptools

# Copy the source.
COPY . /src 
WORKDIR /src

# Install python deps
RUN pip install --no-cache-dir -r demokratikollen/requirements.txt

EXPOSE 8000
