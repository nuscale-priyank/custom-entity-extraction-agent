# Custom Entity Extraction Agent - Endpoint Usage Guide

## 🎯 Overview

This guide provides clear instructions on which payloads to use for each API endpoint in the Custom Entity Extraction Agent.

## 📋 Available Endpoints

### 1. **GET /health** - Health Check
- **Payload**: None required
- **Returns**: API health status
- **Example**: `curl -X GET "http://localhost:8000/health"`

### 2. **GET /context-providers** - Get Available Context Providers
- **Payload**: None required
- **Returns**: List of supported context providers
- **Example**: `curl -X GET "http://localhost:8000/context-providers"`

### 3. **POST /extract-entities** - Main Generic Endpoint
- **Supports**: Both BC3 and generic data via `context_provider` field
- **Flexibility**: Most versatile endpoint

### 4. **POST /extract-entities/bc3** - BC3-Specific Endpoint
- **Supports**: Only BC3 data
- **Auto-sets**: `context_provider` to "bc3"

### 5. **POST /extract-entities/generic** - Generic-Specific Endpoint
- **Supports**: Only generic JSON data
- **Auto-sets**: `context_provider` to "generic"

## 🎯 Payload Selection Matrix

| Your Data Type | Recommended Endpoint | Use This Payload | Notes |
|----------------|---------------------|------------------|-------|
| **BC3 Data** | `/extract-entities` | `SAMPLE_GENERIC_ENDPOINT_REQUEST` | Set `context_provider: "bc3"` |
| **BC3 Data** | `/extract-entities/bc3` | `SAMPLE_BC3_ENDPOINT_REQUEST` | `context_provider` auto-set |
| **Generic JSON** | `/extract-entities` | `SAMPLE_GENERIC_ENDPOINT_REQUEST_2` | Set `context_provider: "generic"` |
| **Generic JSON** | `/extract-entities/generic` | `SAMPLE_GENERIC_SPECIFIC_REQUEST` | `context_provider` auto-set |
| **Mixed/Unknown** | `/extract-entities` | `SAMPLE_GENERIC_ENDPOINT_REQUEST` | Most flexible option |

## 📝 Detailed Payload Guide

### For BC3 Data

#### Option 1: Main Generic Endpoint
```json
{
  "message": "Extract all entities from this BC3 Account History segment",
  "data": {
    "segment_name": "Account History",
    "data_dictionary": [...]
  },
  "context_provider": "bc3",
  "chat_history": [],
  "session_id": "session_12345",
  "tools_enabled": true,
  "metadata": {
    "source": "firestore",
    "collection": "bc3_segments"
  }
}
```

#### Option 2: BC3-Specific Endpoint
```json
{
  "message": "Extract all entities from this BC3 Account History segment",
  "data": {
    "segment_name": "Account History",
    "data_dictionary": [...]
  },
  "chat_history": [],
  "session_id": "session_12345",
  "tools_enabled": true,
  "metadata": {
    "source": "firestore",
    "collection": "bc3_segments"
  }
}
```

### For Generic JSON Data

#### Option 1: Main Generic Endpoint
```json
{
  "message": "Analyze this user profile data and extract entities",
  "data": {
    "user_profile": {...},
    "metadata": {...}
  },
  "context_provider": "generic",
  "chat_history": [...],
  "session_id": "session_67890",
  "tools_enabled": true,
  "metadata": {
    "source": "api",
    "user_id": "user_12345"
  }
}
```

#### Option 2: Generic-Specific Endpoint
```json
{
  "message": "Analyze this user profile data and extract entities",
  "data": {
    "user_profile": {...},
    "metadata": {...}
  },
  "chat_history": [...],
  "session_id": "session_67890",
  "tools_enabled": true,
  "metadata": {
    "source": "api",
    "user_id": "user_12345"
  }
}
```

## 🧪 Testing

### Quick Test Commands

```bash
# 1. Health Check
curl -X GET "http://localhost:8000/health"

# 2. Context Providers
curl -X GET "http://localhost:8000/context-providers"

# 3. Main Generic Endpoint (BC3 Data)
curl -X POST "http://localhost:8000/extract-entities" \
  -H "Content-Type: application/json" \
  -d @bc3_request.json

# 4. BC3-Specific Endpoint
curl -X POST "http://localhost:8000/extract-entities/bc3" \
  -H "Content-Type: application/json" \
  -d @bc3_request.json

# 5. Generic-Specific Endpoint
curl -X POST "http://localhost:8000/extract-entities/generic" \
  -H "Content-Type: application/json" \
  -d @generic_request.json
```

### Run Comprehensive Tests

```bash
# Test all endpoints with sample payloads
python test_endpoints.py
```

## 📊 Expected Results

### BC3 Data Extraction
- **Entities**: ~7-11 business entities
- **Types**: Segment, fields, values, metadata
- **Confidence**: 0.85-0.95
- **Processing Time**: 4-6 seconds

### Generic Data Extraction
- **Entities**: ~1-5 business entities
- **Types**: Fields, objects, arrays
- **Confidence**: 0.75-0.85
- **Processing Time**: 4-6 seconds

## 🔧 Available Payloads in `sample_payloads.py`

| Payload Name | Use For | Endpoint | Data Type |
|--------------|---------|----------|-----------|
| `SAMPLE_GENERIC_ENDPOINT_REQUEST` | Main endpoint | `/extract-entities` | BC3 data |
| `SAMPLE_GENERIC_ENDPOINT_REQUEST_2` | Main endpoint | `/extract-entities` | Generic data |
| `SAMPLE_BC3_ENDPOINT_REQUEST` | BC3 endpoint | `/extract-entities/bc3` | BC3 data |
| `SAMPLE_GENERIC_SPECIFIC_REQUEST` | Generic endpoint | `/extract-entities/generic` | Generic data |
| `SAMPLE_BC3_REQUEST` | Legacy alias | `/extract-entities/bc3` | BC3 data |
| `SAMPLE_GENERIC_REQUEST` | Legacy alias | `/extract-entities/generic` | Generic data |

## 🚀 Best Practices

1. **For BC3 Data**: Use `/extract-entities/bc3` for simplicity, or `/extract-entities` with `context_provider: "bc3"` for flexibility
2. **For Generic Data**: Use `/extract-entities/generic` for simplicity, or `/extract-entities` with `context_provider: "generic"` for flexibility
3. **For Mixed Use**: Use `/extract-entities` with appropriate `context_provider` value
4. **Always Include**: `message`, `data`, and `session_id` fields
5. **Optional**: `chat_history`, `tools_enabled`, and `metadata` for enhanced functionality

## 📞 Support

- **API Documentation**: http://localhost:8000/docs
- **Sample Payloads**: `sample_payloads.py`
- **Test Script**: `test_endpoints.py`
- **Health Check**: `GET /health`

---

**Note**: All endpoints return HTTP 200 for success and HTTP 500 for errors. The response includes extracted entities, confidence scores, processing time, and detailed analysis.
