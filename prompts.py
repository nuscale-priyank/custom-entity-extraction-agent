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

CRITICAL: Use the ACTUAL field names and data from the provided BC3 fields and asset columns. Do not create generic entities like "BC3 Field" or "System Resource". Create specific entities based on the actual data provided.

APPROACH:
- Create ONE OR MORE meaningful business entities based on the actual data provided
- Each entity should have MULTIPLE attributes underneath it
- Use the actual field names, data types, and descriptions from the context
- Think hierarchically: Entity → Attributes
- Focus on business value and relationships

Tool format:
- session_id: The session ID provided
- entities_data: JSON array of entities with this structure:
  [
    {{
      "entity_name": "Specific Business Entity Name (based on actual data)",
      "entity_type": "field|asset|business_metric|derived_insight",
      "entity_value": "Entity description based on actual data",
      "confidence": 0.95,
      "source_field": "Actual source field names from context",
      "description": "Detailed description based on actual data",
      "attributes": [
        {{
          "attribute_name": "Actual Field Name from Context",
          "attribute_value": "Actual field name or value",
          "attribute_type": "string|numeric|boolean|date",
          "confidence": 0.9,
          "source_field": "Actual source field name",
          "description": "Description based on actual field data"
        }}
      ]
    }}
  ]

EXAMPLES:
- If BC3 field is "birth_date" → Entity: "Person Demographics" with attribute "Birth Date"
- If Asset column is "deceased_date" → Entity: "Person Status" with attribute "Deceased Date"
- If BC3 field is "credit_score" → Entity: "Credit Profile" with attribute "Credit Score"

Create 1-3 meaningful entities using the ACTUAL field names and data provided in the context."""


def get_context_prompt(bc3_fields: list = None, asset_columns: list = None) -> str:
    """Generate context prompt from BC3 fields and asset columns"""
    context_parts = []
    
    if bc3_fields:
        context_parts.append("BC3 Fields:")
        for i, field_data in enumerate(bc3_fields, 1):
            # Handle different possible structures
            if isinstance(field_data, dict):
                # Check if it has the nested structure
                if 'field' in field_data and 'segment_context' in field_data:
                    field = field_data.get("field", {})
                    segment = field_data.get("segment_context", {})
                    field_name = field.get('field_name', field.get('description', 'Unknown'))
                    data_type = field.get('data_type', 'string')
                    segment_name = segment.get('segment_name', 'Unknown')
                else:
                    # Direct structure
                    field_name = field_data.get('field_name', field_data.get('description', 'Unknown'))
                    data_type = field_data.get('data_type', 'string')
                    segment_name = field_data.get('segment_name', 'Unknown')
            else:
                field_name = str(field_data)
                data_type = 'string'
                segment_name = 'Unknown'
            
            context_parts.append(f"{i}. {field_name} ({data_type}) - {segment_name}")
    
    if asset_columns:
        context_parts.append("Asset Columns:")
        for i, column_data in enumerate(asset_columns, 1):
            # Get asset context information
            asset_context = column_data.get('asset_context', {})
            asset_name = asset_context.get('asset_name', 'General Asset')
            
            # Concise format with asset context
            column_name = column_data.get('column_name', f'Column_{i}')
            data_type = column_data.get('data_type', 'string')
            description = column_data.get('description', 'No description available')
            
            # Truncate long descriptions
            if len(description) > 50:
                description = description[:47] + "..."
            
            context_parts.append(f"{i}. {column_name} ({data_type}) - {asset_name}: {description}")
    
    if not context_parts:
        return "No context provided"
    
    context_parts.append("")
    context_parts.append("Create 1-3 meaningful business entities with multiple attributes from this data.")
    
    return "\n".join(context_parts)
