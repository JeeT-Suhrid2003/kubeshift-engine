from flask import Flask
import redis
import os

app = Flask(__name__)

# Network configurations fetched from K8s environment variables
redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", 6379))

try:
    cache = redis.Redis(host=redis_host, port=redis_port, socket_timeout=2)
except Exception as e:
    cache = None

@app.route('/')
def hello():
    if cache:
        try:
            hits = cache.incr('hits')
            return f"<h1>KubeShift Engine Demo</h1><p>I've been viewed {hits} times!</p>"
        except redis.exceptions.ConnectionError:
            return "<h1>KubeShift Engine Demo</h1><p>Connected to Redis, but timed out.</p>"
    return "<h1>KubeShift Engine Demo</h1><p>Running in standalone mode (No Redis database detected).</p>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
