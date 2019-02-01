FROM python:3.6

# Add the nodejs repo
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -

# Install needed packages.
RUN apt-get install -y \
    git \
    mongodb-clients \
    postgresql-client \
    nodejs \
 && rm -rf /var/lib/apt/lists/*

# Update pip/setuptools
RUN pip install --no-cache-dir -U pip setuptools

# Copy the source.
COPY demokratikollen/requirements /tmp/

# Install python deps
RUN pip install --no-cache-dir -r /tmp/dev.txt

WORKDIR /src
# Install nodejs tools.
RUN npm install -g gulp bower

ENV PYTHONPATH=/src

EXPOSE 8000
