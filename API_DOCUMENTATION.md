# Entity Extraction Agent API Documentation

## Overview
The Entity Extraction Agent is a specialized AI system that extracts and analyzes entities from Credit Domain (BC3) data and data assets. It can identify both obvious entities and create meaningful derived insights by fusing context from multiple sources.

## Intent-Based Workflow
The agent now uses an intelligent intent detection system that automatically routes user requests to the appropriate operations:

1. **Intent Detection**: Analyzes user messages to determine the desired action
2. **Smart Routing**: Routes requests to appropriate workflow nodes based on intent
3. **Tool Integration**: Uses specialized tools for different operations
4. **Contextual Responses**: Provides responses tailored to the detected intent

### Supported Intents
- **Extract**: Extract entities from BC3 fields and data assets
- **Read**: Retrieve and display existing entities from a session
- **Update Entity**: Modify entity-level information
- **Update Attribute**: Modify specific attributes within entities
- **Delete Entity**: Remove entire entities
- **Delete Attribute**: Remove specific attributes from entities

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

### 3. Entity Management Endpoints

#### 3.1 Read Entities
- **URL**: `/entities/read`
- **Method**: `POST`
- **Description**: Read entities from a session with optional filtering
- **Content-Type**: `application/json`

#### 3.2 Update Entities
- **URL**: `/entities/update`
- **Method**: `POST`
- **Description**: Create or update entities and their attributes
- **Content-Type**: `application/json`

#### 3.3 Delete Entities
- **URL**: `/entities/delete`
- **Method**: `POST`
- **Description**: Delete entities or specific attributes
- **Content-Type**: `application/json`

## Intent-Based Usage Examples

### Extract Intent
```json
{
  "message": "Extract entities from the selected BC3 fields and asset columns to analyze credit risk patterns",
  "session_id": "session_123",
  "selected_bc3_fields": [...],
  "selected_asset_columns": [...],
  "context_provider": "credit_domain",
  "tools_enabled": true
}
```

### Read Intent
```json
{
  "message": "Show me all entities in this session",
  "session_id": "session_123",
  "tools_enabled": true
}
```

### Update Intent
```json
{
  "message": "Update the Account Number entity to have a higher confidence score",
  "session_id": "session_123",
  "tools_enabled": true
}
```

### Delete Intent
```json
{
  "message": "Delete the Account Number entity",
  "session_id": "session_123",
  "tools_enabled": true
}
```

## Primary Agent Input Payload

