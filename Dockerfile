FROM python:3.13-slim
LABEL org.opencontainers.image.vendor="JDB-NET"
WORKDIR /app
COPY . /app
ARG VERSION=unknown
ENV VERSION=${VERSION}
RUN pip install -r requirements.txt \
    && apt-get update \
    && apt-get install curl -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64 \
    && chmod +x tailwindcss-linux-x64 \
    && ./tailwindcss-linux-x64 -i ./static/input.css -o ./static/output.css --content "./templates/*.html" --minify \
    && rm tailwindcss-linux-x64
EXPOSE 5000
CMD ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "app:app", "--log-level", "warning"]