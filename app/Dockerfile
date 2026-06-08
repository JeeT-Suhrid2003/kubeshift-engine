FROM python:3-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Expose port 8080 (Safe for non-root users)
EXPOSE 8080

# Grant group permissions to /app so OpenShift's dynamic random User IDs can read/write
RUN chown -R 1001:0 /app && chmod -R g+w /app

USER 1001

CMD ["python", "app.py"]
