"""
Sample Payloads and Documentation for Custom Entity Extraction Agent API

This file contains example requests and responses for the API endpoints.

==============================================================================
QUICK USAGE GUIDE - WHICH PAYLOAD FOR WHICH ENDPOINT
==============================================================================

1. POST /extract-entities (Main Generic Endpoint)
   - Use: SAMPLE_GENERIC_ENDPOINT_REQUEST or SAMPLE_GENERIC_ENDPOINT_REQUEST_2
   - Supports: Both BC3 and generic data via context_provider field
   - Example: curl -X POST "http://localhost:8000/extract-entities" -H "Content-Type: application/json" -d @sample_request.json

2. POST /extract-entities/bc3 (BC3-Specific Endpoint)
   - Use: SAMPLE_BC3_ENDPOINT_REQUEST
   - Supports: Only BC3 data (context_provider auto-set to "bc3")
   - Example: curl -X POST "http://localhost:8000/extract-entities/bc3" -H "Content-Type: application/json" -d @bc3_request.json

3. POST /extract-entities/generic (Generic-Specific Endpoint)
   - Use: SAMPLE_GENERIC_SPECIFIC_REQUEST
   - Supports: Only generic data (context_provider auto-set to "generic")
   - Example: curl -X POST "http://localhost:8000/extract-entities/generic" -H "Content-Type: application/json" -d @generic_request.json

4. GET /health (Health Check)
   - No payload needed
   - Example: curl -X GET "http://localhost:8000/health"

5. GET /context-providers (Get Available Context Providers)
   - No payload needed
   - Example: curl -X GET "http://localhost:8000/context-providers"

==============================================================================
PAYLOAD SELECTION MATRIX
==============================================================================

| Your Data Type | Recommended Endpoint | Use This Payload | Notes |
|----------------|---------------------|------------------|-------|
| BC3 Data | /extract-entities | SAMPLE_GENERIC_ENDPOINT_REQUEST | Set context_provider: "bc3" |
| BC3 Data | /extract-entities/bc3 | SAMPLE_BC3_ENDPOINT_REQUEST | context_provider auto-set |
| Generic JSON | /extract-entities | SAMPLE_GENERIC_ENDPOINT_REQUEST_2 | Set context_provider: "generic" |
| Generic JSON | /extract-entities/generic | SAMPLE_GENERIC_SPECIFIC_REQUEST | context_provider auto-set |
| Mixed/Unknown | /extract-entities | SAMPLE_GENERIC_ENDPOINT_REQUEST | Most flexible option |

==============================================================================
"""


SAMPLE_BC3_DATA = {
    "segment_name": "Account History",
    "data_dictionary": [
        {
            "definition": "The account history for the specified segment property.",
            "bc3_field": "hist_eff_dte",
            "description": "History Effective Date",
            "notes": "Notes on account history: includes details, clarifications, or any specific remarks about the BC3 segment data.",
            "valid_values": [
                "History based value",
                "Effective",
                "Date of inquiry"
            ]
        },
        {
            "definition": "De-converted C2 MOP value from Account Rating Code",
            "bc3_field": "acct_mop_cde",
            "description": "Account Rating Code",
            "valid_values": [],
            "notes": ""
        },
        {
            "definition": "",
            "bc3_field": "acct_rte_prfl_cde",
            "description": "Account Rating Profile Code",
            "valid_values": [],
            "notes": "Long descriptions in appendix"
        },
        {
            "definition": "The maximum amount of credit that can be extended for that account.",
            "bc3_field": "cr_lmt_amt",
            "description": "Credit Limit Amount",
            "notes": "",
            "valid_values": []
        },
        {
            "definition": "The total amount that is owed on the account at the time of the update.",
            "bc3_field": "curr_bal_amt",
            "description": "Current Balance Amount",
            "notes": "",
            "valid_values": []
        }
    ]
}

