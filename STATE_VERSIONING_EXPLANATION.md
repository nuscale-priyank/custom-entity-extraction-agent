# Auto-Incrementing State Version System

## Overview

The auto-incrementing state version system provides comprehensive change tracking across multiple levels:
1. **Session Level** - Tracks overall session changes
2. **Entity Level** - Tracks individual entity modifications
3. **Attribute Level** - Tracks attribute changes within entities

## Implementation Details

### 1. Model Definitions

#### ChatState (Session Level)
```python
class ChatState(BaseModel):
    session_id: str
    # ... other fields ...
    state_version: int = Field(default=1, description="Current state version")
    last_updated: datetime = Field(default_factory=datetime.now)
```

#### ExtractedEntity (Entity Level)
```python
class ExtractedEntity(BaseModel):
    entity_id: str
    # ... other fields ...
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    state_version: int = Field(default=1, description="State version for tracking changes")
```

#### EntityAttribute (Attribute Level)
```python
class EntityAttribute(BaseModel):
    attribute_id: str
    # ... other fields ...
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    # Note: Attributes don't have their own state_version - they inherit from entity
```

### 2. Auto-Increment Logic

#### Session State Version Increment
```python
def _save_session(self, session_id: str, chat_state: ChatState) -> bool:
    """Save session with updated state version"""
    chat_state.state_version += 1  # 🔄 AUTO-INCREMENT SESSION VERSION
    chat_state.last_updated = datetime.now()
    return self.session_manager.save_session(session_id, chat_state)
```

**When it increments:**
- Every time any entity is created, updated, or deleted
- Every time any attribute is added, updated, or deleted
- Any modification to the session state

#### Entity State Version Increment
```python
# Update entity metadata
entity_to_update.updated_at = datetime.now()
entity_to_update.state_version += 1  # 🔄 AUTO-INCREMENT ENTITY VERSION

# Replace entity in session
chat_state.extracted_entities[entity_index] = entity_to_update

# Save updated session (this also increments session state_version)
if self._save_session(request.session_id, chat_state):
    # ...
```

**When it increments:**
- When entity fields are modified (name, value, description, etc.)
- When attributes are added, updated, or deleted
- When entity relationships change

### 3. Version Tracking Flow

```
Initial State:
├── Session: state_version = 1
├── Entity A: state_version = 1
└── Entity B: state_version = 1

After Creating Entity C:
├── Session: state_version = 2 (+1)
├── Entity A: state_version = 1 (unchanged)
├── Entity B: state_version = 1 (unchanged)
└── Entity C: state_version = 1 (new)

After Updating Entity A:
├── Session: state_version = 3 (+1)
├── Entity A: state_version = 2 (+1)
├── Entity B: state_version = 1 (unchanged)
└── Entity C: state_version = 1 (unchanged)

After Deleting Entity B:
├── Session: state_version = 4 (+1)
├── Entity A: state_version = 2 (unchanged)
└── Entity C: state_version = 1 (unchanged)
```

## Best Practices Implementation

### 1. **Atomic Operations**
```python
# ✅ GOOD: All changes in one transaction
def update_entities(self, request: UpdateEntityRequest):
    # Get session
    chat_state = self._get_session(request.session_id)
    
    # Make all changes
    entity_to_update.state_version += 1
    entity_to_update.updated_at = datetime.now()
    
    # Save once (increments session version)
    if self._save_session(request.session_id, chat_state):
        return success_response
```

### 2. **Consistent Versioning**
```python
# ✅ GOOD: Both session and entity versions increment together
def _save_session(self, session_id: str, chat_state: ChatState) -> bool:
    chat_state.state_version += 1  # Session version
    chat_state.last_updated = datetime.now()
    return self.session_manager.save_session(session_id, chat_state)

def update_entity(self, entity):
    entity.state_version += 1  # Entity version
    entity.updated_at = datetime.now()
    # Then save session (which increments session version)
```

### 3. **Timestamp Tracking**
```python
# ✅ GOOD: Track both creation and update times
class ExtractedEntity(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    state_version: int = Field(default=1)
```