### Standard Chat Request Format
```json
{
  "message": "Extract entities from the selected BC3 fields and asset columns to analyze credit risk patterns and identify key business metrics.",
  "session_id": "primary_session_001",
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

### Expected Output Format

> **Note**: The LLM integration is currently experiencing connectivity issues with Vertex AI, but the core entity extraction and management systems are fully functional. The examples below show the expected output format when the LLM is working properly.
```json
{
  "response": "I've successfully extracted entities from your BC3 fields and data assets. Here are the key findings:\n\n**Extracted Entities:**\n• Account Number (Field) - Unique identifier for credit accounts\n• Credit Limit (Field) - Maximum credit available on accounts\n• Credit Score (Business Metric) - Numerical creditworthiness representation\n\n**Key Insights:**\n• Account numbers are masked for security in production\n• Credit limits range from $5,000 to $50,000\n• Credit scores provide risk assessment capabilities",
  "chat_output": "🤖 **AI Response:**\nI've successfully extracted entities from your BC3 fields and data assets. Here are the key findings:\n\n**📊 Extracted Entities:**\n• **Account Number** (Field) - Unique identifier for credit accounts\n• **Credit Limit** (Field) - Maximum credit available on accounts  \n• **Credit Score** (Business Metric) - Numerical creditworthiness representation\n\n**🔍 Key Insights:**\n• Account numbers are masked for security in production\n• Credit limits range from $5,000 to $50,000\n• Credit scores provide risk assessment capabilities\n\n✅ **Successfully extracted 3 entities with high confidence**",
  "extracted_entities": [
    {
      "entity_id": "entity_001",
      "entity_type": "field",
      "entity_name": "Account Number",
      "entity_value": "Unique identifier for the credit account",
      "confidence": 0.95,
      "source_field": "field_001",
      "description": "Business dictionary field: Account Number",
      "relationships": {},
      "context_provider": "credit_domain",
      "attributes": [
        {
          "attribute_id": "attr_001",
          "attribute_name": "known_implementations",
          "attribute_value": "account_number, credit_account",
          "attribute_type": "string",
          "confidence": 0.9,
          "source_field": "field_001",
          "description": "Known implementation names for Account Number"
        },
        {
          "attribute_id": "attr_002",
          "attribute_name": "valid_values",
          "attribute_value": "1234567890, 0987654321, 1122334455",
          "attribute_type": "string",
          "confidence": 0.9,
          "source_field": "field_001",
          "description": "Valid account number values"
        },
        {
          "attribute_id": "attr_003",
          "attribute_name": "security_notes",
          "attribute_value": "Masked for security in production",
          "attribute_type": "string",
          "confidence": 0.85,
          "source_field": "field_001",
          "description": "Security considerations for account numbers"
        }
      ],
      "created_at": "2025-09-05T13:55:05.938001Z",
      "updated_at": "2025-09-05T13:55:05.938442Z",
      "state_version": 2
    },
    {
      "entity_id": "entity_002",
      "entity_type": "field",
      "entity_name": "Credit Limit",
      "entity_value": "Maximum amount of credit available on the account",
      "confidence": 0.95,
      "source_field": "field_002",
      "description": "Business dictionary field: Credit Limit",
      "relationships": {},
      "context_provider": "credit_domain",
      "attributes": [
        {
          "attribute_id": "attr_004",
          "attribute_name": "known_implementations",
          "attribute_value": "credit_limit, max_credit",
          "attribute_type": "string",
          "confidence": 0.9,
          "source_field": "field_002",
          "description": "Known implementation names for Credit Limit"
        },
        {
          "attribute_id": "attr_005",
          "attribute_name": "valid_values",
          "attribute_value": "5000, 10000, 25000, 50000",
          "attribute_type": "string",
          "confidence": 0.9,
          "source_field": "field_002",
          "description": "Valid credit limit values"
        }
      ],
      "created_at": "2025-09-05T13:55:05.938001Z",
      "updated_at": "2025-09-05T13:55:05.938442Z",
      "state_version": 2
    },
    {
      "entity_id": "entity_003",
      "entity_type": "business_metric",
      "entity_name": "Credit Score",
      "entity_value": "Numerical representation of creditworthiness",
      "confidence": 0.98,
      "source_field": "credit_score",
      "description": "Data asset column: Credit Score",
      "relationships": {},
      "context_provider": "data_asset",
      "attributes": [
        {
          "attribute_id": "attr_006",
          "attribute_name": "score_range",
          "attribute_value": "300-850",
          "attribute_type": "string",
          "confidence": 0.95,
          "source_field": "credit_score",
          "description": "Valid credit score range"
        },
        {
          "attribute_id": "attr_007",
          "attribute_name": "data_source",
          "attribute_value": "Consumer Credit Database",
          "attribute_type": "string",
          "confidence": 1.0,
          "source_field": "asset_name",
          "description": "Source database for credit score data"
        }
      ],
      "created_at": "2025-09-05T13:55:23.661406Z",
      "updated_at": "2025-09-05T13:55:23.661707Z",
      "state_version": 2
    }
  ],
  "chat_state": {
    "session_id": "primary_session_001",
    "messages": [
      {
        "role": "user",
        "content": "Extract entities from the selected BC3 fields and asset columns to analyze credit risk patterns and identify key business metrics.",
        "timestamp": "2025-09-05T13:55:05.938001Z"
      }
    ],
    "selected_segments": [],
    "selected_assets": [],
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
    "extracted_entities": [
      {
        "entity_id": "entity_001",
        "entity_type": "field",
        "entity_name": "Account Number",
        "entity_value": "Unique identifier for the credit account",
        "confidence": 0.95,
        "source_field": "field_001",
        "description": "Business dictionary field: Account Number",
        "relationships": {},
        "context_provider": "credit_domain",
        "attributes": [],
        "created_at": "2025-09-05T13:55:05.938001Z",
        "updated_at": "2025-09-05T13:55:05.938442Z",
        "state_version": 2
      }
    ],
    "state_version": 3,
    "last_updated": "2025-09-05T13:55:23.661707Z",
    "metadata": {}
  },
  "confidence_score": 0.96,
  "processing_time": 2.45,
  "metadata": {
    "session_id": "primary_session_001",
    "extraction_method": "llm_driven",
    "tools_used": ["extract_credit_domain_entities", "extract_data_asset_entities"],
    "entities_extracted": 3,
    "attributes_extracted": 7
  }
}
```

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
  "response": "string (LLM response text)",
  "chat_output": "string (Formatted chat output with bulleted entities and relationships)",
  "extracted_entities": [
    {
      "entity_id": "string (Unique entity identifier)",
      "entity_type": "string (FIELD|DERIVED_INSIGHT|RELATIONSHIP|BUSINESS_METRIC|OPERATIONAL_RULE)",
      "entity_name": "string",
      "entity_value": "string",
      "confidence": "number (0.0-1.0)",
      "source_field": "string",
      "description": "string",
      "relationships": "object (Relationships with other entities)",
      "context_provider": "string (credit_domain|data_asset)",
      "attributes": [
        {
          "attribute_id": "string (Unique attribute identifier)",
          "attribute_name": "string",
          "attribute_value": "string",
          "attribute_type": "string",
          "confidence": "number (0.0-1.0)",
          "source_field": "string",
          "description": "string",
          "created_at": "string (ISO timestamp)",
          "updated_at": "string (ISO timestamp)",
          "metadata": "object"
        }
      ],
      "created_at": "string (ISO timestamp)",
      "updated_at": "string (ISO timestamp)",
      "state_version": "number (Auto-incrementing version)"
    }
  ],
  "chat_state": {
    "session_id": "string",
    "messages": "array (Chat message history)",
    "selected_segments": "array",
    "selected_assets": "array", 
    "selected_bc3_fields": "array",
    "selected_asset_columns": "array",
    "extracted_entities": "array (Entities in session)",
    "state_version": "number (Session state version)",
    "last_updated": "string (ISO timestamp)",
    "metadata": "object"
  },
  "confidence_score": "number (Overall extraction confidence)",
  "processing_time": "number (Seconds)",
  "metadata": {
    "session_id": "string",
    "extraction_method": "string (llm_driven|fallback)",
    "tools_used": "array (Tools utilized)",
    "entities_extracted": "number",
    "attributes_extracted": "number"
  }
}
```