# Sample Generic Data
SAMPLE_GENERIC_DATA = {
    "user_profile": {
        "id": "user_12345",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "preferences": {
            "theme": "dark",
            "notifications": True,
            "language": "en"
        },
        "subscriptions": [
            {
                "plan": "premium",
                "start_date": "2024-01-01",
                "features": ["api_access", "priority_support"]
            },
            {
                "plan": "basic",
                "start_date": "2023-06-01",
                "features": ["basic_access"]
            }
        ]
    },
    "metadata": {
        "created_at": "2024-01-15T10:30:00Z",
        "version": "1.0.0",
        "tags": ["customer", "premium"]
    }
}

# =============================================================================
# ENDPOINT-SPECIFIC SAMPLE REQUESTS
# =============================================================================

# =============================================================================
# ENDPOINT: POST /extract-entities (Generic Endpoint)
# =============================================================================
# Use this payload for the main generic extraction endpoint
# Supports both BC3 and generic data with context_provider field
SAMPLE_GENERIC_ENDPOINT_REQUEST = {
    "message": "Extract all entities from this BC3 Account History segment and provide insights about the data quality.",
    "data": SAMPLE_BC3_DATA,
    "context_provider": "bc3",  # Can be "bc3" or "generic"
    "chat_history": [],
    "session_id": "session_12345",
    "tools_enabled": True,
    "metadata": {
        "source": "firestore",
        "collection": "bc3_segments",
        "document_id": "account_history_001"
    }
}

# Alternative generic endpoint request with generic data
SAMPLE_GENERIC_ENDPOINT_REQUEST_2 = {
    "message": "Analyze this user profile data and extract all meaningful entities including nested objects and arrays.",
    "data": SAMPLE_GENERIC_DATA,
    "context_provider": "generic",  # Can be "bc3" or "generic"
    "chat_history": [
        {
            "role": "user",
            "content": "What entities can you extract from user data?",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I can extract various entities from user data including profile information, preferences, subscriptions, and metadata. Would you like me to analyze a specific dataset?",
            "timestamp": "2024-01-15T10:01:00Z"
        }
    ],
    "session_id": "session_67890",
    "tools_enabled": True,
    "metadata": {
        "source": "api",
        "user_id": "user_12345",
        "analysis_type": "profile_extraction"
    }
}

# =============================================================================
# ENDPOINT: POST /extract-entities/bc3 (BC3-Specific Endpoint)
# =============================================================================
# Use this payload for the BC3-specific endpoint
# context_provider is automatically set to "bc3"
SAMPLE_BC3_ENDPOINT_REQUEST = {
    "message": "Extract all entities from this BC3 Account History segment and provide insights about the data quality.",
    "data": SAMPLE_BC3_DATA,
    # Note: context_provider is automatically set to "bc3" for this endpoint
    "chat_history": [],
    "session_id": "session_12345",
    "tools_enabled": True,
    "metadata": {
        "source": "firestore",
        "collection": "bc3_segments",
        "document_id": "account_history_001"
    }
}

# =============================================================================
# ENDPOINT: POST /extract-entities/generic (Generic-Specific Endpoint)
# =============================================================================
# Use this payload for the generic-specific endpoint
# context_provider is automatically set to "generic"
SAMPLE_GENERIC_SPECIFIC_REQUEST = {
    "message": "Analyze this user profile data and extract all meaningful entities including nested objects and arrays.",
    "data": SAMPLE_GENERIC_DATA,
    # Note: context_provider is automatically set to "generic" for this endpoint
    "chat_history": [
        {
            "role": "user",
            "content": "What entities can you extract from user data?",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I can extract various entities from user data including profile information, preferences, subscriptions, and metadata. Would you like me to analyze a specific dataset?",
            "timestamp": "2024-01-15T10:01:00Z"
        }
    ],
    "session_id": "session_67890",
    "tools_enabled": True,
    "metadata": {
        "source": "api",
        "user_id": "user_12345",
        "analysis_type": "profile_extraction"
    }
}

# =============================================================================
# LEGACY PAYLOADS (for backward compatibility)
# =============================================================================
SAMPLE_BC3_REQUEST = SAMPLE_BC3_ENDPOINT_REQUEST  # Use for /extract-entities/bc3
SAMPLE_GENERIC_REQUEST = SAMPLE_GENERIC_SPECIFIC_REQUEST  # Use for /extract-entities/generic

