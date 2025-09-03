# Entity Extraction Agent API Documentation

## Overview
The Entity Extraction Agent is a specialized AI system that extracts and analyzes entities from Credit Domain (BC3) data and data assets. It can identify both obvious entities and create meaningful derived insights by fusing context from multiple sources.

## Base URL
```
http://localhost:8000
```

## Endpoints

### 1. Health Check
- **URL**: `/health`
- **Method**: `GET`
- **Description**: Check if the service is running
- **Response**: Simple health status

### 2. Entity Extraction Chat
- **URL**: `/chat`
- **Method**: `POST`
- **Description**: Extract entities from BC3 fields and data assets
- **Content-Type**: `application/json`

## Working Input Payload Examples

### Example 1: Basic Credit Risk Analysis
```json
{
  "message": "Please extract entities from the selected BC3 fields and asset columns to help me understand credit risk patterns.",
  "session_id": "test_session_001",
  "selected_bc3_fields": [
    {
      "field": {
        "uuid": "field_001",
        "known_implementations": ["account_number", "credit_account"],
        "valid_values": ["1234567890", "0987654321", "1122334455"],
        "definition": "Unique identifier for the credit account",
        "notes": "Masked for security in production",
        "description": "Account Number"
      },
      "segment_context": {
        "segment_name": "Credit Accounts"
      }
    },
    {
      "field": {
        "uuid": "field_002",
        "known_implementations": ["credit_limit", "max_credit"],
        "valid_values": ["5000", "10000", "25000", "50000"],
        "definition": "Maximum amount of credit available on the account",
        "notes": "Expressed in dollars without currency symbol",
        "description": "Credit Limit"
      },
      "segment_context": {
        "segment_name": "Credit Accounts"
      }
    }
  ],
  "selected_asset_columns": [
    {
      "column": {
        "column_name": "credit_score",
        "column": "credit_score"
      },
      "asset_context": {
        "asset_name": "Consumer Credit Database",
        "workspace_name": "Credit Analytics Workspace",
        "big_query_table_name": "credit_analytics.consumer_credit_data"
      }
    }
  ],
  "context_provider": "credit_domain",
  "tools_enabled": true
}
```

### Example 2: Comprehensive Risk Assessment
```json
{
  "message": "Extract all possible entities and relationships for comprehensive credit risk modeling.",
  "session_id": "test_session_002",
  "selected_bc3_fields": [
    {
      "field": {
        "uuid": "field_003",
        "known_implementations": ["account_number", "credit_account"],
        "valid_values": ["1234567890", "0987654321", "1122334455"],
        "definition": "Unique identifier for the credit account",
        "notes": "Masked for security in production",
        "description": "Account Number"
      },
      "segment_context": {
        "segment_name": "Credit Accounts"
      }
    },
    {
      "field": {
        "uuid": "field_004",
        "known_implementations": ["credit_limit", "max_credit"],
        "valid_values": ["5000", "10000", "25000", "50000"],
        "definition": "Maximum amount of credit available on the account",
        "notes": "Expressed in dollars without currency symbol",
        "description": "Credit Limit"
      },
      "segment_context": {
        "segment_name": "Credit Accounts"
      }
    },
    {
      "field": {
        "uuid": "field_005",
        "known_implementations": ["payment_history", "delinquency_status"],
        "valid_values": ["current", "30_days_late", "60_days_late", "90_days_late"],
        "definition": "Current payment status of the account",
        "notes": "Based on most recent payment activity",
        "description": "Payment Status"
      },
      "segment_context": {
        "segment_name": "Credit Accounts"
      }
    }
  ],
  "selected_asset_columns": [
    {
      "column": {
        "column_name": "credit_score",
        "column": "credit_score"
      },
      "asset_context": {
        "asset_name": "Consumer Credit Database",
        "workspace_name": "Credit Analytics Workspace",
        "big_query_table_name": "credit_analytics.consumer_credit_data"
      }
    },
    {
      "column": {
        "column_name": "total_debt",
        "column": "total_debt"
      },
      "asset_context": {
        "asset_name": "Consumer Credit Database",
        "workspace_name": "Credit Analytics Workspace",
        "big_query_table_name": "credit_analytics.consumer_credit_data"
      }
    },
    {
      "column": {
        "column_name": "income_level",
        "column": "income_level"
      },
      "asset_context": {
        "asset_name": "Consumer Credit Database",
        "workspace_name": "Credit Analytics Workspace",
        "big_query_table_name": "credit_analytics.consumer_income_data"
      }
    }
  ],
  "context_provider": "credit_domain",
  "tools_enabled": true
}
```

