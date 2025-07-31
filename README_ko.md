# AI 모델 Tool Call 프록시 서버

**🌍 [English README](README.md)**

다양한 Tool Call 형식을 가진 AI 모델들을 OpenAI 표준 형식으로 자동 변환하여 원활한 통합을 가능하게 하는 Flask 기반 프록시 서버입니다. GLM과 같은 모델을 OpenAI 호환 클라이언트와 함께 사용하기에 완벽합니다.

## ✨ 주요 기능

- **🔄 자동 Tool Call 변환**: 모델별 Tool Call 형식(GLM의 `<tool_call>` 구문 등)을 OpenAI 표준 형식으로 자동 변환
- **⚡ 스트리밍 지원**: 스트리밍 및 비스트리밍 응답 모두 완벽 지원
- **🎯 모델별 처리**: 다양한 모델 형식을 자동으로 감지하고 처리하는 모듈형 변환기 시스템
- **🌐 완전한 OpenAI API 호환성**: 모든 주요 엔드포인트 지원 (`/v1/chat/completions`, `/v1/completions`, `/v1/models`, `/v1/embeddings`)
- **🔧 설정 가능**: 환경 기반 설정으로 쉬운 배포
- **🧩 확장 가능**: 새로운 모델 형식 지원 추가가 간편

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.7+
- 실행 중인 AI 모델 서버 (LM Studio, Ollama 등)

### 설치

1. **클론 및 설정**:
   ```bash
   git clone <저장소-URL>
   cd proxy
   pip install -r requirements.txt
   ```

2. **백엔드 설정** (선택사항):
   ```bash
   # 환경 변수 설정 또는 config.py 수정
   export BACKEND_HOST=localhost
   export BACKEND_PORT=8888
   ```

3. **프록시 시작**:
   ```bash
   python app.py
   ```

4. **OpenAI 호환 클라이언트와 함께 사용**:
   ```python
   from openai import OpenAI
   
   client = OpenAI(base_url="http://localhost:5000", api_key="your-key")
   
   response = client.chat.completions.create(
       model="glm-4.5-air-hi-mlx",
       messages=[{"role": "user", "content": "파이썬에 대한 정보를 검색해주세요"}],
       tools=[{
           "type": "function",
           "function": {
               "name": "search_wikipedia",
               "description": "위키피디아 검색",
               "parameters": {
                   "type": "object",
                   "properties": {"query": {"type": "string"}},
                   "required": ["query"]
               }
           }
       }]
   )
   ```

## 🎯 지원 모델

### 현재 지원되는 모델

| 모델 유형 | Tool Call 형식 | 상태 |
|-----------|----------------|------|
| **GLM 모델** | `<tool_call>` 구문 | ✅ 완전 지원 |
| **OpenAI 모델** | 표준 형식 | ✅ 패스스루 |
| **Claude 모델** | `<invoke>` 구문 | ✅ 예시 구현 |

### GLM 형식 예시

**입력 (GLM 형식):**
```
해당 정보를 검색해드리겠습니다.
<tool_call>fetch_wikipedia_content
<arg_key>search_query</arg_key>
<arg_value>Python 프로그래밍</arg_value>
</tool_call>
```

**출력 (OpenAI 형식):**
```json
{
  "tool_calls": [{
    "id": "123456789",
    "type": "function",
    "function": {
      "name": "fetch_wikipedia_content",
      "arguments": "{\"search_query\": \"Python 프로그래밍\"}"
    }
  }],
  "finish_reason": "tool_calls"
}
```

## 🔧 설정

### 환경 변수

| 변수 | 기본값 | 설명 |
|------|--------|------|
| `BACKEND_HOST` | `localhost` | 백엔드 서버 호스트명 |
| `BACKEND_PORT` | `8888` | 백엔드 서버 포트 |
| `BACKEND_PROTOCOL` | `http` | 백엔드 프로토콜 |
| `PROXY_HOST` | `0.0.0.0` | 프록시 서버 바인드 주소 |
| `PROXY_PORT` | `5000` | 프록시 서버 포트 |
| `REQUEST_TIMEOUT` | `300` | 요청 타임아웃 (초) |
| `ENABLE_TOOL_CALL_CONVERSION` | `true` | Tool Call 변환 활성화/비활성화 |
| `LOG_LEVEL` | `INFO` | 로깅 레벨 |
| `FLASK_ENV` | `development` | 환경 (development/production/testing) |

### 설정 파일

`.env` 파일을 만들거나 `config.py`를 직접 수정:

```python
# config.py
BACKEND_HOST = 'localhost'
BACKEND_PORT = 8888
PROXY_PORT = 5000
ENABLE_TOOL_CALL_CONVERSION = True
```

### 사전 정의된 백엔드 설정

