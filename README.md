# AI Model Tool Call Proxy Server

**🌍 [한국어 README](README_ko.md)**

A Flask-based proxy server that enables seamless integration of AI models with different tool call formats by automatically converting them to OpenAI's standard format. Perfect for using models like GLM with OpenAI-compatible clients.

## ✨ Features

- **🔄 Automatic Tool Call Conversion**: Converts model-specific tool call formats (like GLM's `<tool_call>` syntax) to OpenAI's standard format
- **⚡ Streaming Support**: Full support for both streaming and non-streaming responses
- **🎯 Model-Specific Handling**: Modular converter system that automatically detects and handles different model formats
- **🌐 Full OpenAI API Compatibility**: Supports all major endpoints (`/v1/chat/completions`, `/v1/completions`, `/v1/models`, `/v1/embeddings`)
- **🔧 Configurable**: Environment-based configuration for easy deployment
- **🧩 Extensible**: Easy to add support for new model formats

## 🚀 Quick Start

### Prerequisites

- Python 3.7+
- A running AI model server (LM Studio, Ollama, etc.)

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd proxy
   pip install -r requirements.txt
   ```

2. **Configure your backend** (optional):
   ```bash
   # Set environment variables or modify config.py
   export BACKEND_HOST=localhost
   export BACKEND_PORT=8888
   ```

3. **Start the proxy**:
   ```bash
   python app.py
   ```

4. **Use with any OpenAI-compatible client**:
   ```python
   from openai import OpenAI
   
   client = OpenAI(base_url="http://localhost:5000", api_key="your-key")
   
   response = client.chat.completions.create(
       model="glm-4.5-air-hi-mlx",
       messages=[{"role": "user", "content": "Search for information about Python"}],
       tools=[{
           "type": "function",
           "function": {
               "name": "search_wikipedia",
               "description": "Search Wikipedia",
               "parameters": {
                   "type": "object",
                   "properties": {"query": {"type": "string"}},
                   "required": ["query"]
               }
           }
       }]
   )
   ```

## 🎯 Supported Models

### Currently Supported

| Model Type | Tool Call Format | Status |
|------------|------------------|---------|
| **GLM Models** | `<tool_call>` syntax | ✅ Full Support |
| **OpenAI Models** | Standard format | ✅ Pass-through |
| **Claude Models** | `<invoke>` syntax | ✅ Example Implementation |

### GLM Format Example

**Input (GLM format):**
```
I'll search for that information.
<tool_call>fetch_wikipedia_content
<arg_key>search_query</arg_key>
<arg_value>Python programming</arg_value>
</tool_call>
```

**Output (OpenAI format):**
```json
{
  "tool_calls": [{
    "id": "123456789",
    "type": "function",
    "function": {
      "name": "fetch_wikipedia_content",
      "arguments": "{\"search_query\": \"Python programming\"}"
    }
  }],
  "finish_reason": "tool_calls"
}
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BACKEND_HOST` | `localhost` | Backend server hostname |
| `BACKEND_PORT` | `8888` | Backend server port |
| `BACKEND_PROTOCOL` | `http` | Backend protocol |
| `PROXY_HOST` | `0.0.0.0` | Proxy server bind address |
| `PROXY_PORT` | `5000` | Proxy server port |
| `REQUEST_TIMEOUT` | `3600` | Regular request timeout (seconds) |
| `STREAMING_TIMEOUT` | `3600` | Streaming request timeout (seconds, use 'none' to disable) |
| `ENABLE_TOOL_CALL_CONVERSION` | `true` | Enable/disable tool call conversion |
| `REMOVE_THINK_TAGS` | `true` | Remove complete `<think>...</think>` blocks from responses |
| `LOG_LEVEL` | `INFO` | Logging level |
| `FLASK_ENV` | `development` | Environment (development/production/testing) |

### Configuration File

Create a `.env` file or modify `config.py` directly:

```python
# config.py
BACKEND_HOST = 'localhost'
BACKEND_PORT = 8888
PROXY_PORT = 5000
ENABLE_TOOL_CALL_CONVERSION = True
REMOVE_THINK_TAGS = True  # Set to False to preserve <think> content
```

### Predefined Backend Configurations

```python
from config import get_backend_config

# Use with LM Studio
lmstudio_config = get_backend_config('lmstudio')  # localhost:8888

# Use with Ollama
ollama_config = get_backend_config('ollama')      # localhost:11434

# Use with OpenAI API
openai_config = get_backend_config('openai')     # api.openai.com:443
```

## 🏗️ Architecture

### Modular Converter System

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client        │───▶│  Proxy Server    │───▶│  Backend Model  │
│  (OpenAI API)   │    │                  │    │   (GLM/etc.)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ Converter Factory │
                       │  - GLM Converter  │
                       │  - OpenAI Converter│
                       │  - Claude Converter│
                       │  - Custom Converter│
                       └──────────────────┘
```

### Adding New Model Support

1. **Create a converter**:
   ```python
   # converters/mymodel.py
   from .base import ToolCallConverter
   
   class MyModelConverter(ToolCallConverter):
       def can_handle_model(self, model_name: str) -> bool:
           return 'mymodel' in model_name.lower()
       
       def parse_tool_calls(self, content: str) -> List[Dict]:
           # Your parsing logic here
           pass
   ```

2. **Register the converter**:
   ```python
   # In factory.py or at runtime
   from converters.factory import converter_factory
   converter_factory.register_converter(MyModelConverter())
   ```

## 📡 API Endpoints

### Chat Completions
- `POST /v1/chat/completions` - Chat completions with tool call conversion
- `POST /chat/completions` - Alternative endpoint

### Other OpenAI Compatible Endpoints
- `GET /v1/models` - List available models
- `POST /v1/completions` - Text completions
- `POST /v1/embeddings` - Text embeddings
- `GET /health` - Health check

### Request Example

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.5-air-hi-mlx",
    "messages": [
      {"role": "user", "content": "Search for Python tutorials"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "web_search",
          "description": "Search the web",
          "parameters": {
            "type": "object",
            "properties": {
              "query": {"type": "string"}
            },
            "required": ["query"]
          }
        }
      }
    ],
    "stream": false
  }'
