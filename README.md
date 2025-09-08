# BC3 AI Agent - Entity Extraction and Management

A comprehensive entity extraction and management agent for BC3 (Credit Domain) data and data assets with full CRUD operations.

## Architecture

**Modular & Clean:**
- `main.py` - FastAPI server entry point (23 lines)
- `routers.py` - All API endpoints with CRUD operations (269 lines)
- `models.py` - Pydantic models for API requests/responses (95 lines)
- `agent.py` - Core agent logic (122 lines)
- `config.py` - Configuration settings (47 lines)
- `tools.py` - LangChain tools (68 lines)
- `prompts.py` - System prompts (88 lines)
- `entity_collection_manager.py` - Firestore operations (432 lines)
- `entity_collection_models.py` - Data models (140 lines)

## Features

- ✅ **Entity Extraction**: `create_entities` tool - extracts and saves entities
- ✅ **Full CRUD Operations**: Create, Read, Update, Delete entities and attributes
- ✅ **Direct LLM Interaction**: No complex workflows
- ✅ **Firestore Integration**: Saves entities to `custom_entities` collection
- ✅ **RESTful API**: Complete set of endpoints for entity management
- ✅ **Configurable**: Environment variables and config.py
- ✅ **Modular**: Separated concerns (models, routers, config, tools, prompts)
- ✅ **Entity-Attribute Structure**: Creates meaningful business entities with multiple attributes
- ✅ **No Emojis**: Clean logging and responses

## Configuration

All settings are managed in `config.py`:

- **Google Cloud**: Project ID, location
- **LLM**: Model name, temperature, max tokens
- **Firestore**: Collection names
- **API**: Host, port

Override with environment variables:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export LLM_MODEL_NAME="gemini-2.5-pro"
export LLM_TEMPERATURE="0"
export LLM_MAX_OUTPUT_TOKENS="64000"
```

## Quick Start

1. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

2. **Set up Google Cloud:**
```bash
   gcloud auth login
   gcloud config set project firestore-470903
   gcloud auth application-default set-quota-project firestore-470903
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```

4. **Test the API:**
   ```bash
   curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Extract entities from BC3 fields",
       "session_id": "test_001",
       "selected_bc3_fields": [...],
       "selected_asset_columns": [...]
     }'
   ```

5. **View API Documentation:**
   - Open http://localhost:8000/docs in your browser
   - Interactive Swagger UI with all endpoints
   - Test endpoints directly from the browser

## API Documentation

### Chat Endpoint

**POST** `/chat`

Extract entities from BC3 fields and asset columns, creating meaningful business entities with attributes.

### Entity CRUD Operations

**GET** `/entities?session_id={id}` - Read entities for a session
**POST** `/entities` - Create new entity
**PUT** `/entities` - Update existing entity
**DELETE** `/entities` - Delete entity

### Attribute CRUD Operations

**GET** `/entities/{entity_id}/attributes` - Read attributes for an entity
**POST** `/entities/{entity_id}/attributes` - Create new attribute
**PUT** `/entities/{entity_id}/attributes/{attribute_id}` - Update attribute
**DELETE** `/entities/{entity_id}/attributes/{attribute_id}` - Delete attribute

#### Request Body

```json
{
  "message": "string",
  "session_id": "string",
  "selected_bc3_fields": [
    {
      "field": {
        "field_name": "string",
        "description": "string",
        "data_type": "string",
        "valid_values": ["string"],
        "notes": "string",
        "known_implementations": ["string"]
      },
      "segment_context": {
        "segment_name": "string",
        "segment_description": "string"
      }
    }
  ],
  "selected_asset_columns": [
    {
      "column_name": "string",
      "data_type": "string",
      "description": "string",
      "asset_name": "string",
      "workspace_name": "string",
      "big_query_table_name": "string"
    }
  ]
}
```

#### Response

```json
{
  "response": "string",
  "success": true,
  "entities_created": 2,
  "entities": [
    {
      "entity_id": "string",
      "session_id": "string",
      "entity_type": "asset",
      "entity_name": "string",
      "entity_value": "string",
      "confidence": 0.95,
      "source_field": "string",
      "description": "string",
      "attributes": [
        {
          "attribute_id": "string",
          "attribute_name": "string",
          "attribute_value": "string",
          "attribute_type": "string",
      "confidence": 0.9,
          "source_field": "string",
          "description": "string"
        }
      ]
    }
  ]
}
```

### Health Check

**GET** `/health`

Returns server health status.

```json
{
  "status": "healthy",
  "agent": "simple"
}
```

## Comprehensive Test Payloads

### Test 1: Basic Entity Extraction

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Extract entities from the BC3 fields and create meaningful business entities",
    "session_id": "test_basic_001",
    "selected_bc3_fields": [
      {
        "field": {
          "field_name": "account_number",
          "description": "Unique identifier for the credit account",
          "data_type": "string",
          "valid_values": ["numeric"],
          "notes": "Masked for security",
          "known_implementations": ["account_number", "credit_account"]
        },
        "segment_context": {
          "segment_name": "Account Management",
          "segment_description": "Manages customer account information"
        }
      }
    ],
    "selected_asset_columns": [
      {
        "column_name": "credit_score",
        "data_type": "Numeric",
        "description": "Customer credit score",
        "asset_name": "Consumer Credit Database",
        "workspace_name": "Credit Analytics Workspace",
        "big_query_table_name": "credit_analytics.consumer_credit_data"
      }
    ]
  }'
```