### Entity Types
- **FIELD**: Direct entities from BC3 fields or asset columns
- **DERIVED_INSIGHT**: Calculated or inferred business metrics
- **RELATIONSHIP**: Connections between multiple entities
- **BUSINESS_METRIC**: Key performance indicators
- **OPERATIONAL_RULE**: Business rules and constraints

## Testing the API

### Using curl - Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

### Using curl - CRUD Endpoints (When LLM is unavailable)
```bash
# Create/Update an entity with attributes
curl -X POST "http://localhost:8000/entities/update" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "entity_id": "account_number_entity",
    "entity_updates": {
      "entity_name": "Account Number",
      "entity_type": "field",
      "entity_value": "Unique identifier for the credit account",
      "confidence": 0.95,
      "source_field": "field_001",
      "description": "Business dictionary field: Account Number",
      "context_provider": "credit_domain"
    },
    "attribute_updates": [
      {
        "attribute_name": "known_implementations",
        "attribute_value": "account_number, credit_account",
        "attribute_type": "string",
        "confidence": 0.9,
        "source_field": "field_001",
        "description": "Known implementation names for Account Number"
      }
    ]
  }'

# Read entities with filtering
curl -X POST "http://localhost:8000/entities/read" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_session",
    "entity_type": "field",
    "include_attributes": true
  }'
```

