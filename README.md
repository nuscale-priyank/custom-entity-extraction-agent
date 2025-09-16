# Credit Domain AI Agent - LangGraph-Powered Conversational Entity Management

A comprehensive conversational AI agent powered by LangGraph for credit domain data and data assets with natural language entity building, full CRUD operations, intelligent session management, and advanced state persistence.

## 🚀 What's New - LangGraph Integration

**Enhanced with LangGraph for Advanced State Management:**
- ✅ **LangGraph StateGraph**: Complete workflow with nodes for message processing, intent analysis, tool execution, and response generation
- ✅ **Automatic State Persistence**: InMemory checkpointer for conversation state management
- ✅ **Thread-Based Sessions**: Unique thread IDs for each user session with automatic message accumulation
- ✅ **Intent-Based Routing**: Smart routing based on user intent analysis with conversation context
- ✅ **Enhanced Tool Integration**: Custom tool execution with proper error handling
- ✅ **Conversation Memory**: Full conversation history automatically maintained and accessible

## Architecture

**Modular LangGraph-Powered & Conversational:**
- `main.py` - FastAPI server entry point
- `routers.py` - All API endpoints with CRUD and conversation operations (now using LangGraph)
- `config.py` - Configuration settings

**Services Package (`services/`):**
- `agent.py` - **LangGraph-based conversational agent with state management**
- `simple_agent.py` - Simplified agent for direct entity extraction
- `entity_collection_manager.py` - Firestore operations and entity CRUD
- `chat_session_manager.py` - Legacy conversation history and session management
- `relationship_detector.py` - Entity relationship detection and analysis
- `tools.py` - LangChain tools for entity operations
- `prompts.py` - System prompts and templates

**Models Package (`models/`):**
- `models.py` - Pydantic models for API requests/responses
- `entity_collection_models.py` - Data models for entities and attributes

## Features

- ✅ **LangGraph State Management**: Advanced conversation state persistence with automatic message accumulation
- ✅ **Conversational Interface**: Natural language entity building through chat with full context awareness
- ✅ **Intent Recognition**: Understands extract, create, list, update, delete, help commands with conversation context
- ✅ **Session Management**: Persistent conversation history and context tracking with thread-based sessions
- ✅ **Entity Extraction**: `create_entities` tool - extracts and saves entities from credit domain/asset data
- ✅ **Natural Language Entity Creation**: Create sophisticated business entities from natural language descriptions
- ✅ **Full CRUD Operations**: Create, Read, Update, Delete entities and attributes
- ✅ **Direct LLM Interaction**: Vertex AI integration with conversation context
- ✅ **Firestore Integration**: Saves entities to `llmops-demo-track2` database
- ✅ **RESTful API**: Complete set of endpoints for entity management
- ✅ **Configuration Constants**: Centralized config management, no hardcoded values
- ✅ **Modular Architecture**: Clean separation with managers/ and services/ packages
- ✅ **Entity-Attribute Structure**: Creates meaningful business entities with multiple attributes
- ✅ **Relationship Detection**: Automatic detection and analysis of entity relationships
- ✅ **Clean Logging**: Professional logging without emojis

## Configuration

All settings are managed in `config.py`:

- **Google Cloud**: Project ID, location, database ID
- **LLM**: Model name, temperature, max tokens
- **Firestore**: Collection names, database configuration
- **API**: Host, port

### Default Configuration:
```python
PROJECT_ID = "firestore-470903"
DATABASE_ID = "llmops-demo-track2"
MODEL_NAME = "gemini-2.5-pro"
TEMPERATURE = 0
MAX_OUTPUT_TOKENS = 64000
FIRESTORE_COLLECTION_CUSTOM_ENTITIES = "custom_entities"
FIRESTORE_COLLECTION_CHAT_SESSIONS = "chat_sessions"
API_HOST = "0.0.0.0"
API_PORT = 8000
DEFAULT_USER_ID = "default_user"
THREAD_PREFIX = "thread"
DEFAULT_CONVERSATION_LIMIT = 10
```