### Test 2: Multiple Entities with Multiple Attributes

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Extract entities from the BC3 fields and create meaningful business entities",
    "session_id": "test_comprehensive_001",
    "selected_bc3_fields": [
      {
        "field": {
          "field_name": "account_number",
          "description": "Unique identifier for the credit account",
          "data_type": "string",
          "valid_values": ["numeric"],
          "notes": "Masked for security",
          "known_implementations": ["account_number", "credit_account"]
        },
        "segment_context": {
          "segment_name": "Account Management",
          "segment_description": "Manages customer account information"
        }
      },
      {
        "field": {
          "field_name": "credit_limit",
          "description": "Maximum credit amount allowed for the account",
          "data_type": "numeric",
          "valid_values": ["positive numbers"],
          "notes": "Updated based on risk assessment",
          "known_implementations": ["credit_limit", "max_credit"]
        },
        "segment_context": {
          "segment_name": "Risk Management",
          "segment_description": "Manages credit risk and limits"
        }
      },
      {
        "field": {
          "field_name": "account_status",
          "description": "Current status of the credit account",
          "data_type": "string",
          "valid_values": ["active", "suspended", "closed"],
          "notes": "Updated in real-time",
          "known_implementations": ["status", "account_state"]
        },
        "segment_context": {
          "segment_name": "Account Management",
          "segment_description": "Manages customer account information"
        }
      }
    ],
    "selected_asset_columns": [
      {
        "column_name": "credit_score",
        "data_type": "Numeric",
        "description": "Customer credit score",
        "asset_name": "Consumer Credit Database",
        "workspace_name": "Credit Analytics Workspace",
        "big_query_table_name": "credit_analytics.consumer_credit_data"
      },
      {
        "column_name": "customer_id",
        "data_type": "String",
        "description": "Unique customer identifier",
        "asset_name": "Customer Database",
        "workspace_name": "Customer Management",
        "big_query_table_name": "customer_mgmt.customers"
      },
      {
        "column_name": "risk_rating",
        "data_type": "String",
        "description": "Customer risk rating",
        "asset_name": "Risk Assessment Database",
        "workspace_name": "Risk Management",
        "big_query_table_name": "risk_mgmt.assessments"
      },
      {
        "column_name": "transaction_amount",
        "data_type": "Numeric",
        "description": "Transaction amount",
        "asset_name": "Transaction Database",
        "workspace_name": "Transaction Processing",
        "big_query_table_name": "transactions.processed"
      }
    ]
  }'
```

### Test 3: Complex Business Scenario

```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Extract entities from the BC3 fields and create meaningful business entities",
    "session_id": "test_complex_001",
    "selected_bc3_fields": [
      {
        "field": {
          "field_name": "loan_amount",
          "description": "Total loan amount approved",
          "data_type": "numeric",
          "valid_values": ["positive numbers"],
          "notes": "Includes principal and fees",
          "known_implementations": ["loan_amount", "principal_amount"]
        },
        "segment_context": {
          "segment_name": "Loan Management",
          "segment_description": "Manages loan origination and servicing"
        }
      },
      {
        "field": {
          "field_name": "interest_rate",
          "description": "Annual interest rate for the loan",
          "data_type": "numeric",
          "valid_values": ["percentage values"],
          "notes": "Fixed or variable rate",
          "known_implementations": ["interest_rate", "apr"]
        },
        "segment_context": {
          "segment_name": "Loan Management",
          "segment_description": "Manages loan origination and servicing"
        }
      },
      {
        "field": {
          "field_name": "collateral_value",
          "description": "Estimated value of collateral",
          "data_type": "numeric",
          "valid_values": ["positive numbers"],
          "notes": "Appraised value",
          "known_implementations": ["collateral_value", "appraised_value"]
        },
        "segment_context": {
          "segment_name": "Collateral Management",
          "segment_description": "Manages collateral valuation and monitoring"
        }
      }
    ],
    "selected_asset_columns": [
      {
        "column_name": "borrower_id",
        "data_type": "String",
        "description": "Unique borrower identifier",
        "asset_name": "Borrower Database",
        "workspace_name": "Borrower Management",
        "big_query_table_name": "borrowers.profiles"
      },
      {
        "column_name": "employment_status",
        "data_type": "String",
        "description": "Current employment status",
        "asset_name": "Employment Database",
        "workspace_name": "Employment Verification",
        "big_query_table_name": "employment.verification"
      },
      {
        "column_name": "income_amount",
        "data_type": "Numeric",
        "description": "Annual income amount",
        "asset_name": "Income Database",
        "workspace_name": "Income Verification",
        "big_query_table_name": "income.verification"
      },
      {
        "column_name": "debt_to_income_ratio",
        "data_type": "Numeric",
        "description": "Debt to income ratio",
        "asset_name": "Financial Ratios Database",
        "workspace_name": "Financial Analysis",
        "big_query_table_name": "ratios.financial"
      }
    ]
  }'
