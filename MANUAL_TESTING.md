# Manual Testing Guide - Testing with Real LM Arena

This guide explains how to manually test the server with **actual LM Arena model responses**.

## Prerequisites

- ✅ Server code (this repository)
- ✅ Modern browser (Chrome, Edge, or Firefox recommended)
- ✅ Access to https://lmarena.ai
- ✅ Python 3.8+

## Step-by-Step Testing Guide

### Step 1: Install Dependencies

```bash
cd LMArena-Api
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
python3 server/proxy_server.py
```

You should see:
```
🚀 LMArena Reverse Proxy Server
📍 Local access: http://localhost:9080
📍 LAN access: http://192.168.x.x:9080
```

Keep this terminal window open.

### Step 3: Install Browser Userscript

#### Option A: Using Tampermonkey (Recommended)

1. Install Tampermonkey extension:
   - Chrome/Edge: https://chrome.google.com/webstore/detail/tampermonkey
   - Firefox: https://addons.mozilla.org/firefox/addon/tampermonkey/

2. Click Tampermonkey icon → Create new script

3. Copy contents from `Userscript/script.js` and paste into editor

4. Save (Ctrl+S or Cmd+S)

#### Option B: Manual Extension Installation

See browser extension documentation in the `browser/` directory.

### Step 4: Open LM Arena Website

1. Navigate to https://lmarena.ai in your browser

2. The userscript should automatically connect to your local server

3. Check server terminal - you should see:
   ```
   ✅ Browser WebSocket connected
   ```

### Step 5: Test with API Client

Now you can send actual queries! Open a new terminal:

#### Test 1: Simple Query (Python)

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:9080/v1",
    api_key="sk-any-string-you-like"
)

# Test with Claude
response = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": "Say hello and tell me what model you are!"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()
```

#### Test 2: Using curl

```bash
curl http://localhost:9080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4.1-2025-04-14",
    "messages": [{"role": "user", "content": "Count from 1 to 5"}],
    "stream": false
  }'
```

#### Test 3: Multiple Models

Try different models from the list:

```bash
# List available models
curl http://localhost:9080/v1/models | jq '.data[].id' | head -20

# Test different models
python -c "
from openai import OpenAI
client = OpenAI(base_url='http://localhost:9080/v1', api_key='sk-test')

models = ['claude-3-5-sonnet-20241022', 'gpt-4.1-2025-04-14', 'gemini-2.5-pro']
for model in models:
    print(f'\n=== Testing {model} ===')
    response = client.chat.completions.create(
        model=model,
        messages=[{'role': 'user', 'content': 'Say hi in 5 words'}],
        stream=False
    )
    print(response.choices[0].message.content)
"
```

#### Test 4: Image Generation

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:9080/v1",
    api_key="sk-test"
)

# Test DALL-E 3
response = client.chat.completions.create(
    model="dall-e-3",
    messages=[{"role": "user", "content": "A serene mountain landscape at sunset"}],
    stream=False
)

print(response.choices[0].message.content)  # Should contain image URL
```

### Step 6: Monitor Activity

While testing, monitor the server:

1. **Server Logs** - Check the terminal where server is running
2. **Monitor Dashboard** - Open http://localhost:9080/monitor in browser
3. **Metrics** - Check http://localhost:9080/metrics for Prometheus metrics

### Expected Results

✅ **If Everything Works:**
- Server shows "Browser WebSocket connected"
- API requests return actual model responses
- Monitor dashboard shows request activity
- Different models respond with their characteristic styles

❌ **Common Issues:**

1. **503 Service Unavailable - "Browser client not connected"**
   - Solution: Make sure browser has LM Arena page open with userscript active

2. **Request Timeout**
   - Solution: LM Arena might be slow or require login. Check browser console.

3. **Model Not Found**
   - Solution: Use `curl http://localhost:9080/v1/models` to see available models

4. **WebSocket Connection Failed**
   - Solution: Check userscript is installed and enabled
   - Check browser console for errors
   - Verify server is running on port 9080

### Verification Checklist

- [ ] Server starts without errors
- [ ] Browser connects (see "✅ Browser WebSocket connected" in logs)
- [ ] Chat completion returns actual response (not error)
- [ ] Different models return different responses
- [ ] Streaming works (responses arrive in chunks)
- [ ] Monitor dashboard shows request statistics
- [ ] Server handles multiple concurrent requests

### Performance Testing

Test with multiple concurrent requests:

```bash
# Install openai if needed
pip install openai

# Run concurrent test
python3 -c "
import concurrent.futures
from openai import OpenAI

def test_request(i):
    client = OpenAI(base_url='http://localhost:9080/v1', api_key='sk-test')
    response = client.chat.completions.create(
        model='claude-3-5-sonnet-20241022',
        messages=[{'role': 'user', 'content': f'Request {i}: Count to 3'}],
        stream=False
    )
    return f'Request {i}: {response.choices[0].message.content[:50]}'

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(test_request, i) for i in range(5)]
    for future in concurrent.futures.as_completed(futures):
        print(future.result())
"
```

### Debugging

Enable detailed logging:

```python
# In server/proxy_server.py, change logging level
logging.basicConfig(
    level=logging.DEBUG,  # Changed from INFO
    ...
)
```

Check logs in `logs/` directory:
- `server.log` - Server activity
- `requests.jsonl` - All requests
- `errors.jsonl` - Error details

## Success Criteria

Your manual testing is successful if:

1. ✅ Server accepts API requests
2. ✅ Browser WebSocket connects successfully
3. ✅ Actual model responses are received (not just errors)
4. ✅ Multiple models work (Claude, GPT, Gemini, etc.)
5. ✅ Streaming responses work
6. ✅ Monitor dashboard shows activity

## Troubleshooting Tips

**Browser not connecting?**
- Open browser console (F12) and check for JavaScript errors
- Verify userscript is enabled in Tampermonkey
- Try refreshing the LM Arena page

**Models not responding?**
- Some models may require LM Arena account/credits
- Try different models from the list
- Check if LM Arena website itself is working

**Server crashes?**
- Check Python version (3.8+ required)
- Verify all dependencies installed
- Check logs/server.log for details

## Next Steps

Once manual testing confirms everything works:
- Deploy server to a dedicated machine
- Configure firewall for network access
- Set up monitoring/alerting
- Document model selection for your use case

## Automated vs Manual Testing

| Aspect | Automated Tests | Manual Testing |
|--------|----------------|----------------|
| Server API | ✅ Tested | ✅ Verified |
| Model responses | ❌ Not possible | ✅ Required |
| Browser integration | ❌ Not possible | ✅ Required |
| Performance | ⚠️ Limited | ✅ Full |
| CI/CD | ✅ Suitable | ❌ Not suitable |

Both are necessary for complete validation!
