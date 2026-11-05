FROM python:3.12-slim
WORKDIR /app
COPY ethicslab /app/ethicslab
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
USER 10001:10001
ENTRYPOINT ["python", "-m", "ethicslab"]
