"""
Relationship Detection and Management for Entities
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from models.entity_collection_models import CustomEntity

logger = logging.getLogger(__name__)


class RelationshipDetector:
    """Detects and manages relationships between entities"""
    
    def __init__(self):
        self.relationship_types = {
            "derived_from": "This entity is derived from or calculated using data from another entity",
            "relates_to": "This entity is related to another entity in the same domain",
            "depends_on": "This entity depends on data from another entity",
            "part_of": "This entity is part of a larger entity or system",
            "references": "This entity references or links to another entity"
        }
    
    def detect_relationships(self, entities: List[CustomEntity]) -> Dict[str, Dict[str, Any]]:
        """
        Detect relationships between entities based on various criteria
        
        Args:
            entities: List of entities to analyze
            
        Returns:
            Dictionary mapping entity_id to relationship information
        """
        relationships = {}
        
        if len(entities) < 2:
            return relationships
        
        logger.info(f"Detecting relationships between {len(entities)} entities")
        
        for entity in entities:
            entity_relationships = {}
            
            for other_entity in entities:
                if entity.entity_id == other_entity.entity_id:
                    continue
                
                # Detect different types of relationships
                detected_relationships = self._analyze_entity_pair(entity, other_entity)
                
                if detected_relationships:
                    entity_relationships[other_entity.entity_id] = detected_relationships
            
            if entity_relationships:
                relationships[entity.entity_id] = entity_relationships
        
        logger.info(f"Detected relationships for {len(relationships)} entities")
        return relationships
    
    def _analyze_entity_pair(self, entity1: CustomEntity, entity2: CustomEntity) -> Optional[Dict[str, Any]]:
        """Analyze a pair of entities to detect relationships"""
        
        relationships = []
        
        # 1. Check for shared attributes (common data fields)
        shared_attrs = self._find_shared_attributes(entity1, entity2)
        if shared_attrs:
            relationships.append({
                "type": "relates_to",
                "confidence": 0.8,
                "description": f"Shares {len(shared_attrs)} common attributes: {', '.join(shared_attrs[:3])}",
                "shared_attributes": shared_attrs
            })
        
        # 2. Check for derived relationships based on entity types
        derived_rel = self._check_derived_relationship(entity1, entity2)
        if derived_rel:
            relationships.append(derived_rel)
        
        # 3. Check for dependency relationships based on source fields
        dep_rel = self._check_dependency_relationship(entity1, entity2)
        if dep_rel:
            relationships.append(dep_rel)
        
        # 4. Check for hierarchical relationships
        hier_rel = self._check_hierarchical_relationship(entity1, entity2)
        if hier_rel:
            relationships.append(hier_rel)
        
        return relationships if relationships else None
    
    def _find_shared_attributes(self, entity1: CustomEntity, entity2: CustomEntity) -> List[str]:
        """Find shared attribute names between two entities"""
        attrs1 = {attr.attribute_name.lower() for attr in entity1.attributes}
        attrs2 = {attr.attribute_name.lower() for attr in entity2.attributes}
        
        shared = list(attrs1.intersection(attrs2))
        return shared
    
    def _check_derived_relationship(self, entity1: CustomEntity, entity2: CustomEntity) -> Optional[Dict[str, Any]]:
        """Check if one entity is derived from another"""
        
        # Check if one is derived_insight and the other is field/asset
        if (entity1.entity_type.value == "derived_insight" and 
            entity2.entity_type.value in ["field", "asset", "business_metric"]):
            
            # Check if derived entity references the source entity's data
            source_fields = entity1.source_field.lower()
            if any(field in source_fields for field in [entity2.entity_name.lower(), entity2.entity_value.lower()]):
                return {
                    "type": "derived_from",
                    "confidence": 0.9,
                    "description": f"'{entity1.entity_name}' is derived from data in '{entity2.entity_name}'",
                    "source_entity": entity2.entity_id
                }
        
        return None
    
    def _check_dependency_relationship(self, entity1: CustomEntity, entity2: CustomEntity) -> Optional[Dict[str, Any]]:
        """Check if one entity depends on another"""
        
        # Check if entity descriptions or names suggest dependency
        desc1 = entity1.description.lower()
        desc2 = entity2.description.lower()
        name1 = entity1.entity_name.lower()
        name2 = entity2.entity_name.lower()
        
        # Look for dependency keywords
        dependency_keywords = ["depends on", "based on", "calculated from", "derived from", "uses data from"]
        
        for keyword in dependency_keywords:
            if keyword in desc1 and (name2 in desc1 or any(attr.attribute_name.lower() in desc1 for attr in entity2.attributes)):
                return {
                    "type": "depends_on",
                    "confidence": 0.85,
                    "description": f"'{entity1.entity_name}' depends on data from '{entity2.entity_name}'",
                    "dependency_reason": keyword
                }
        
        return None
    
    def _check_hierarchical_relationship(self, entity1: CustomEntity, entity2: CustomEntity) -> Optional[Dict[str, Any]]:
        """Check for hierarchical relationships"""
        
        # Check if one entity is part of another based on naming patterns
        name1 = entity1.entity_name.lower()
        name2 = entity2.entity_name.lower()
        
        # Look for hierarchical patterns
        if ("profile" in name1 and "profile" not in name2 and 
            any(word in name2 for word in name1.split() if len(word) > 3)):
            return {
                "type": "part_of",
                "confidence": 0.7,
                "description": f"'{entity2.entity_name}' appears to be part of '{entity1.entity_name}'",
                "hierarchical_reason": "naming_pattern"
            }
        
        return None
    
    def create_relationship_summary(self, relationships: Dict[str, Dict[str, Any]], entities: List[CustomEntity]) -> str:
        """Create a human-readable summary of relationships"""
        
        if not relationships:
            return "No relationships detected between entities."
        
        summary_parts = ["**Entity Relationships:**\n"]
        
        # Create entity lookup
        entity_lookup = {entity.entity_id: entity for entity in entities}
        
        for entity_id, entity_rels in relationships.items():
            entity = entity_lookup.get(entity_id)
            if not entity:
                continue
                
            summary_parts.append(f"**{entity.entity_name}:**")
            
            for target_entity_id, rel_list in entity_rels.items():
                target_entity = entity_lookup.get(target_entity_id)
                if not target_entity:
                    continue
                
                for rel in rel_list:
                    rel_type = rel["type"].replace("_", " ").title()
                    confidence = rel["confidence"]
                    description = rel["description"]
                    
                    summary_parts.append(f"  • {rel_type} → {target_entity.entity_name} (confidence: {confidence:.1f})")
                    summary_parts.append(f"    {description}")
            
            summary_parts.append("")
        
        return "\n".join(summary_parts)
    
    def update_entity_relationships(self, entity: CustomEntity, relationships: Dict[str, Any]) -> CustomEntity:
        """Update an entity with relationship information"""
        
        # Convert relationships to the format expected by the entity model
        formatted_relationships = {}
        
        for target_entity_id, rel_list in relationships.items():
            formatted_relationships[target_entity_id] = {
                "relationships": rel_list,
                "last_updated": "2025-01-08T00:00:00Z"  # Current timestamp
            }
        
        entity.relationships = formatted_relationships
        return entity