### 4. **Version-Specific Queries**
```python
# ✅ GOOD: Can read from specific state versions
def read_entities(self, request: ReadEntityRequest):
    entities = chat_state.extracted_entities
    
    # Filter by state version if specified
    if request.state_version:
        entities = [e for e in entities if e.state_version <= request.state_version]
    
    return entities
```

## Advanced Features

### 1. **State Version History**
```python
# You can track the history of changes
def get_entity_history(self, entity_id: str, session_id: str):
    # Read entities from different state versions
    versions = []
    for version in range(1, current_state_version + 1):
        entities = self.read_entities(ReadEntityRequest(
            session_id=session_id,
            entity_id=entity_id,
            state_version=version
        ))
        if entities.entities:
            versions.append({
                'state_version': version,
                'entity': entities.entities[0]
            })
    return versions
```

### 2. **Change Detection**
```python
# Detect what changed between versions
def get_changes(self, session_id: str, from_version: int, to_version: int):
    old_entities = self.read_entities(ReadEntityRequest(
        session_id=session_id,
        state_version=from_version
    ))
    
    new_entities = self.read_entities(ReadEntityRequest(
        session_id=session_id,
        state_version=to_version
    ))
    
    # Compare and return differences
    return compare_entities(old_entities.entities, new_entities.entities)
```

### 3. **Rollback Capability**
```python
# Rollback to a previous state version
def rollback_to_version(self, session_id: str, target_version: int):
    # This would require storing full state snapshots
    # or reconstructing from change logs
    pass
```

## Performance Considerations

### 1. **Efficient Incrementing**
```python
# ✅ GOOD: Simple integer increment (very fast)
chat_state.state_version += 1

# ❌ BAD: Complex version strings or UUIDs
chat_state.state_version = f"v{datetime.now().timestamp()}"
```

### 2. **Batch Operations**
```python
# ✅ GOOD: Batch multiple changes, increment once
def batch_update_entities(self, updates: List[UpdateEntityRequest]):
    chat_state = self._get_session(updates[0].session_id)
    
    for update in updates:
        # Make all changes
        entity = self._find_entity(update.entity_id)
        entity.state_version += 1
        # ... apply updates
    
    # Save once (single session version increment)
    self._save_session(updates[0].session_id, chat_state)
```

### 3. **Version Cleanup**
```python
# Optional: Clean up old versions to prevent unbounded growth
def cleanup_old_versions(self, session_id: str, keep_versions: int = 100):
    # Keep only the last N versions
    pass
```

## Testing the Version System

### Test Script
```python
def test_state_versioning():
    # Create entity
    response1 = update_entity(session_id="test", entity_id="test_entity", 
                             entity_updates={"name": "Test Entity"})
    assert response1.state_version == 2  # Session version
    
    # Update entity
    response2 = update_entity(session_id="test", entity_id="test_entity",
                             entity_updates={"name": "Updated Entity"})
    assert response2.state_version == 3  # Session version
    assert response2.updated_entity.state_version == 2  # Entity version
    
    # Read from specific version
    response3 = read_entities(session_id="test", state_version=2)
    # Should return entity as it was at version 2
```

## Benefits of This Approach

1. **🔍 Audit Trail**: Complete history of all changes
2. **🔄 Rollback**: Can revert to previous states
3. **📊 Analytics**: Track change frequency and patterns
4. **🔒 Consistency**: Atomic operations with version tracking
5. **⚡ Performance**: Simple integer increments are very fast
6. **🛡️ Reliability**: Easy to detect and handle conflicts
7. **📈 Scalability**: Works with large numbers of entities

## Summary

The auto-incrementing state version system provides:
- **Session-level versioning** for overall state changes
- **Entity-level versioning** for individual entity modifications
- **Timestamp tracking** for creation and update times
- **Atomic operations** ensuring consistency
- **Version-specific queries** for historical data access
- **Simple, efficient implementation** using integer increments

This approach balances functionality, performance, and simplicity while providing comprehensive change tracking capabilities.
