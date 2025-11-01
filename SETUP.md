# LMArena API Setup Guide

## Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository** (or download from releases)
```bash
git clone https://github.com/computersrmyfriends/LMArena-Api.git
cd LMArena-Api
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the server**

**Option A: Run server directly (recommended for testing)**
```bash
python3 server/proxy_server.py
```

**Option B: Run with starter script (Windows with browser)**
```bash
python starter.py
```

The server will start on `http://localhost:9080`

### Verify Installation

Run the automated test suite:
```bash
python3 test_server.py
```

You should see:
```
✓ All tests passed! Server is working correctly.
```

## Usage

### Using with OpenAI Python Client

```python
from openai import OpenAI

# Configure client to use LMArena proxy
client = OpenAI(
    base_url="http://localhost:9080/v1",
    api_key="sk-any-string-you-like"  # API key can be any string
)

# List available models
models = client.models.list()
for model in models.data:
    print(f"- {model.id}")

# Chat with a model
response = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    messages=[
        {"role": "user", "content": "Hello! How are you?"}
    ],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### Using with curl

**List models:**
```bash
curl http://localhost:9080/v1/models
```

**Chat completion:**
```bash
curl http://localhost:9080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": true
  }'
```

**Health check:**
```bash
curl http://localhost:9080/health
```

## Available Endpoints

### AI API Endpoints
- `POST /v1/chat/completions` - OpenAI-compatible chat API
- `GET /v1/models` - List available models
- `POST /v1/refresh-models` - Refresh model list

### Monitoring Endpoints
- `GET /health` - Basic health check
- `GET /api/health/detailed` - Detailed health with scoring
- `GET /monitor` - Web-based monitoring dashboard
- `GET /metrics` - Prometheus metrics

### Statistics & Logs
- `GET /api/stats/summary` - 24-hour statistics summary
- `GET /api/logs/requests` - Request logs
- `GET /api/logs/errors` - Error logs
- `GET /api/alerts` - System alerts

### Configuration
- `GET /api/config` - Get current configuration
- `POST /api/config` - Update configuration
- `GET /api/system/info` - System information

## Monitoring Dashboard

Access the real-time monitoring dashboard at:
```
http://localhost:9080/monitor
```

Features:
- Real-time request monitoring
- Performance metrics (response times, QPS)
- Model usage statistics
- Error tracking
- System health scoring

## Network Access

### Local Network Access

The server automatically detects your local IP and makes the API available on your network:

```
Local: http://localhost:9080
Network: http://<your-local-ip>:9080
```

Access from other devices on the same WiFi network using the Network URL.

### Manual IP Configuration

If automatic IP detection doesn't work, you can set a manual IP:

Edit `server/proxy_server.py` and change:
```python
MANUAL_IP = None
```
to:
```python
MANUAL_IP = "192.168.1.100"  # Your desired IP
```

## Supported Models

The server comes with 89+ pre-configured models including:

**Chat Models:**
- Claude (3.5, 3.7, Opus 4)
- GPT (4.1, 5, O3, O4)
- Gemini (2.0, 2.5)
- Llama (3.3, 4)
- Grok (3, 4)
- DeepSeek
- Qwen
- And many more...

**Image Generation:**
- DALL-E 3
- Flux 1.1 Pro
- Midjourney alternatives
- Imagen
- And more...

**Video Generation:**
- Supported models (check `/v1/models` for list)

## Configuration

### Environment Variables

The server supports configuration via:
- Configuration file: `logs/config.json`
- Direct modification of `server/proxy_server.py`

Key settings:
- `PORT`: Server port (default: 9080)
- `HOST`: Bind address (default: 0.0.0.0)
- `MAX_CONCURRENT_REQUESTS`: Max concurrent requests (default: 20)
- `REQUEST_TIMEOUT_SECONDS`: Request timeout (default: 180)

## Troubleshooting

### Server won't start
- Check if port 9080 is already in use
- Verify all dependencies are installed: `pip install -r requirements.txt`

### Connection refused
- Ensure the server is running
- Check firewall settings
- Verify the correct IP/port is being used

### Models not available
- The server loads fallback models on startup
- Browser extension integration provides dynamic model updates
- Models work without browser connection for testing

### Performance issues
- Check active request count: `/api/stats/summary`
- Monitor system health: `/api/health/detailed`
- Review metrics: `/metrics`

## Development

### Running Tests
```bash
python3 test_server.py
```

### Viewing Logs
Logs are stored in the `logs/` directory:
- `server.log` - General server logs
- `requests.jsonl` - Request logs (JSON Lines format)
- `errors.jsonl` - Error logs

## Architecture

- **Framework**: FastAPI (async Python web framework)
- **WebSocket**: Real-time communication with browser extension
- **Monitoring**: Prometheus metrics + custom dashboard
- **Logging**: Structured JSON Lines format with rotation
- **Request Management**: Persistent request tracking with timeout handling

## Browser Extension (Optional)

For enhanced functionality, the browser extension provides:
- Automatic model detection from LMArena
- Direct WebSocket integration
- Real-time model updates

Without the extension, the server uses fallback models and still works for API requests.

## Contributing

This project is based on [lmarena-proxy](https://github.com/zhongruichen/lmarena-proxy) with English translation and improvements.

## Support

For issues and questions, please open an issue on GitHub.
