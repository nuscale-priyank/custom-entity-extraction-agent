# Custom Entity Creator - How to Use

## Overview
The Custom Entity Creator is an intelligent entity extraction and management tool that helps you create meaningful business entities from your Credit Domain fields and asset columns through natural language conversations.

## Getting Started

### 1. Select Your Data Sources
- **Credit Domain Fields**: Choose relevant fields from your Credit Domain system
- **Asset Columns**: Select columns from your data assets
- The system will use these selections to create contextual entities

### 2. Start a Conversation
Simply type your request in natural language. The AI will understand your intent and help you extract or manage entities.

## Available Commands

### Entity Extraction
**Extract entities from your selected data:**
```
"Extract entities from this data"
"Create entities from the selected fields"
"Analyze the Credit Domain fields and asset columns"
"Generate entities from context"
```

### Entity Creation
**Create custom entities:**
```
"Create a Customer Profile entity"
"Build a Risk Assessment entity"
"Make an entity for Transaction Data"
"Add a new entity for Credit Analysis"
```

### Entity Management
**List and view your entities:**
```
"List all my entities"
"Show me the entities I created"
"Display entity information"
"What entities do I have?"
```

**Delete entities:**
```
"Delete the Customer entity"
"Remove the Risk Assessment entity"
"Drop the Transaction entity"
```

### Relationship Analysis
**Analyze connections between entities:**
```
"Show me relationships between entities"
"Analyze entity relationships"
"How are my entities connected?"
"Find relationships in my data"
```

### General Help
**Get assistance:**
```
"Help"
"What can you do?"
"How do I use this tool?"
"Show me available commands"
```

## Example Workflows

### Workflow 1: Extract Entities from Data
1. Select Credit Domain fields (e.g., `customer_id`, `credit_score`)
2. Select asset columns (e.g., `risk_category`, `transaction_amount`)
3. Type: `"Extract entities from this data"`
4. The AI will create meaningful entities like "Customer Credit Profile" with attributes from your selected fields

### Workflow 2: Create Custom Entities
1. Type: `"Create a Customer Demographics entity with age, location, and income attributes"`
2. The AI will create the entity with the specified attributes
3. Use: `"List all my entities"` to see what was created

### Workflow 3: Analyze Relationships
1. Create multiple related entities
2. Type: `"Show me relationships between entities"`
3. The AI will analyze and display how your entities are connected

## Tips for Better Results

### ✅ Do This:
- **Be specific**: "Create a Customer Profile entity" vs "Create entity"
- **Use natural language**: "Extract entities from this data" works better than "extract"
- **Provide context**: Mention what you want the entity to represent
- **Ask for relationships**: "How are these entities connected?"

### ❌ Avoid:
- Overly complex requests in a single message
- Vague commands like "do something"
- Mixing multiple intents in one message

## Understanding the Output

### Entity Information
Each entity includes:
- **Name**: Descriptive name based on your data
- **Type**: Category (business_metric, derived_insight, etc.)
- **Attributes**: Specific fields from your Credit Domain/asset data
- **Relationships**: Connections to other entities
- **Confidence**: AI's confidence in the extraction

### Relationship Types
- **Depends On**: One entity relies on data from another
- **Derived From**: One entity is calculated from another
- **Related To**: General connection between entities

## Quick Reference

| Intent | Example Commands |
|--------|------------------|
| Extract | "Extract entities", "Create from data" |
| Create | "Create Customer entity", "Build Risk entity" |
| List | "List entities", "Show my entities" |
| Delete | "Delete Customer", "Remove Risk entity" |
| Relationships | "Show relationships", "Analyze connections" |
| Help | "Help", "What can you do?" |

## Need More Help?

The AI agent is designed to understand natural language, so feel free to ask questions in your own words. The system will guide you through the process and provide helpful responses based on your specific data and requirements.

---

*The Custom Entity Creator learns from your data selections and creates entities that are meaningful for your specific business context.*
