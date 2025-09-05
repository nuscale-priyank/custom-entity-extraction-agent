# Entity Management System Documentation

## Overview

The Entity Management System provides comprehensive CRUD (Create, Read, Update, Delete) operations for entities and their attributes. Each entity can have multiple attributes with unique IDs, and the system includes automatic state versioning and timestamp tracking.

## Key Features

- **Entities with Attributes**: Each entity can have multiple attributes with unique IDs
- **State Versioning**: Automatic state version incrementing for tracking changes
- **Timestamp Tracking**: Created/updated timestamps for all entities and attributes
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **Agent Integration**: LLM can perform CRUD operations via LangChain tools
- **Firestore Persistence**: All data is persisted in Firestore with state management

## Entity Structure

### Entity Model
```json
{
  "entity_id": "entity_12345678",
  "entity_type": "field|business_metric|relationship|derived_insight|operational_rule",
  "entity_name": "Entity Name",
  "entity_value": "Entity Value",
  "confidence": 0.95,
  "source_field": "Source field name",
  "description": "Entity description",
  "relationships": {
    "influences": "Related Entity",
    "correlates_with": "Another Entity"
  },
  "context_provider": "credit_domain",
  "attributes": [
    {
      "attribute_id": "attr_87654321",
      "attribute_name": "Attribute Name",
      "attribute_value": "Attribute Value",
      "attribute_type": "string|number|boolean|object",
      "confidence": 0.9,
      "source_field": "Source field for attribute",
      "description": "Attribute description",
      "created_at": "2025-09-05T13:34:48.233424Z",
      "updated_at": "2025-09-05T13:34:48.233425Z",
      "metadata": {}
    }
  ],
  "created_at": "2025-09-05T13:34:48.233185Z",
  "updated_at": "2025-09-05T13:34:48.233456Z",
  "state_version": 2,
  "metadata": {}
}
```

### Attribute Model
```json
{
  "attribute_id": "attr_87654321",
  "attribute_name": "Attribute Name",
  "attribute_value": "Attribute Value",
  "attribute_type": "string|number|boolean|object",
  "confidence": 0.9,
  "source_field": "Source field for attribute",
  "description": "Attribute description",
  "created_at": "2025-09-05T13:34:48.233424Z",
  "updated_at": "2025-09-05T13:34:48.233425Z",
  "metadata": {}
}
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

## 1. Read Entities

### Endpoint
```
POST /entities/read
```

### Description
Read entities from a session with optional filtering by entity ID, type, or state version.

### Request Payload
```json
{
  "session_id": "string (required)",
  "entity_id": "string (optional) - Specific entity ID to read",
  "entity_type": "string (optional) - Filter by entity type",
  "include_attributes": "boolean (optional, default: true) - Include entity attributes",
  "state_version": "integer (optional) - Specific state version to read"
}
```

### Examples

#### Read All Entities
```bash
curl -X POST "http://localhost:8000/entities/read" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "include_attributes": true
  }'
```

#### Read Specific Entity
```bash
curl -X POST "http://localhost:8000/entities/read" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "entity_id": "entity_12345678",
    "include_attributes": true
  }'
```

#### Read Entities by Type
```bash
curl -X POST "http://localhost:8000/entities/read" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "entity_type": "field",
    "include_attributes": true
  }'
```

#### Read Entities from Specific State Version
```bash
curl -X POST "http://localhost:8000/entities/read" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "state_version": 3,
    "include_attributes": true
  }'
