# Entity Management - Quick Reference Guide

## 🚀 Quick Start Examples

### 1. Create Entity with Attributes
```bash
curl -X POST "http://localhost:8000/entities/update" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session",
    "entity_id": "credit_score_001",
    "entity_updates": {
      "entity_name": "Credit Score",
      "entity_type": "business_metric",
      "description": "Customer credit score"
    },
    "attribute_updates": [
      {
        "attribute_name": "score_value",
        "attribute_value": "750",
        "attribute_type": "number"
      },
      {
        "attribute_name": "risk_level",
        "attribute_value": "low",
        "attribute_type": "string"
      }
    ]
  }'
```

### 2. Read All Entities
```bash
curl -X POST "http://localhost:8000/entities/read" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session",
    "include_attributes": true
  }'
```

### 3. Update Entity
```bash
curl -X POST "http://localhost:8000/entities/update" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session",
    "entity_id": "credit_score_001",
    "entity_updates": {
      "description": "Updated credit score description"
    }
  }'
```

### 4. Delete Specific Attributes
```bash
curl -X POST "http://localhost:8000/entities/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session",
    "attribute_ids": ["attr_123", "attr_456"]
  }'
```

### 5. Delete Entire Entity
```bash
curl -X POST "http://localhost:8000/entities/delete" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "my_session",
    "entity_id": "credit_score_001"
  }'
```

## 📋 Common Patterns

### Filter by Entity Type
```json
{
  "session_id": "my_session",
  "entity_type": "field",
  "include_attributes": true
}
```

### Read Specific Entity
```json
{
  "session_id": "my_session",
  "entity_id": "entity_123",
  "include_attributes": true
}
```

### Add New Attribute
```json
{
  "session_id": "my_session",
  "entity_id": "entity_123",
  "attribute_updates": [
    {
      "attribute_name": "new_attribute",
      "attribute_value": "new_value",
      "attribute_type": "string"
    }
  ]
}
```

### Update Existing Attribute
```json
{
  "session_id": "my_session",
  "entity_id": "entity_123",
  "attribute_updates": [
    {
      "attribute_id": "attr_456",
      "attribute_value": "updated_value"
    }
  ]
}
```

## 🔧 Entity Types
- `field` - Data fields
- `business_metric` - Business metrics
- `relationship` - Entity relationships
- `derived_insight` - Derived insights
- `operational_rule` - Operational rules

## 📊 Attribute Types
- `string` - Text values
- `number` - Numeric values
- `boolean` - True/false
- `object` - Complex objects

## ✅ Response Check
Always check the `success` field:
```json
{
  "success": true,
  "message": "Operation completed successfully"
}
```