### Environment Variable Overrides:
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export FIRESTORE_DATABASE_ID="your-database-id"
export LLM_MODEL_NAME="gemini-2.5-pro"
export LLM_TEMPERATURE="0"
export LLM_MAX_OUTPUT_TOKENS="64000"
export DEFAULT_USER_ID="your-default-user"
export THREAD_PREFIX="your-thread-prefix"
export DEFAULT_CONVERSATION_LIMIT="20"
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
source .venv/bin/activate && python main.py
```

4. **Test the API:**
```bash
curl -X POST "http://localhost:8000/conversation?user_id=test_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me understand what this system does?",
    "session_id": "test_001",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

5. **View API Documentation:**
   - Open http://localhost:8000/docs in your browser
   - Interactive Swagger UI with all endpoints
   - Test endpoints directly from the browser

## API Documentation

### 🆕 LangGraph-Powered Conversational Endpoints

**POST** `/conversation` - Main conversational interface with LangGraph state management
**GET** `/conversation/{session_id}/history` - Get conversation history with LangGraph persistence
**GET** `/conversation/{session_id}/summary` - Get session summary with LangGraph state
**POST** `/conversation/{session_id}/context` - Update session context

### Traditional Chat Endpoint

**POST** `/conversation` - Extract entities from credit domain fields and asset columns

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

### Health Check

**GET** `/health` - Server health status

## Comprehensive API Examples

### 🆕 LangGraph Conversational Examples

#### Basic Help Request
```bash
curl -X POST "http://localhost:8000/conversation?user_id=demo_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello! Can you help me understand what this system does?",
    "session_id": "demo_help_001",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Response:**
```json
{
  "response": "I'm here to help you build and manage entities! Here's what I can do:\n\n**Entity Extraction:**\n- \"Extract entities from my credit domain fields\"\n- \"Find entities in my asset columns\"\n- \"Identify business entities from the data\"\n\n**Entity Creation:**\n- \"Create a customer entity with name and email attributes\"\n- \"Build a credit account entity\"\n- \"Make a transaction entity\"\n\n**Entity Management:**\n- \"List all my entities\"\n- \"Show me what entities I have\"\n- \"Delete the Customer Profile entity\"\n- \"Remove entity_abc123\"\n\n**Relationship Management:**\n- \"Show me relationships between entities\"\n- \"How are my entities connected?\"\n- \"Analyze entity relationships\"\n\n**Data Context:**\n- You can provide credit domain fields and asset columns, and I'll use them for extraction\n- I remember our conversation context throughout the session\n- I automatically detect relationships between entities\n\nJust tell me what you'd like to do in natural language!",
  "success": true,
  "entities_created": 0,
  "entities": []
}
```

#### List Entities Through Conversation
```bash
curl -X POST "http://localhost:8000/conversation?user_id=demo_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "List all my entities",
    "session_id": "demo_list_001",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Response:**
```json
{
  "response": "No entities found in this session.",
  "success": true,
  "entities_created": 0,
  "entities": []
}
```

#### Extract Entities with Data Context
```bash
curl -X POST "http://localhost:8000/conversation?user_id=demo_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Extract entities from my credit domain fields and asset columns",
    "session_id": "demo_extract_001",
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
      }
    ]
  }'
```

#### Get Conversation History
```bash
curl "http://localhost:8000/conversation/demo_extract_001/history?user_id=demo_user"
```

**Response:**
```json
{
  "session_id": "demo_extract_001",
  "user_id": "demo_user",
  "messages": [
    {
      "role": "user",
      "content": "Extract entities from my credit domain fields and asset columns",
      "timestamp": "2025-09-11T20:07:17.866293+00:00"
    },
    {
      "role": "assistant",
      "content": "Successfully extracted 2 entities: Credit Account, Customer Profile",
      "timestamp": "2025-09-11T20:07:17.867212+00:00"
    }
  ],
  "total_messages": 2
}
```