```

### Response
```json
{
  "entities": [
    {
      "entity_id": "entity_12345678",
      "entity_type": "field",
      "entity_name": "Account Number",
      "entity_value": "account_number",
      "confidence": 0.95,
      "source_field": "Account Number (Credit Accounts)",
      "description": "Unique identifier for credit account",
      "relationships": {},
      "context_provider": "credit_domain",
      "attributes": [
        {
          "attribute_id": "attr_87654321",
          "attribute_name": "implementation",
          "attribute_value": "account_number",
          "attribute_type": "string",
          "confidence": 0.95,
          "source_field": "known_implementations",
          "description": "Known implementation name",
          "created_at": "2025-09-05T13:34:48.233424Z",
          "updated_at": "2025-09-05T13:34:48.233425Z",
          "metadata": {}
        }
      ],
      "created_at": "2025-09-05T13:34:48.233185Z",
      "updated_at": "2025-09-05T13:34:48.233456Z",
      "state_version": 2,
      "metadata": {}
    }
  ],
  "state_version": 2,
  "total_count": 1,
  "success": true,
  "message": "Successfully retrieved 1 entities"
}
```

## 2. Update Entities

### Endpoint
```
POST /entities/update
```

### Description
Update entities or their attributes. If the entity doesn't exist, it will be created.

### Request Payload
```json
{
  "session_id": "string (required)",
  "entity_id": "string (required)",
  "entity_updates": {
    "entity_name": "string (optional)",
    "entity_value": "string (optional)",
    "description": "string (optional)",
    "entity_type": "string (optional)",
    "confidence": "number (optional)",
    "source_field": "string (optional)",
    "relationships": "object (optional)",
    "metadata": "object (optional)"
  },
  "attribute_updates": [
    {
      "attribute_id": "string (optional) - If not provided, creates new attribute",
      "attribute_name": "string (required for new attributes)",
      "attribute_value": "any (required for new attributes)",
      "attribute_type": "string (optional, default: string)",
      "confidence": "number (optional, default: 0.8)",
      "source_field": "string (optional)",
      "description": "string (optional)",
      "metadata": "object (optional)"
    }
  ]
}
```

### Examples

#### Create New Entity with Attributes
```bash
curl -X POST "http://localhost:8000/entities/update" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "entity_id": "entity_credit_score",
    "entity_updates": {
      "entity_name": "Credit Score",
      "entity_value": "credit_score",
      "description": "Numerical representation of creditworthiness",
      "entity_type": "business_metric",
      "confidence": 0.95,
      "source_field": "Credit Score (Consumer Database)"
    },
    "attribute_updates": [
      {
        "attribute_name": "score_range",
        "attribute_value": "300-850",
        "attribute_type": "string",
        "confidence": 0.9,
        "source_field": "score_range",
        "description": "Valid credit score range"
      },
      {
        "attribute_name": "risk_level",
        "attribute_value": "low|medium|high",
        "attribute_type": "string",
        "confidence": 0.85,
        "source_field": "risk_assessment",
        "description": "Risk level classification"
      }
    ]
  }'
```

#### Update Existing Entity Fields
```bash
curl -X POST "http://localhost:8000/entities/update" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "entity_id": "entity_credit_score",
    "entity_updates": {
      "description": "Updated description for credit score entity",
      "confidence": 0.98
    }
  }'
```

#### Add New Attribute to Existing Entity
```bash
curl -X POST "http://localhost:8000/entities/update" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "entity_id": "entity_credit_score",
    "attribute_updates": [
      {
        "attribute_name": "calculation_method",
        "attribute_value": "FICO",
        "attribute_type": "string",
        "confidence": 0.9,
        "source_field": "calculation_method",
        "description": "Method used to calculate credit score"
      }
    ]
  }'
```

#### Update Existing Attribute
```bash
curl -X POST "http://localhost:8000/entities/update" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "entity_id": "entity_credit_score",
    "attribute_updates": [
      {
        "attribute_id": "attr_87654321",
        "attribute_value": "300-900",
        "confidence": 0.95,
        "description": "Updated credit score range"
      }
    ]
  }'
```

### Response
```json
{
  "updated_entity": {
    "entity_id": "entity_credit_score",
    "entity_type": "business_metric",
    "entity_name": "Credit Score",
    "entity_value": "credit_score",
    "confidence": 0.98,
    "source_field": "Credit Score (Consumer Database)",
    "description": "Updated description for credit score entity",
    "relationships": {},
    "context_provider": "credit_domain",
    "attributes": [
      {
        "attribute_id": "attr_87654321",
        "attribute_name": "score_range",
        "attribute_value": "300-900",
        "attribute_type": "string",
        "confidence": 0.95,
        "source_field": "score_range",
        "description": "Updated credit score range",
        "created_at": "2025-09-05T13:34:48.233424Z",
        "updated_at": "2025-09-05T13:35:00.123456Z",
        "metadata": {}
      }
    ],
    "created_at": "2025-09-05T13:34:48.233185Z",
    "updated_at": "2025-09-05T13:35:00.123456Z",
    "state_version": 3,
    "metadata": {}
  },
  "state_version": 3,
  "success": true,
  "message": "Successfully updated entity entity_credit_score"
}
```

## 3. Delete Entities

### Endpoint
```
POST /entities/delete
```

### Description
Delete entities or specific attributes from a session.

### Request Payload
```json
{
  "session_id": "string (required)",
  "entity_id": "string (optional) - Delete specific entity",
  "attribute_ids": ["string"] (optional) - Delete specific attributes by ID,
  "delete_all": "boolean (optional, default: false) - Delete all entities in session"
}
```

### Examples

#### Delete Specific Entity
```bash
curl -X POST "http://localhost:8000/entities/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "entity_id": "entity_credit_score"
  }'