# Sample API Responses

SAMPLE_BC3_RESPONSE = {
    "response": "I've successfully analyzed the BC3 Account History segment and extracted 15 entities. Here's my analysis:\n\n**Data Quality Assessment:**\n- Overall data quality score: 0.75 (Good)\n- 5 fields with definitions (100%)\n- 2 fields with notes (40%)\n- 1 field with valid values (20%)\n\n**Key Entities Extracted:**\n- **Segment**: Account History (confidence: 1.0)\n- **Fields**: 5 BC3 fields including hist_eff_dte, acct_mop_cde, acct_rte_prfl_cde, cr_lmt_amt, curr_bal_amt\n- **Values**: 3 valid values for History Effective Date\n- **Metadata**: Notes for account history and rating profile code\n\n**Business Insights:**\n- The segment focuses on account history and credit information\n- Most fields are well-defined but could benefit from more valid value constraints\n- The data structure follows BC3 standards effectively",
    "extracted_entities": [
        {
            "entity_type": "segment",
            "entity_name": "segment_name",
            "entity_value": "Account History",
            "confidence": 1.0,
            "source_field": "segment_name",
            "description": "Business segment: Account History",
            "context_provider": "bc3"
        },
        {
            "entity_type": "field",
            "entity_name": "hist_eff_dte",
            "entity_value": "History Effective Date",
            "confidence": 0.95,
            "source_field": "hist_eff_dte",
            "description": "The account history for the specified segment property.",
            "context_provider": "bc3"
        },
        {
            "entity_type": "value",
            "entity_name": "hist_eff_dte_value",
            "entity_value": "History based value",
            "confidence": 0.9,
            "source_field": "hist_eff_dte",
            "description": "Valid value for History Effective Date: History based value",
            "context_provider": "bc3"
        }
        # ... more entities would be included
    ],
    "chat_history": [
        {
            "role": "user",
            "content": "Extract all entities from this BC3 Account History segment and provide insights about the data quality.",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "role": "assistant",
            "content": "I've successfully analyzed the BC3 Account History segment...",
            "timestamp": "2024-01-15T10:30:05Z"
        }
    ],
    "session_id": "session_12345",
    "confidence_score": 0.92,
    "processing_time": 2.34,
    "metadata": {
        "analysis": {
            "context_provider": "bc3",
            "segment_name": "Account History",
            "total_fields": 5,
            "fields_with_definitions": 5,
            "fields_with_notes": 2,
            "fields_with_valid_values": 1,
            "field_types": {
                "date": 1,
                "amount": 2,
                "code": 2
            },
            "data_quality_score": 0.75
        },
        "tools_enabled": True,
        "context_provider": "bc3",
        "source": "firestore",
        "collection": "bc3_segments",
        "document_id": "account_history_001"
    }
}