#### Get Session Summary
```bash
curl "http://localhost:8000/conversation/demo_extract_001/summary?user_id=demo_user"
```

**Response:**
```json
{
  "session_id": "demo_extract_001",
  "thread_id": "thread_demo_user_demo_extract_001",
  "message_count": 2,
  "entities_created_count": 2,
  "has_credit_domain_fields": true,
  "has_asset_columns": true,
  "current_intent": "extract_entities",
  "last_activity": "2025-09-11T20:07:17.867212+00:00",
  "status": "completed"
}
```

### Traditional Chat Endpoint Examples

#### Basic Entity Extraction
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Extract entities from the credit domain fields and create meaningful business entities",
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

#### Comprehensive Entity Extraction
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Extract entities from the credit domain fields and create meaningful business entities",
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

### CRUD Operations Examples

#### Create Entity
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
      },
      {
        "attribute_name": "Email",
        "attribute_value": "john.doe@example.com",
        "attribute_type": "string",
        "description": "Customer email address"
      },
      {
        "attribute_name": "Phone",
        "attribute_value": "+1-555-123-4567",
        "attribute_type": "string",
        "description": "Customer phone number"
      }
    ]
  }'
```

#### Read Entities
```bash
curl "http://localhost:8000/entities?session_id=test_crud_001"
```

**Response:**
```json
{
  "success": true,
  "message": "Entities retrieved successfully",
  "entities": [
    {
      "entity_id": "entity_990434f1",
      "session_id": "test_crud_001",
      "entity_type": "business_metric",
      "entity_name": "Customer Profile",
      "entity_value": "Customer profile information",
      "description": "A comprehensive customer profile with personal and financial information",
      "created_at": "2025-09-11T20:00:00.000Z",
      "updated_at": "2025-09-11T20:00:00.000Z",
      "attributes": [
        {
          "attribute_id": "attr_b0caf65a",
          "attribute_name": "Customer Name",
          "attribute_value": "John Doe",
          "attribute_type": "string",
          "description": "Full name of the customer",
          "created_at": "2025-09-11T20:00:00.000Z"
        },
        {
          "attribute_id": "attr_c1dbe76b",
          "attribute_name": "Age",
          "attribute_value": "35",
          "attribute_type": "numeric",
          "description": "Age of the customer",
          "created_at": "2025-09-11T20:00:00.000Z"
        }
      ]
    }
  ],
  "total_count": 1
}
```

#### Update Entity
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

#### Delete Entity
```bash
curl -X DELETE "http://localhost:8000/entities" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_crud_001",
    "entity_id": "entity_990434f1"
  }'
```

#### Read Attributes
```bash
curl "http://localhost:8000/entities/entity_990434f1/attributes?session_id=test_crud_001"
```

#### Delete Attribute
```bash
curl -X DELETE "http://localhost:8000/entities/entity_990434f1/attributes/attr_b0caf65a" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test_crud_001",
    "entity_id": "entity_990434f1",
    "attribute_id": "attr_b0caf65a"
  }'
```

## 🎯 Natural Language Entity Creation Examples

The system excels at creating sophisticated business entities from natural language descriptions. Here are comprehensive examples showcasing different business scenarios:

### 1. **Fraud Detection System** 🛡️
```bash
curl -X POST "http://localhost:8000/conversation?user_id=fraud_detection_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a fraud detection system that monitors suspicious transactions and customer behavior patterns",
    "session_id": "fraud_detection_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Fraud Alert Entity**: Alert ID, transaction ID, customer ID, risk score, reason code, status
- **Customer Behavior Profile Entity**: Customer ID, risk score, transaction patterns, common locations