### Example 3: Minimal BC3 Fields Only
```json
{
  "message": "Extract entities from BC3 fields for credit account analysis.",
  "session_id": "test_session_003",
  "selected_bc3_fields": [
    {
      "field": {
        "uuid": "field_006",
        "known_implementations": ["account_number"],
        "valid_values": ["1234567890"],
        "definition": "Unique identifier for the credit account",
        "notes": "Primary key field",
        "description": "Account Number"
      },
      "segment_context": {
        "segment_name": "Credit Accounts"
      }
    }
  ],
  "selected_asset_columns": [],
  "context_provider": "credit_domain",
  "tools_enabled": true
}
```

### Example 4: Asset Columns Only
```json
{
  "message": "Analyze data assets for credit risk patterns.",
  "session_id": "test_session_004",
  "selected_bc3_fields": [],
  "selected_asset_columns": [
    {
      "column": {
        "column_name": "credit_score",
        "column": "credit_score"
      },
      "asset_context": {
        "asset_name": "Credit Risk Database",
        "workspace_name": "Risk Analytics",
        "big_query_table_name": "risk_analytics.credit_scores"
      }
    },
    {
      "column": {
        "column_name": "debt_to_income_ratio",
        "column": "debt_to_income_ratio"
      },
      "asset_context": {
        "asset_name": "Credit Risk Database",
        "workspace_name": "Risk Analytics",
        "big_query_table_name": "risk_analytics.credit_scores"
      }
    }
  ],
  "context_provider": "credit_domain",
  "tools_enabled": true
}
```

## Request Schema

### Required Fields
- `message` (string): Natural language instruction for entity extraction
- `session_id` (string): Unique identifier for the chat session
- `context_provider` (string): Must be "credit_domain"
- `tools_enabled` (boolean): Must be true for entity extraction

### Optional Fields
- `selected_bc3_fields` (array): Array of BC3 field objects
- `selected_asset_columns` (array): Array of data asset column objects

### BC3 Field Structure
```json
{
  "field": {
    "uuid": "string",
    "known_implementations": ["array of strings"],
    "valid_values": ["array of strings"],
    "definition": "string",
    "notes": "string",
    "description": "string"
  },
  "segment_context": {
    "segment_name": "string"
  }
}
```

### Asset Column Structure
```json
{
  "column": {
    "column_name": "string",
    "column": "string"
  },
  "asset_context": {
    "asset_name": "string",
    "workspace_name": "string",
    "big_query_table_name": "string"
  }
}
```

## Response Schema

### Success Response
```json
{
  "response": "string (LLM response in JSON format)",
  "extracted_entities": [
    {
      "entity_type": "string (FIELD|DERIVED_INSIGHT|RELATIONSHIP|BUSINESS_METRIC|OPERATIONAL_RULE)",
      "entity_name": "string",
      "entity_value": "string",
      "confidence": "number (0.0-1.0)",
      "source_field": "string",
      "description": "string",
      "relationships": "object",
      "context_provider": "string"
    }
  ],
  "chat_state": "object",
  "confidence_score": "number",
  "processing_time": "number",
  "metadata": "object"
}
```

### Entity Types
- **FIELD**: Direct entities from BC3 fields or asset columns
- **DERIVED_INSIGHT**: Calculated or inferred business metrics
- **RELATIONSHIP**: Connections between multiple entities
- **BUSINESS_METRIC**: Key performance indicators
- **OPERATIONAL_RULE**: Business rules and constraints

## Testing the API

### Using curl
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

### Using Python
```python
import requests
import json

url = "http://localhost:8000/chat"
headers = {"Content-Type": "application/json"}

with open("payload.json", "r") as f:
    payload = json.load(f)

response = requests.post(url, headers=headers, json=payload)
print(json.dumps(response.json(), indent=2))
```

## Error Handling

### Common HTTP Status Codes
- `200`: Success
- `400`: Bad Request (invalid payload)
- `422`: Validation Error (schema mismatch)
- `500`: Internal Server Error

### Error Response Format
```json
{
  "detail": "Error description"
}
```

## Best Practices

1. **Session Management**: Use unique session IDs for different conversations
2. **Field Selection**: Include relevant BC3 fields and asset columns for comprehensive analysis
3. **Message Clarity**: Be specific about what entities you want to extract
4. **Context Provider**: Always set to "credit_domain" for credit-related analysis
5. **Tools Enabled**: Keep true for entity extraction capabilities

## Performance Notes

- **Typical Response Time**: 3-5 seconds for complex entity extraction
- **Entity Limit**: No hard limit, but typically 3-10 entities per request
- **Memory**: Sessions are maintained in memory for context continuity
- **Scalability**: Designed for single-user sessions with hot-reload support
