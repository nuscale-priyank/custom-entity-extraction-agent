"""
Prompts for the BC3 AI Agent
"""

def get_system_prompt() -> str:
    """Get the system prompt for entity extraction"""
    return """You are an entity extraction agent. 

Your job is to:
1. Analyze the provided BC3 fields and asset columns
2. Create meaningful business entities using the create_entities tool
3. Use the tool to save entities to Firestore

IMPORTANT: You MUST use the create_entities tool. Do not just describe entities - actually create them.

APPROACH:
- Create ONE OR MORE meaningful business entities
- Each entity should have MULTIPLE attributes underneath it
- Think hierarchically: Entity → Attributes
- Focus on business value and relationships

Tool format:
- session_id: The session ID provided
- entities_data: JSON array of entities with this structure:
  [
    {{
      "entity_name": "Main Business Entity Name",
      "entity_type": "field|asset|business_metric|derived_insight",
      "entity_value": "Entity description",
      "confidence": 0.95,
      "source_field": "Source field name",
      "description": "Detailed description",
      "attributes": [
        {{
          "attribute_name": "Attribute 1 Name",
          "attribute_value": "Attribute 1 Value",
          "attribute_type": "string|numeric|boolean",
          "confidence": 0.9,
          "source_field": "Source",
          "description": "Attribute 1 description"
        }},
        {{
          "attribute_name": "Attribute 2 Name",
          "attribute_value": "Attribute 2 Value",
          "attribute_type": "string|numeric|boolean",
          "confidence": 0.9,
          "source_field": "Source",
          "description": "Attribute 2 description"
        }}
      ]
    }}
  ]

EXAMPLES:
- Entity: "Credit Account" with attributes: "Account ID", "Credit Score", "Account Type"
- Entity: "Customer Profile" with attributes: "Customer ID", "Risk Rating", "Credit Limit"
- Entity: "Transaction" with attributes: "Transaction ID", "Amount", "Date", "Type"

Create 1-3 meaningful entities, each with 2-5 relevant attributes from the provided data."""


def get_context_prompt(bc3_fields: list = None, asset_columns: list = None) -> str:
    """Generate context prompt from BC3 fields and asset columns"""
    context_parts = []
    
    if bc3_fields:
        context_parts.append("BC3 Fields:")
        for i, field_data in enumerate(bc3_fields, 1):
            field = field_data.get("field", {})
            segment = field_data.get("segment_context", {})
            
            # Use field_name or description, and get data_type from field
            field_name = field.get('field_name', field.get('description', 'Unknown'))
            data_type = field.get('data_type', 'string')  # Default to string if not specified
            segment_name = segment.get('segment_name', 'Unknown')
            
            context_parts.append(f"{i}. {field_name} ({data_type}) - {segment_name}")
    
    if asset_columns:
        context_parts.append("Asset Columns:")
        for i, column_data in enumerate(asset_columns, 1):
            # Get asset context information
            asset_context = column_data.get('asset_context', {})
            asset_name = asset_context.get('asset_name', 'Unknown')
            
            # Concise format with asset context
            column_name = column_data.get('column_name', 'Unknown')
            data_type = column_data.get('data_type', 'Unknown')
            description = column_data.get('description', 'No description')
            
            # Truncate long descriptions
            if len(description) > 50:
                description = description[:47] + "..."
            
            context_parts.append(f"{i}. {column_name} ({data_type}) - {asset_name}: {description}")
    
    if not context_parts:
        return "No context provided"
    
    context_parts.append("")
    context_parts.append("Create 1-3 meaningful business entities with multiple attributes from this data.")
    
    return "\n".join(context_parts)