### 2. **Credit Risk Assessment** 💳
```bash
curl -X POST "http://localhost:8000/conversation?user_id=credit_risk_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a comprehensive credit risk assessment system that evaluates borrower creditworthiness and loan approval decisions",
    "session_id": "credit_risk_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Credit Application Entity**: Application ID, borrower info, loan amount, purpose, income
- **Risk Assessment Entity**: Credit score, debt-to-income ratio, employment history, collateral value
- **Loan Decision Entity**: Decision status, approval amount, interest rate, terms, conditions

### 3. **Customer Onboarding System** 👥
```bash
curl -X POST "http://localhost:8000/conversation?user_id=onboarding_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a digital customer onboarding system that handles KYC verification, document collection, and account setup",
    "session_id": "onboarding_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Customer Profile Entity**: Personal info, contact details, identification documents
- **KYC Verification Entity**: Document status, verification results, compliance checks
- **Account Setup Entity**: Account type, initial settings, service preferences

### 4. **Investment Portfolio Management** 📈
```bash
curl -X POST "http://localhost:8000/conversation?user_id=portfolio_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for an investment portfolio management system that tracks assets, performance metrics, and rebalancing strategies",
    "session_id": "portfolio_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Portfolio Entity**: Portfolio ID, owner, total value, risk profile, investment strategy
- **Asset Entity**: Asset ID, type, current value, purchase price, performance metrics
- **Rebalancing Rule Entity**: Trigger conditions, target allocations, rebalancing frequency

### 5. **Insurance Claims Processing** 🏥
```bash
curl -X POST "http://localhost:8000/conversation?user_id=insurance_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for an insurance claims processing system that handles claim submission, investigation, and settlement",
    "session_id": "insurance_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Insurance Claim Entity**: Claim ID, policy number, incident details, claim amount
- **Investigation Entity**: Investigator ID, findings, evidence, recommendation
- **Settlement Entity**: Settlement amount, payment method, approval status, timeline

### 6. **Supply Chain Management** 🚚
```bash
curl -X POST "http://localhost:8000/conversation?user_id=supply_chain_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a supply chain management system that tracks inventory, suppliers, orders, and logistics",
    "session_id": "supply_chain_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Inventory Entity**: Product ID, quantity, location, reorder level, supplier info
- **Purchase Order Entity**: Order ID, supplier, items, quantities, delivery date
- **Logistics Entity**: Shipment ID, route, carrier, tracking info, delivery status

### 7. **Healthcare Patient Management** 🏥
```bash
curl -X POST "http://localhost:8000/conversation?user_id=healthcare_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a healthcare patient management system that handles patient records, appointments, and treatment plans",
    "session_id": "healthcare_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Patient Entity**: Patient ID, demographics, medical history, insurance info
- **Appointment Entity**: Appointment ID, patient, provider, date/time, type, status
- **Treatment Plan Entity**: Plan ID, patient, diagnosis, medications, follow-up schedule

### 8. **E-commerce Order Management** 🛒
```bash
curl -X POST "http://localhost:8000/conversation?user_id=ecommerce_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for an e-commerce order management system that handles product catalog, shopping cart, and order fulfillment",
    "session_id": "ecommerce_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Product Entity**: Product ID, name, description, price, inventory, category
- **Shopping Cart Entity**: Cart ID, customer, items, quantities, total amount
- **Order Entity**: Order ID, customer, items, shipping address, payment status

### 9. **Real Estate Property Management** 🏠
```bash
curl -X POST "http://localhost:8000/conversation?user_id=real_estate_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a real estate property management system that handles property listings, tenant management, and lease agreements",
    "session_id": "real_estate_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Property Entity**: Property ID, address, type, size, amenities, market value
- **Tenant Entity**: Tenant ID, personal info, rental history, payment status
- **Lease Agreement Entity**: Lease ID, property, tenant, terms, rent amount, duration