```

#### Delete Specific Attributes
```bash
curl -X POST "http://localhost:8000/entities/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "attribute_ids": ["attr_87654321", "attr_12345678"]
  }'
```

#### Delete All Entities in Session
```bash
curl -X POST "http://localhost:8000/entities/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session_123",
    "delete_all": true
  }'
```

### Response
```json
{
  "deleted_entities": ["entity_credit_score"],
  "deleted_attributes": [],
  "state_version": 4,
  "success": true,
  "message": "Successfully deleted 1 entities and 0 attributes"
}
```

## State Management

### State Versioning
- Each operation increments the session's state version
- Entities track their own state version changes
- You can read entities from specific state versions
- State versions help track changes over time

### Timestamp Tracking
- `created_at`: When the entity/attribute was first created
- `updated_at`: When the entity/attribute was last modified
- All timestamps are in ISO 8601 format

## Entity Types

The system supports the following entity types:

- `field` - Data fields from BC3 segments
- `segment` - Credit domain segments
- `value` - Valid values for fields
- `metadata` - Additional metadata
- `document` - Document entities
- `object` - Object entities
- `array` - Array entities
- `asset` - Data assets
- `column` - Asset columns
- `business_metric` - Business metrics
- `relationship` - Entity relationships
- `derived_insight` - Derived insights
- `operational_rule` - Operational rules

## Attribute Types

Attributes can be of the following types:

- `string` - Text values
- `number` - Numeric values
- `boolean` - True/false values
- `object` - Complex objects

## Error Handling

### Common Error Responses

#### Session Not Found
```json
{
  "entities": [],
  "state_version": 0,
  "total_count": 0,
  "success": false,
  "message": "Session my_session_123 not found"
}
```

#### Entity Not Found
```json
{
  "updated_entity": null,
  "state_version": 1,
  "success": false,
  "message": "Entity entity_nonexistent not found"
}
```

#### Invalid Entity Type
```json
{
  "success": false,
  "message": "Invalid entity type: invalid_type. Valid types: ['field', 'segment', 'value', 'metadata', 'document', 'object', 'array', 'asset', 'column', 'business_metric', 'relationship', 'derived_insight', 'operational_rule']"
}
```

## Agent Integration

The LLM agent can also perform CRUD operations using the following tools:

### Available Agent Tools

1. **`read_entities`** - Read entities with filtering
2. **`delete_entities`** - Delete entities or attributes
3. **`update_entities`** - Update entities or attributes

### Example Agent Usage

```json
{
  "message": "Please create a Credit Score entity with score range and risk level attributes, then read it back to me",
  "session_id": "agent_session_123",
  "tools_enabled": true
}
```

The agent will automatically use the appropriate tools to perform the requested operations.

## Best Practices

1. **Use Descriptive Entity Names**: Choose clear, descriptive names for entities
2. **Include Attributes**: Add relevant attributes to provide more context
3. **Set Appropriate Confidence Scores**: Use confidence scores to indicate reliability
4. **Use State Versioning**: Track changes using state versions
5. **Handle Errors Gracefully**: Always check the `success` field in responses
6. **Use Unique IDs**: Ensure entity and attribute IDs are unique within a session

## Performance Notes

- All operations are atomic and consistent
- State versions are automatically incremented
- Firestore provides persistent storage with automatic backups
- Operations are optimized for concurrent access
- Large numbers of attributes per entity are supported

## Security Considerations

- All operations are scoped to specific sessions
- No cross-session data access
- Input validation on all fields
- Automatic sanitization of user inputs
- Audit trail through state versioning and timestamps