```python
from config import get_backend_config

# LM Studio와 함께 사용
lmstudio_config = get_backend_config('lmstudio')  # localhost:8888

# Ollama와 함께 사용
ollama_config = get_backend_config('ollama')      # localhost:11434

# OpenAI API와 함께 사용
openai_config = get_backend_config('openai')     # api.openai.com:443
```

## 🏗️ 아키텍처

### 모듈형 변환기 시스템

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   클라이언트    │───▶│  프록시 서버     │───▶│  백엔드 모델    │
│  (OpenAI API)   │    │                  │    │   (GLM 등)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │ 변환기 팩토리    │
                       │  - GLM 변환기    │
                       │  - OpenAI 변환기 │
                       │  - Claude 변환기 │
                       │  - 사용자 변환기 │
                       └──────────────────┘
```

### 새로운 모델 지원 추가

1. **변환기 생성**:
   ```python
   # converters/mymodel.py
   from .base import ToolCallConverter
   
   class MyModelConverter(ToolCallConverter):
       def can_handle_model(self, model_name: str) -> bool:
           return 'mymodel' in model_name.lower()
       
       def parse_tool_calls(self, content: str) -> List[Dict]:
           # 파싱 로직 구현
           pass
   ```

2. **변환기 등록**:
   ```python
   # factory.py 또는 런타임에서
   from converters.factory import converter_factory
   converter_factory.register_converter(MyModelConverter())
   ```

## 📡 API 엔드포인트

### 채팅 완성
- `POST /v1/chat/completions` - Tool Call 변환이 포함된 채팅 완성
- `POST /chat/completions` - 대체 엔드포인트

### 기타 OpenAI 호환 엔드포인트
- `GET /v1/models` - 사용 가능한 모델 목록
- `POST /v1/completions` - 텍스트 완성
- `POST /v1/embeddings` - 텍스트 임베딩
- `GET /health` - 상태 확인

### 요청 예시

```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "glm-4.5-air-hi-mlx",
    "messages": [
      {"role": "user", "content": "파이썬 튜토리얼을 검색해주세요"}
    ],
    "tools": [
      {
        "type": "function",
        "function": {
          "name": "web_search",
          "description": "웹 검색",
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

## 🧪 테스트

### 모든 테스트 실행

```bash
# 모듈형 변환기 테스트
python test_modular_converters.py

# Tool Call 변환 테스트
python test_tool_call_real.py

# 스트리밍 기능 테스트
python test_streaming_tools.py

# 전체 API 호환성 테스트
python test_full_api.py
```

### 통합 테스트

```bash
# 백엔드 모델 서버 시작 (예: 포트 8888에서 LM Studio)
# 프록시 서버 시작
python app.py

# 예시 클라이언트로 테스트
python lmstudio-tooluse-test.py
```

## 🐛 문제 해결

### 일반적인 문제

1. **연결 거부됨**
   ```bash
   # 백엔드 서버가 실행 중인지 확인
   curl http://localhost:8888/v1/models
   
   # 프록시 서버 확인
   curl http://localhost:5000/health
   ```

2. **Tool Call이 변환되지 않음**
   ```bash
   # 변환이 활성화되어 있는지 확인
   export ENABLE_TOOL_CALL_CONVERSION=true
   
   # 모델 감지 확인
   # 모델명이 변환기 패턴과 일치하는지 확인
   ```

3. **Import 오류**
   ```bash
   # 올바른 디렉토리에 있는지 확인
   cd /path/to/proxy
   python app.py
   ```

### 디버그 모드

```bash
export FLASK_ENV=development
export LOG_LEVEL=DEBUG
python app.py
```

## 🤝 기여하기

1. **저장소 포크**
2. **기능 브랜치 생성**: `git checkout -b feature/amazing-feature`
3. **변경사항에 대한 테스트 추가**
4. **변경사항 커밋**: `git commit -m 'Add amazing feature'`
5. **브랜치에 푸시**: `git push origin feature/amazing-feature`
6. **Pull Request 열기**

### 모델 지원 추가

새로운 모델 형식에 대한 기여를 환영합니다! 다음을 준수해 주세요:

1. `converters/`에 변환기 생성
2. 포괄적인 테스트 추가
3. 문서 업데이트
4. 예시와 함께 PR 제출

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [LM Studio](https://lmstudio.ai/)와의 원활한 통합을 위해 제작
- [OpenAI Python SDK](https://github.com/openai/openai-python)와 호환
- 범용 AI 모델 호환성의 필요성에서 영감을 받음

## 📞 지원

- 🐛 **버그 리포트**: [이슈 열기](issues)
- 💡 **기능 요청**: [토론 시작](discussions)
- 📖 **문서**: [위키](wiki)
- 🌍 **영문 문서**: [README.md](README.md)

---

**AI 커뮤니티를 위해 ❤️로 제작**