### 10. **Banking Transaction Monitoring** 🏦
```bash
curl -X POST "http://localhost:8000/conversation?user_id=banking_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a banking transaction monitoring system that tracks account activity, compliance, and regulatory reporting",
    "session_id": "banking_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Bank Account Entity**: Account number, type, balance, owner, status, opening date
- **Transaction Entity**: Transaction ID, account, amount, type, timestamp, description
- **Compliance Report Entity**: Report ID, period, account, transaction count, flagged items

### 11. **Manufacturing Quality Control** 🏭
```bash
curl -X POST "http://localhost:8000/conversation?user_id=manufacturing_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for a manufacturing quality control system that monitors production lines, quality metrics, and defect tracking",
    "session_id": "manufacturing_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Production Line Entity**: Line ID, product type, capacity, current status, efficiency
- **Quality Check Entity**: Check ID, product batch, test results, inspector, timestamp
- **Defect Report Entity**: Defect ID, product, severity, cause, corrective action

### 12. **Energy Grid Management** ⚡
```bash
curl -X POST "http://localhost:8000/conversation?user_id=energy_user" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Create entities for an energy grid management system that monitors power generation, distribution, and consumption patterns",
    "session_id": "energy_session",
    "selected_credit_domain_fields": [],
    "selected_asset_columns": []
  }'
```

**Creates:**
- **Power Plant Entity**: Plant ID, type, capacity, location, operational status
- **Grid Node Entity**: Node ID, location, voltage level, load capacity, connections
- **Energy Consumption Entity**: Consumer ID, usage pattern, peak demand, billing cycle

### 🎯 **Key Benefits of Natural Language Entity Creation:**

1. **Business Context Understanding**: The AI understands complex business scenarios and creates relevant entities
2. **Automatic Relationship Detection**: Entities are created with built-in relationships and shared attributes
3. **Comprehensive Attribute Modeling**: Each entity includes detailed attributes with proper data types
4. **Domain-Specific Intelligence**: The system adapts to different industries and use cases
5. **Scalable Entity Design**: Creates multiple interconnected entities that work together
6. **Real-World Applicability**: Entities are designed for actual business implementation

### 🔧 **Technical Implementation:**

- **Intent Recognition**: Automatically detects "natural_language_entity" intent
- **LLM Processing**: Uses advanced prompts to generate structured entity data
- **JSON Parsing**: Robust parsing with markdown cleanup and error handling
- **Entity Creation**: Seamless integration with Firestore storage
- **Relationship Analysis**: Automatic detection of entity relationships
- **Conversation Context**: Maintains full conversation history and context

## Frontend Integration Guide

### React/JavaScript Integration

#### 1. Basic Chat Component

```jsx
import React, { useState, useEffect } from 'react';

const ChatComponent = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId] = useState(`session_${Date.now()}`);
  const [userId] = useState('frontend_user');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async (message) => {
    setIsLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/conversation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
          selected_credit_domain_fields: [],
          selected_asset_columns: []
        })
      });

      const data = await response.json();
      
      setMessages(prev => [
        ...prev,
        { role: 'user', content: message },
        { role: 'assistant', content: data.response }
      ]);
      
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputMessage.trim()) {
      sendMessage(inputMessage);
      setInputMessage('');
    }
  };

  return (
    <div className="chat-container">
      <div className="messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
            <div>{msg.content}</div>
          </div>
        ))}
        {isLoading && <div className="loading">AI is typing...</div>}
      </div>
      
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          placeholder="Ask me to help with entity extraction..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatComponent;
```

#### 2. Advanced Chat with Data Context

