FROM python:3.11-slim

ENV APP_HOME /app
WORKDIR $APP_HOME

# Removes output stream buffering, allowing for more efficient logging
ENV PYTHONUNBUFFERED 1

# Install dependencies
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache \
    pip install -r requirements.txt

# Copy local code to the container image.
COPY . .
CMD ["gunicorn", "--bind", ":8000", "--workers", "3", "fokusin_api.wsgi"]