### Using Python
```python
import requests
import json

# Chat endpoint
url = "http://localhost:8000/chat"
headers = {"Content-Type": "application/json"}

with open("payload.json", "r") as f:
    payload = json.load(f)

response = requests.post(url, headers=headers, json=payload)
print(json.dumps(response.json(), indent=2))

# CRUD endpoints
# Create entity
create_url = "http://localhost:8000/entities/update"
create_payload = {
    "session_id": "test_session",
    "entity_id": "credit_score_entity",
    "entity_updates": {
        "entity_name": "Credit Score",
        "entity_type": "business_metric",
        "entity_value": "Numerical representation of creditworthiness",
        "confidence": 0.98,
        "source_field": "credit_score",
        "description": "Data asset column: Credit Score",
        "context_provider": "data_asset"
    }
}
response = requests.post(create_url, headers=headers, json=create_payload)
print(json.dumps(response.json(), indent=2))

# Read entities
read_url = "http://localhost:8000/entities/read"
read_payload = {
    "session_id": "test_session",
    "include_attributes": True
}
response = requests.post(read_url, headers=headers, json=read_payload)
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

## New Features & Capabilities

### 🆕 **Intent-Based Workflow System**
- **Smart Intent Detection**: Automatically analyzes user messages to determine desired actions
- **Intelligent Routing**: Routes requests to appropriate workflow nodes based on intent
- **Contextual Responses**: Provides responses tailored to the detected intent
- **Tool Integration**: Uses specialized tools for different operations (extract, read, update, delete)

### 🆕 **Enhanced Entity Structure**
- **Unique Entity IDs**: Each entity has a unique identifier for tracking
- **Attribute Management**: Entities can have multiple attributes with individual IDs
- **State Versioning**: Auto-incrementing version numbers for change tracking
- **Timestamp Tracking**: Created/updated timestamps for audit trails

### 🆕 **Advanced Entity Management**
- **CRUD Operations**: Create, Read, Update, Delete entities and attributes
- **Flexible Filtering**: Filter by entity type, ID, or state version
- **Attribute-Level Operations**: Update or delete specific attributes within entities
- **Session State Management**: Persistent session state with versioning

### 🆕 **Improved Output Format**
- **Chat Output**: Human-readable formatted output with bulleted entities
- **Rich Metadata**: Detailed extraction metadata and tool usage information
- **Confidence Scoring**: Individual confidence scores for entities and attributes
- **Relationship Modeling**: Structured relationship representation between entities

### 🆕 **Agent Tool Integration**
- **LangChain Tools**: Entity extraction methods available as callable tools
- **CRUD Tools**: Read, update, and delete operations available to the agent
- **Comprehensive Documentation**: Detailed docstrings for all tools with examples
- **Workflow Architecture**: LangGraph-based state management with conditional routing
- **Tool Documentation**: Comprehensive docstrings for agent tool usage

## Workflow Architecture

### Intent Detection Flow
1. **Message Analysis**: User message is analyzed for intent keywords
2. **Intent Classification**: Message is classified into one of 6 intent types
3. **Route Selection**: Appropriate workflow node is selected based on intent
4. **Tool Execution**: Relevant tools are called based on the intent
5. **Response Generation**: Contextual response is generated for the specific intent

### Supported Intent Types
- **extract**: Extract entities from BC3 fields and data assets
- **read**: Retrieve and display existing entities from a session
- **update_entity**: Modify entity-level information
- **update_attribute**: Modify specific attributes within entities
- **delete_entity**: Remove entire entities
- **delete_attribute**: Remove specific attributes from entities

### Workflow Nodes
- **analyze_request**: Initial request analysis and validation
- **detect_intent**: Intent detection and classification
- **route_action**: Route to appropriate action node
- **extract_entities**: Entity extraction workflow
- **update_entities**: Entity update workflow
- **delete_entities**: Entity deletion workflow
- **read_entities**: Entity reading workflow
- **generate_response**: Final response generation

## Best Practices

1. **Session Management**: Use unique session IDs for different conversations
2. **Field Selection**: Include relevant BC3 fields and asset columns for comprehensive analysis
3. **Message Clarity**: Be specific about what entities you want to extract
4. **Context Provider**: Always set to "credit_domain" for credit-related analysis
5. **Tools Enabled**: Keep true for entity extraction capabilities
6. **Entity IDs**: Use meaningful entity IDs for better tracking and management
7. **State Versioning**: Monitor state versions for change tracking and rollback capabilities
8. **Attribute Organization**: Group related information as attributes within entities

## Performance Notes

- **Typical Response Time**: 3-5 seconds for complex entity extraction, < 1 second for CRUD operations
- **Entity Limit**: No hard limit, but typically 3-10 entities per request
- **Attribute Limit**: No hard limit, typically 2-5 attributes per entity
- **Memory**: Sessions are maintained in Firestore for persistence and scalability
- **State Versioning**: Minimal overhead with integer increments
- **Scalability**: Designed for multi-user sessions with Firestore backend
- **CRUD Performance**: Sub-second response times for entity management operations
- **Tool Integration**: LangChain tools provide seamless agent integration