SAMPLE_GENERIC_RESPONSE = {
    "response": "I've analyzed the user profile data and extracted 12 entities. Here's my analysis:\n\n**Data Structure Overview:**\n- Complex nested object with user profile information\n- Contains preferences object and subscriptions array\n- Well-structured metadata\n\n**Key Entities Extracted:**\n- **Document**: Root object with 2 main sections\n- **Objects**: user_profile, preferences, metadata\n- **Arrays**: subscriptions (2 items)\n- **Fields**: id, name, email, theme, notifications, language, plan, start_date, features\n\n**Data Quality:**\n- Good structure with clear hierarchy\n- Consistent data types\n- Comprehensive user information\n\n**Business Insights:**\n- User has multiple subscription plans\n- Preferences are well-defined\n- Metadata provides good tracking information",
    "extracted_entities": [
        {
            "entity_type": "document",
            "entity_name": "document",
            "entity_value": "dict",
            "confidence": 0.9,
            "source_field": "root",
            "description": "Document with 2 fields",
            "context_provider": "generic"
        },
        {
            "entity_type": "object",
            "entity_name": "user_profile",
            "entity_value": "Object with 5 fields",
            "confidence": 0.85,
            "source_field": "user_profile",
            "description": "Object field: user_profile",
            "context_provider": "generic"
        },
        {
            "entity_type": "field",
            "entity_name": "id",
            "entity_value": "user_12345",
            "confidence": 0.95,
            "source_field": "user_profile.id",
            "description": "Field: id = user_12345",
            "context_provider": "generic"
        }
        # ... more entities would be included
    ],
    "chat_history": [
        {
            "role": "user",
            "content": "What entities can you extract from user data?",
            "timestamp": "2024-01-15T10:00:00Z"
        },
        {
            "role": "assistant",
            "content": "I can extract various entities from user data including profile information, preferences, subscriptions, and metadata. Would you like me to analyze a specific dataset?",
            "timestamp": "2024-01-15T10:01:00Z"
        },
        {
            "role": "user",
            "content": "Analyze this user profile data and extract all meaningful entities including nested objects and arrays.",
            "timestamp": "2024-01-15T10:30:00Z"
        },
        {
            "role": "assistant",
            "content": "I've analyzed the user profile data and extracted 12 entities...",
            "timestamp": "2024-01-15T10:30:03Z"
        }
    ],
    "session_id": "session_67890",
    "confidence_score": 0.88,
    "processing_time": 1.87,
    "metadata": {
        "analysis": {
            "context_provider": "generic",
            "total_elements": 15,
            "structure_info": {
                "type": "dict",
                "path": "",
                "fields": 2,
                "field_names": ["user_profile", "metadata"],
                "nested_objects": 2
            },
            "data_types": ["dict", "str", "bool", "list"],
            "complexity_score": 8
        },
        "tools_enabled": True,
        "context_provider": "generic",
        "source": "api",
        "user_id": "user_12345",
        "analysis_type": "profile_extraction"
    }
}

# API Documentation

API_DOCUMENTATION = """
# Custom Entity Extraction Agent API Documentation

## Overview
The Custom Entity Extraction Agent API provides intelligent entity extraction from various data structures using LangGraph and Vertex AI. It supports multiple context providers including BC3 (Business Credit Bureau) data and generic JSON documents.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required. For production use, implement appropriate authentication mechanisms.

## Endpoints

### 1. Health Check
**GET** `/health`

Check the health status of the API.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0"
}
```

### 2. Extract Entities (Generic)
**POST** `/extract-entities`

Extract entities from any supported data structure.

**Request Body:**
```json
{
  "message": "Your analysis request",
  "data": {
    // Your data structure here
  },
  "context_provider": "generic",
  "chat_history": [],
  "session_id": "optional_session_id",
  "tools_enabled": true,
  "metadata": {}
}
```

### 3. Extract BC3 Entities
**POST** `/extract-entities/bc3`

Extract entities specifically from BC3 data structures.

**Request Body:**
```json
{
  "message": "Extract all entities from this BC3 segment",
  "data": {
    "segment_name": "Account History",
    "data_dictionary": [
      {
        "definition": "Field definition",
        "bc3_field": "field_code",
        "description": "Field description",
        "notes": "Additional notes",
        "valid_values": ["value1", "value2"]
      }
    ]
  },
  "chat_history": [],
  "session_id": "optional_session_id",
  "tools_enabled": true,
  "metadata": {}
}
```

### 4. Extract Generic Entities
**POST** `/extract-entities/generic`

Extract entities from generic JSON documents.

**Request Body:**
```json
{
  "message": "Analyze this data structure",
  "data": {
    // Any JSON structure
  },
  "chat_history": [],
  "session_id": "optional_session_id",
  "tools_enabled": true,
  "metadata": {}
}
```

### 5. Get Context Providers
**GET** `/context-providers`

Get information about supported context providers.

**Response:**
```json
{
  "context_providers": [
    {
      "name": "bc3",
      "description": "Business Credit Bureau data structures",
      "features": ["Segment analysis", "Field extraction", "Value validation"]
    },
    {
      "name": "generic",
      "description": "Generic JSON documents and data structures",
      "features": ["Nested object analysis", "Array processing", "Type detection"]
    }
  ]
}
```

## Response Format

All extraction endpoints return the same response format:

```json
{
  "response": "AI-generated analysis and insights",
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
  "chat_history": [
    {
      "role": "user|assistant",
      "content": "message_content",
      "timestamp": "2024-01-15T10:30:00Z"
    }
  ],
  "session_id": "session_identifier",
  "confidence_score": 0.92,
  "processing_time": 2.34,
  "metadata": {
    "analysis": {},
    "tools_enabled": true,
    "context_provider": "bc3|generic|custom",
    "custom_metadata": {}
  }
}
```

## Entity Types

- **FIELD**: Individual data fields
- **SEGMENT**: Business segment or document section information
- **VALUE**: Important data values
- **METADATA**: Contextual information
- **OBJECT**: Complex nested objects
- **ARRAY**: List-based data structures
- **DOCUMENT**: Document-level information

## Error Handling

The API returns appropriate HTTP status codes:

- **200**: Success
- **400**: Bad Request (invalid input)
- **500**: Internal Server Error

Error responses include a detail message:

```json
{
  "detail": "Error description"
}
```

## Environment Variables

Set these environment variables before running the API:

```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # Optional, defaults to us-central1
```

## Running the API

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

3. Run the API:
```bash
python main.py
```

4. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Examples

See `sample_payloads.py` for complete examples of requests and responses.
"""