```

## 🧪 Testing

### Run All Tests

```bash
# Test modular converters
python test_modular_converters.py

# Test tool call conversion
python test_tool_call_real.py

# Test streaming functionality
python test_streaming_tools.py

# Test full API compatibility
python test_full_api.py
```

### Integration Testing

```bash
# Start your backend model server (e.g., LM Studio on port 8888)
# Start the proxy server
python app.py

# Test with the example client
python lmstudio-tooluse-test.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if backend server is running
   curl http://localhost:8888/v1/models
   
   # Check proxy server
   curl http://localhost:5000/health
   ```

2. **Tool Calls Not Converting**
   ```bash
   # Check if conversion is enabled
   export ENABLE_TOOL_CALL_CONVERSION=true
   
   # Check model detection
   # Make sure your model name matches the converter patterns
   ```

3. **Import Errors**
   ```bash
   # Make sure you're in the correct directory
   cd /path/to/proxy
   python app.py
   ```

### Debug Mode

```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
python app.py
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Add tests** for your changes
4. **Commit your changes**: `git commit -m 'Add amazing feature'`
5. **Push to the branch**: `git push origin feature/amazing-feature`
6. **Open a Pull Request**

### Adding Model Support

We welcome contributions for new model formats! Please:

1. Create a converter in `converters/`
2. Add comprehensive tests
3. Update documentation
4. Submit a PR with examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🧠 Think Tag Processing

The proxy server can handle GLM model `<think>` tags for better response formatting:

### Configuration
Set `REMOVE_THINK_TAGS` environment variable to control behavior:

- `REMOVE_THINK_TAGS=true` (default): Remove complete `<think>...</think>` blocks
- `REMOVE_THINK_TAGS=false`: Preserve `<think>` content for debugging/transparency

### Examples

**With REMOVE_THINK_TAGS=true (default):**
```
Input:  "I need to analyze this. <think>Let me think step by step...</think> Here's my answer."
Output: "I need to analyze this.  Here's my answer."
```

**With REMOVE_THINK_TAGS=false:**
```
Input:  "I need to analyze this. <think>Let me think step by step...</think> Here's my answer."
Output: "I need to analyze this. Let me think step by step... Here's my answer."
```

**Note:** Malformed/orphaned think tags are always cleaned up regardless of the setting:
- `</think>` without opening tag → removed
- `<think>` without closing tag → removed

## ⏱️ Timeout Configuration

The proxy server supports different timeout settings for regular and streaming requests:

### Environment Variables

- `REQUEST_TIMEOUT=3600`: Regular request timeout (60 minutes)
- `STREAMING_TIMEOUT=3600`: Streaming request timeout (60 minutes)

### Disable Streaming Timeout

For long-running streaming requests, you can disable the timeout:

```bash
export STREAMING_TIMEOUT=none
# or
export STREAMING_TIMEOUT=0
# or 
export STREAMING_TIMEOUT=false
```

### Usage Examples

**Short timeout for quick responses:**
```bash
export REQUEST_TIMEOUT=30
export STREAMING_TIMEOUT=120
```

**No timeout for long streaming sessions:**
```bash
export REQUEST_TIMEOUT=3600
export STREAMING_TIMEOUT=none
```

**Note:** Disabling streaming timeout is useful for:
- Long document generation
- Complex reasoning tasks
- Large dataset processing
- Extended conversations

## 🙏 Acknowledgments

- Built for seamless integration with [LM Studio](https://lmstudio.ai/)
- Compatible with [OpenAI Python SDK](https://github.com/openai/openai-python)
- Inspired by the need for universal AI model compatibility

## 📞 Support

- 🐛 **Bug Reports**: [Open an issue](issues)
- 💡 **Feature Requests**: [Start a discussion](discussions)
- 📖 **Documentation**: [Wiki](wiki)
- 🌍 **Korean Documentation**: [README_ko.md](README_ko.md)

---

**Made with ❤️ for the AI community**