```jsx
import React, { useState, useEffect } from 'react';

const AdvancedChatComponent = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId] = useState(`session_${Date.now()}`);
  const [userId] = useState('frontend_user');
  const [creditDomainFields, setCreditDomainFields] = useState([]);
  const [assetColumns, setAssetColumns] = useState([]);
  const [conversationHistory, setConversationHistory] = useState([]);

  // Load conversation history on component mount
  useEffect(() => {
    loadConversationHistory();
  }, []);

  const loadConversationHistory = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/conversation/${sessionId}/history?user_id=${userId}`
      );
      const data = await response.json();
      setConversationHistory(data.messages);
    } catch (error) {
      console.error('Error loading conversation history:', error);
    }
  };

  const sendMessage = async (message) => {
    try {
      const response = await fetch(`http://localhost:8000/conversation?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: sessionId,
          selected_credit_domain_fields: creditDomainFields,
          selected_asset_columns: assetColumns
        })
      });

      const data = await response.json();
      
      setMessages(prev => [
        ...prev,
        { role: 'user', content: message },
        { 
          role: 'assistant', 
          content: data.response,
          entities_created: data.entities_created,
          entities: data.entities
        }
      ]);
      
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const addCreditDomainField = (field) => {
    setCreditDomainFields(prev => [...prev, field]);
  };

  const addAssetColumn = (column) => {
    setAssetColumns(prev => [...prev, column]);
  };

  return (
    <div className="advanced-chat-container">
      <div className="data-context">
        <h3>Credit Domain Fields ({creditDomainFields.length})</h3>
        <div className="fields-list">
          {creditDomainFields.map((field, index) => (
            <div key={index} className="field-item">
              {field.field.field_name} - {field.field.description}
            </div>
          ))}
        </div>
        
        <h3>Asset Columns ({assetColumns.length})</h3>
        <div className="columns-list">
          {assetColumns.map((column, index) => (
            <div key={index} className="column-item">
              {column.column_name} - {column.description}
            </div>
          ))}
        </div>
      </div>

      <div className="chat-section">
        <div className="messages">
          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <strong>{msg.role === 'user' ? 'You' : 'AI'}:</strong>
              <div>{msg.content}</div>
              {msg.entities_created > 0 && (
                <div className="entities-info">
                  Created {msg.entities_created} entities
                </div>
              )}
            </div>
          ))}
        </div>
        
        <form onSubmit={(e) => {
          e.preventDefault();
          if (inputMessage.trim()) {
            sendMessage(inputMessage);
            setInputMessage('');
          }
        }}>
          <input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            placeholder="Ask me to help with entity extraction..."
          />
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
};

export default AdvancedChatComponent;
```

#### 3. Entity Management Component

```jsx
import React, { useState, useEffect } from 'react';

const EntityManagementComponent = () => {
  const [entities, setEntities] = useState([]);
  const [sessionId] = useState(`session_${Date.now()}`);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadEntities();
  }, []);

  const loadEntities = async () => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/entities?session_id=${sessionId}`);
      const data = await response.json();
      setEntities(data.entities || []);
    } catch (error) {
      console.error('Error loading entities:', error);
    } finally {
      setLoading(false);
    }
  };

  const createEntity = async (entityData) => {
    try {
      const response = await fetch('http://localhost:8000/entities', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          ...entityData
        })
      });

      const data = await response.json();
      if (data.success) {
        loadEntities(); // Reload entities
      }
    } catch (error) {
      console.error('Error creating entity:', error);
    }
  };

  const deleteEntity = async (entityId) => {
    try {
      const response = await fetch('http://localhost:8000/entities', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          entity_id: entityId
        })
      });

      const data = await response.json();
      if (data.success) {
        loadEntities(); // Reload entities
      }
    } catch (error) {
      console.error('Error deleting entity:', error);
    }
  };

  return (
    <div className="entity-management">
      <h2>Entity Management</h2>
      
      {loading ? (
        <div>Loading entities...</div>
      ) : (
        <div className="entities-list">
          {entities.map((entity) => (
            <div key={entity.entity_id} className="entity-card">
              <h3>{entity.entity_name}</h3>
              <p>{entity.description}</p>
              <div className="attributes">
                {entity.attributes?.map((attr) => (
                  <div key={attr.attribute_id} className="attribute">
                    <strong>{attr.attribute_name}:</strong> {attr.attribute_value}
                  </div>
                ))}
              </div>
              <button onClick={() => deleteEntity(entity.entity_id)}>
                Delete Entity
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EntityManagementComponent;
```

### Vue.js Integration

#### 1. Vue Chat Component

```vue
<template>
  <div class="chat-container">
    <div class="messages">
      <div 
        v-for="(message, index) in messages" 
        :key="index" 
        :class="['message', message.role]"
      >
        <strong>{{ message.role === 'user' ? 'You' : 'AI' }}:</strong>
        <div>{{ message.content }}</div>
      </div>
      <div v-if="isLoading" class="loading">AI is typing...</div>
    </div>
    
    <form @submit.prevent="sendMessage">
      <input
        v-model="inputMessage"
        type="text"
        placeholder="Ask me to help with entity extraction..."
        :disabled="isLoading"
      />
      <button type="submit" :disabled="isLoading">
        Send
      </button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'ChatComponent',
  data() {
    return {
      messages: [],
      inputMessage: '',
      sessionId: `session_${Date.now()}`,
      userId: 'frontend_user',
      isLoading: false
    }
  },
  methods: {
    async sendMessage() {
      if (!this.inputMessage.trim()) return;
      
      this.isLoading = true;
      
      try {
        const response = await fetch('http://localhost:8000/conversation', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: this.inputMessage,
            session_id: this.sessionId,
            selected_credit_domain_fields: [],
            selected_asset_columns: []
          })
        });

        const data = await response.json();
        
        this.messages.push(
          { role: 'user', content: this.inputMessage },
          { role: 'assistant', content: data.response }
        );
        
        this.inputMessage = '';
      } catch (error) {
        console.error('Error sending message:', error);
      } finally {
        this.isLoading = false;
      }
    }
  }
}
</script>
```

### Angular Integration

#### 1. Angular Service

```typescript
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) { }

  sendMessage(message: string, sessionId: string, userId: string = 'frontend_user'): Observable<any> {
    return this.http.post(`${this.baseUrl}/conversation`, {
      message,
      session_id: sessionId,
      selected_bc3_fields: [],
      selected_asset_columns: []
    }, {
      params: { user_id: userId }
    });
  }

  getConversationHistory(sessionId: string, userId: string = 'frontend_user'): Observable<any> {
    return this.http.get(`${this.baseUrl}/conversation/${sessionId}/history`, {
      params: { user_id: userId }
    });
  }

  getSessionSummary(sessionId: string, userId: string = 'frontend_user'): Observable<any> {
    return this.http.get(`${this.baseUrl}/conversation/${sessionId}/summary`, {
      params: { user_id: userId }
    });
  }

  getEntities(sessionId: string): Observable<any> {
    return this.http.get(`${this.baseUrl}/entities`, {
      params: { session_id: sessionId }
    });
  }

  createEntity(entityData: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/entities`, entityData);
  }

  deleteEntity(sessionId: string, entityId: string): Observable<any> {
    return this.http.delete(`${this.baseUrl}/entities`, {
      body: {
        session_id: sessionId,
        entity_id: entityId
      }
    });
  }
}
```

#### 2. Angular Component

```typescript
import { Component, OnInit } from '@angular/core';
import { ChatService } from './chat.service';

@Component({
  selector: 'app-chat',
  template: `
    <div class="chat-container">
      <div class="messages">
        <div 
          *ngFor="let message of messages; let i = index" 
          [class]="'message ' + message.role"
        >
          <strong>{{ message.role === 'user' ? 'You' : 'AI' }}:</strong>
          <div>{{ message.content }}</div>
        </div>
        <div *ngIf="isLoading" class="loading">AI is typing...</div>
      </div>
      
      <form (ngSubmit)="sendMessage()">
        <input
          [(ngModel)]="inputMessage"
          name="inputMessage"
          type="text"
          placeholder="Ask me to help with entity extraction..."
          [disabled]="isLoading"
        />
        <button type="submit" [disabled]="isLoading">
          Send
        </button>
      </form>
    </div>
  `
})
export class ChatComponent implements OnInit {
  messages: any[] = [];
  inputMessage: string = '';
  sessionId: string = `session_${Date.now()}`;
  isLoading: boolean = false;

  constructor(private chatService: ChatService) { }

  ngOnInit() {
    this.loadConversationHistory();
  }

  loadConversationHistory() {
    this.chatService.getConversationHistory(this.sessionId).subscribe(
      (data) => {
        this.messages = data.messages || [];
      },
      (error) => {
        console.error('Error loading conversation history:', error);
      }
    );
  }

  sendMessage() {
    if (!this.inputMessage.trim()) return;
    
    this.isLoading = true;
    
    this.chatService.sendMessage(this.inputMessage, this.sessionId).subscribe(
      (data) => {
        this.messages.push(
          { role: 'user', content: this.inputMessage },
          { role: 'assistant', content: data.response }
        );
        this.inputMessage = '';
      },
      (error) => {
        console.error('Error sending message:', error);
      },
      () => {
        this.isLoading = false;
      }
    );
  }
}
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

## LangGraph Architecture Benefits

### What LangGraph Brings to the Table:

1. **Advanced State Management**: Automatic conversation state persistence with thread-based sessions
2. **Intent-Based Routing**: Smart routing based on user intent analysis with conversation context
3. **Message Accumulation**: Automatic conversation history management with proper message types
4. **Tool Integration**: Seamless tool execution with proper error handling and state updates
5. **Workflow Orchestration**: Clean separation of concerns with nodes for different processing stages
6. **Fault Tolerance**: Built-in error recovery and state management
7. **Scalability**: Easy to extend with new nodes, tools, and routing logic

### LangGraph Workflow:

```
START → Message Processing → Intent Analysis → [Tool Execution | Relationship Analysis | Response Generation] → END
```

Each node in the workflow has a specific responsibility:
- **Message Processing**: Handles incoming user messages and context updates
- **Intent Analysis**: Analyzes user intent with conversation context
- **Tool Execution**: Executes appropriate tools based on intent
- **Relationship Analysis**: Analyzes relationships between entities
- **Response Generation**: Generates final responses with proper message handling

## Current Status

✅ **LangGraph Integration**: Complete state management with conversation persistence
✅ **Conversational Interface**: Natural language entity building with full context awareness
✅ **Natural Language Entity Creation**: Sophisticated business entity creation from natural language
✅ **Session Management**: Persistent conversation history with thread-based sessions
✅ **Intent Recognition**: Understands user commands with conversation context
✅ **Modular Architecture**: Clean separation with managers/ and services/ packages
✅ **Fully Functional**: All CRUD operations working with enhanced state management
✅ **Database Integration**: Using llmops-demo-track2 database
✅ **Configuration Constants**: No hardcoded values
✅ **Relationship Detection**: Automatic entity relationship analysis
✅ **Tested**: Comprehensive test coverage with 4 scenarios (Credit Domain only, Asset only, Combined, Natural Language)
✅ **Documented**: Complete API documentation with frontend integration and 12+ natural language examples
✅ **Production Ready**: Stable and reliable with advanced state management

## Key Innovations

1. **LangGraph State Management**: Advanced conversation state persistence with automatic message accumulation
2. **Natural Language Entity Creation**: Sophisticated business entity creation from natural language descriptions
3. **Conversational Entity Building**: Users can build entities through natural language with full context awareness
4. **Modular Architecture**: Clean separation with managers/ and services/ packages for better maintainability
5. **Intent Recognition with Context**: AI understands what users want to do with conversation history
6. **Session Persistence**: Maintains conversation context and history with thread-based sessions
7. **Dual Interface**: Both conversational and traditional API endpoints with enhanced capabilities
8. **Configuration Management**: Centralized, environment-variable driven
9. **Database Isolation**: Dedicated database for entity storage
10. **Frontend Integration**: Comprehensive examples for React, Vue.js, and Angular
11. **Tool Orchestration**: Seamless tool execution with proper state management
12. **Workflow Architecture**: Clean separation of concerns with LangGraph nodes and edges
13. **Relationship Detection**: Automatic detection and analysis of entity relationships
14. **Multi-Domain Support**: Handles diverse business scenarios from fraud detection to healthcare