if __name__ == "__main__":
    print("Sample payloads and documentation loaded successfully!")
    print("\n" + "="*80)
    print("QUICK TESTING GUIDE")
    print("="*80)
    
    print("\n1. TEST HEALTH ENDPOINT:")
    print("   curl -X GET 'http://localhost:8000/health'")
    
    print("\n2. TEST MAIN GENERIC ENDPOINT (BC3 Data):")
    print("   curl -X POST 'http://localhost:8000/extract-entities' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Extract BC3 entities\", \"data\": " + str(SAMPLE_BC3_DATA)[:100] + "...\", \"context_provider\": \"bc3\"}'")
    
    print("\n3. TEST BC3-SPECIFIC ENDPOINT:")
    print("   curl -X POST 'http://localhost:8000/extract-entities/bc3' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Extract BC3 entities\", \"data\": " + str(SAMPLE_BC3_DATA)[:100] + "...\"}'")
    
    print("\n4. TEST GENERIC-SPECIFIC ENDPOINT:")
    print("   curl -X POST 'http://localhost:8000/extract-entities/generic' \\")
    print("     -H 'Content-Type: application/json' \\")
    print("     -d '{\"message\": \"Extract generic entities\", \"data\": " + str(SAMPLE_GENERIC_DATA)[:100] + "...\"}'")
    
    print("\n5. TEST CONTEXT PROVIDERS:")
    print("   curl -X GET 'http://localhost:8000/context-providers'")
    
    print("\n" + "="*80)
    print("PAYLOAD REFERENCE")
    print("="*80)
    print("• SAMPLE_GENERIC_ENDPOINT_REQUEST: Use for /extract-entities with BC3 data")
    print("• SAMPLE_GENERIC_ENDPOINT_REQUEST_2: Use for /extract-entities with generic data")
    print("• SAMPLE_BC3_ENDPOINT_REQUEST: Use for /extract-entities/bc3")
    print("• SAMPLE_GENERIC_SPECIFIC_REQUEST: Use for /extract-entities/generic")
    print("• SAMPLE_BC3_REQUEST: Legacy alias for BC3 endpoint")
    print("• SAMPLE_GENERIC_REQUEST: Legacy alias for generic endpoint")
    
    print("\n" + "="*80)
    print("EXPECTED RESPONSES")
    print("="*80)
    print("• Health: {\"status\": \"healthy\", \"timestamp\": \"...\", \"version\": \"1.0.0\"}")
    print("• BC3 Extraction: ~7 business entities (segment, fields, values)")
    print("• Generic Extraction: ~1-5 business entities (depending on data)")
    print("• Context Providers: List of available context providers")
