# Custom Entity Extraction Agent

A sophisticated AI agent built with LangGraph and Vertex AI for extracting custom entities from various data structures, with special support for BC3 (Business Credit Bureau) data and generic JSON documents.

## 🚀 Features

- **Multi-Context Support**: Handles BC3 data, generic JSON documents, and custom data structures
- **Intelligent Entity Extraction**: Extracts fields, segments, values, metadata, objects, arrays, and documents
- **Chat History Management**: Maintains conversation context across requests
- **Confidence Scoring**: Provides confidence scores for each extracted entity
- **LangGraph Workflow**: Uses the latest LangGraph framework for robust agent workflows
- **Vertex AI Integration**: Leverages Google's Vertex AI for advanced language model capabilities
- **FastAPI REST API**: Clean, documented REST endpoints with automatic OpenAPI documentation
- **Data Quality Analysis**: Provides insights about data structure quality and completeness

## 📋 Requirements

- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd bc3_ai_agent
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # Optional, defaults to us-central1
```

4. **Authenticate with Google Cloud**:
```bash
gcloud auth application-default login
```

## 🏃‍♂️ Quick Start

### Running the API Server

```bash
python main.py
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Health Check

```bash
curl http://localhost:8000/health
```

### Example: Extract BC3 Entities

```bash
curl -X POST "http://localhost:8000/extract-entities/bc3" \
  -H "Content-Type: application/json" \
  -d @sample_payloads.py
```

## 📊 Supported Data Types

### 1. BC3 (Business Credit Bureau) Data
```json
{
  "segment_name": "Account History",
  "data_dictionary": [
    {
      "definition": "Field description",
      "bc3_field": "field_code",
      "description": "Human-readable name",
      "notes": "Additional context",
      "valid_values": ["value1", "value2"]
    }
  ]
}
```

### 2. Generic JSON Documents
```json
{
  "user_profile": {
    "id": "user_12345",
    "name": "John Doe",
    "preferences": {
      "theme": "dark",
      "notifications": true
    },
    "subscriptions": [
      {
        "plan": "premium",
        "features": ["api_access", "priority_support"]
      }
    ]
  }
}
```

## 🔧 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/extract-entities` | Generic entity extraction |
| `POST` | `/extract-entities/bc3` | BC3-specific extraction |
| `POST` | `/extract-entities/generic` | Generic JSON extraction |
| `GET` | `/context-providers` | List supported providers |

### Request Format

```json
{
  "message": "Your analysis request",
  "data": {
    // Your data structure
  },
  "context_provider": "bc3|generic|custom",
  "chat_history": [],
  "session_id": "optional_session_id",
  "tools_enabled": true,
  "metadata": {}
}
```

### Response Format

```json
{
  "response": "AI-generated analysis",
  "extracted_entities": [
    {
      "entity_type": "field|segment|value|metadata|object|array|document",
      "entity_name": "entity_identifier",
      "entity_value": "extracted_value",
      "confidence": 0.95,
      "source_field": "field_path",
      "description": "Entity description",
      "context_provider": "bc3|generic|custom"
    }
  ],
  "chat_history": [],
  "session_id": "session_id",
  "confidence_score": 0.92,
  "processing_time": 2.34,
  "metadata": {}
}
```

## 🏗️ Architecture

### Agent Components

1. **CustomEntityExtractionAgent**: Main agent class with LangGraph workflow
2. **Entity Extraction Tools**: Specialized tools for different data types
3. **LangGraph Workflow**: Three-node pipeline:
   - `extract_entities`: Extract entities from data
   - `analyze_structure`: Analyze data structure and quality
   - `generate_response`: Generate AI response with insights

### Data Models

- **BC3Segment**: BC3-specific data structure
- **GenericDocument**: Generic document structure
- **ExtractedEntity**: Extracted entity representation
- **AgentRequest/Response**: API request/response models

## 🔍 Entity Types

| Type | Description | Example |
|------|-------------|---------|
| `FIELD` | Individual data fields | `hist_eff_dte`, `user_id` |
| `SEGMENT` | Business segments | `Account History` |
| `VALUE` | Important values | `"History based value"` |
| `METADATA` | Contextual information | Notes, timestamps |
| `OBJECT` | Complex nested objects | User preferences |
| `ARRAY` | List-based structures | Subscriptions array |
| `DOCUMENT` | Document-level info | Root document structure |

## 📈 Data Quality Analysis

The agent provides comprehensive data quality insights:

- **Data Quality Score**: Overall quality assessment (0-1)
- **Field Completeness**: Percentage of fields with definitions
- **Value Constraints**: Fields with valid value lists
- **Structure Complexity**: Complexity score of data structure
- **Type Distribution**: Distribution of data types

## 🧪 Testing

### Sample Data

Use the sample data in `sample_payloads.py`:

```python
from sample_payloads import SAMPLE_BC3_REQUEST, SAMPLE_GENERIC_REQUEST

# Test BC3 extraction
response = requests.post("http://localhost:8000/extract-entities/bc3", 
                        json=SAMPLE_BC3_REQUEST)

# Test generic extraction
response = requests.post("http://localhost:8000/extract-entities/generic", 
                        json=SAMPLE_GENERIC_REQUEST)
```

### Running Tests

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test context providers
curl http://localhost:8000/context-providers

# Test entity extraction (use sample data)
python -c "
import requests
from sample_payloads import SAMPLE_BC3_REQUEST
response = requests.post('http://localhost:8000/extract-entities/bc3', 
                        json=SAMPLE_BC3_REQUEST)
print(response.json())
"
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud Project ID | Required |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI location | `us-central1` |

### Agent Configuration

```python
from agent import CustomEntityExtractionAgent

agent = CustomEntityExtractionAgent(
    project_id="your-project-id",
    location="us-central1"
)
```

## 🚀 Deployment

### Local Development

```bash
python main.py
```

### Production Deployment

1. **Docker** (recommended):
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["python", "main.py"]
```

2. **Google Cloud Run**:
```bash
gcloud run deploy custom-entity-agent \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

3. **Kubernetes**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-entity-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: custom-entity-agent
  template:
    metadata:
      labels:
        app: custom-entity-agent
    spec:
      containers:
      - name: agent
        image: custom-entity-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: GOOGLE_CLOUD_PROJECT
          value: "your-project-id"
```

## 📚 Documentation

- **API Documentation**: Available at `/docs` (Swagger UI) and `/redoc`
- **Sample Payloads**: See `sample_payloads.py` for complete examples
- **Code Documentation**: Inline documentation in all Python files

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the sample payloads in `sample_payloads.py`
- Open an issue in the repository

## 🔄 Changelog

### v1.0.0
- Initial release with BC3 and generic entity extraction
- LangGraph workflow implementation
- FastAPI REST API
- Comprehensive documentation and samples