```

## CRUD Operations Examples

### Create Entity

```bash
curl -X POST "http://localhost:8000/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_crud_001",
    "entity_name": "Customer Profile",
    "entity_type": "business_metric",
    "entity_value": "Customer profile information",
    "description": "A comprehensive customer profile with personal and financial information",
    "attributes": [
      {
        "attribute_name": "Customer Name",
        "attribute_value": "John Doe",
        "attribute_type": "string",
        "description": "Full name of the customer"
      },
      {
        "attribute_name": "Age",
        "attribute_value": "35",
        "attribute_type": "numeric",
        "description": "Age of the customer"
      }
    ]
  }'
```

### Read Entities

```bash
curl "http://localhost:8000/entities?session_id=test_crud_001"
```

### Update Entity

```bash
curl -X PUT "http://localhost:8000/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_crud_001",
    "entity_id": "entity_990434f1",
    "entity_name": "Updated Customer Profile",
    "description": "Updated description for the customer profile"
  }'
```

### Delete Entity

```bash
curl -X DELETE "http://localhost:8000/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_crud_001",
    "entity_id": "entity_990434f1"
  }'
```

### Read Attributes

```bash
curl "http://localhost:8000/entities/entity_990434f1/attributes?session_id=test_crud_001"
```

### Delete Attribute

```bash
curl -X DELETE "http://localhost:8000/entities/entity_990434f1/attributes/attr_b0caf65a" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_crud_001",
    "entity_id": "entity_990434f1",
    "attribute_id": "attr_b0caf65a"
  }'
```

## Entity Structure

The agent creates entities following this hierarchical structure:

```
Entity (Main Business Concept)
├── Attribute 1
├── Attribute 2  
├── Attribute 3
└── Attribute N
```

### Example Output

```json
{
  "entities_created": 2,
  "entities": [
    {
      "entity_name": "Credit Account",
      "entity_type": "asset",
      "description": "Represents a credit account with its associated attributes",
      "attributes": [
        {
          "attribute_name": "Account ID",
          "attribute_value": "Unique identifier for the credit account",
          "attribute_type": "string"
        },
        {
          "attribute_name": "Credit Limit",
          "attribute_value": "Maximum credit amount allowed",
          "attribute_type": "numeric"
        },
        {
          "attribute_name": "Account Status",
          "attribute_value": "Current status of the account",
          "attribute_type": "string"
        }
      ]
    },
    {
      "entity_name": "Customer Profile",
      "entity_type": "asset",
      "description": "Represents a customer with their associated attributes",
      "attributes": [
        {
          "attribute_name": "Customer ID",
          "attribute_value": "Unique customer identifier",
          "attribute_type": "string"
        },
        {
          "attribute_name": "Credit Score",
          "attribute_value": "Customer credit score",
          "attribute_type": "numeric"
        },
        {
          "attribute_name": "Risk Rating",
          "attribute_value": "Customer risk rating",
          "attribute_type": "string"
        }
      ]
    }
  ]
}
```

## Utilities

### Clear Firestore Collections

```bash
# Dry run to see what would be deleted
python3 clear_firestore_sessions.py --dry-run

# Clear both collections with confirmation
python3 clear_firestore_sessions.py

# Clear only custom_entities collection
python3 clear_firestore_sessions.py --collections custom_entities

# Clear without confirmation (use with caution)
python3 clear_firestore_sessions.py --confirm
```

## What We Learned

The original complex architecture with:
- 6 different tools
- LangGraph workflows
- Multiple abstraction layers
- Complex state management

**Was causing the LLM to fail at tool calling.**

The current approach with:
- 1 tool for extraction
- Full CRUD operations for management
- Direct LLM interaction
- Modular structure
- Entity-Attribute hierarchy
- Clean API design

**Works perfectly!** 

## Current Status

✅ **Fully Functional**: All CRUD operations working
✅ **Modular**: Clean separation of concerns
✅ **Tested**: Comprehensive test coverage
✅ **Documented**: Complete API documentation
✅ **Production Ready**: Stable and reliable