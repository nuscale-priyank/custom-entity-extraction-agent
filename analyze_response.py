#!/usr/bin/env python3
"""
Analyze the API response from the entity extraction endpoint
"""

import json
import re

def analyze_response():
    """Analyze the API response"""
    
    print("🔍 ANALYSIS OF ENTITY EXTRACTION RESPONSE")
    print("=" * 60)
    
    # The raw response from the API (cleaned)
    raw_response = """{"response":"EXTRACTED ENTITIES:\n1. Entity Type: Account Identifier - account_number (Confidence: 1.0)\n   Source: BC3 Fields (Account Number)\n   Business Significance: Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.\n   Relationships: Links to specific credit limits and consumer credit data.\n\n2. Entity Type: Credit Limit - credit_limit (Confidence: 1.0)\n   Source: BC3 Fields (Credit Limit)\n   Business Significance: Represents the maximum borrowing capacity for an account, a key factor in assessing credit utilization and potential risk.\n   Relationships: Directly related to account number and influences credit utilization ratio calculations when combined with balance information.\n\n3. Entity Type: Credit Score - credit_score (Confidence: 0.9)\n   Source: Asset Columns (credit_score from Consumer Credit Database)\n   Business Significance: A primary indicator of an individual's creditworthiness and likelihood to repay debt, essential for risk assessment.\n   Relationships: Can be correlated with credit limits and account payment behavior to identify risk patterns.\n\n4. Entity Type: Potential Credit Utilization - Potential Credit Utilization (Confidence: 0.8)\n   Source: BC3 Fields (Credit Limit), Asset Columns (credit_score)\n   Business Significance: This derived metric represents the potential for an account to become over-utilized, a significant risk indicator. It's calculated by considering the credit limit in relation to typical spending patterns (which would require balance data). A high credit limit with a low credit score suggests a higher risk of over-utilization.\n   Relationships: Links credit limit and credit score to a forward-looking risk assessment.\n\nANALYSIS:\nThe extracted entities provide a foundational understanding of credit risk. The Account Number and Credit Limit are direct data points from the BC3 segment, essential for identifying and quantifying credit exposure. The Credit Score from the asset data is a critical external measure of creditworthiness.\n\nBy combining these, we can begin to infer potential risk patterns. For instance, a high credit limit coupled with a low credit score (as indicated by the derived \"Potential Credit Utilization\" entity) suggests a higher risk profile. To further enhance this analysis, information on current account balances and payment history would be highly valuable for calculating actual credit utilization and identifying delinquency patterns.\n\nSUGGESTIONS FOR ADDITIONAL CONTEXT:\n- BC3 Fields: Account Balance, Payment History, Loan Amount, Loan Term\n- Asset Columns: Debt-to-Income Ratio, Loan Default History, Employment Status","extracted_entities":[{"entity_type":"metadata","entity_name":"Account Identifier","entity_value":"account_number","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"BC3 Fields (Account Number)\n   Business Significance: Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.\n   Relationships: Links to specific credit limits and consumer credit data.\n\n2. Entity Type: Credit Limit","entity_value":"credit_limit","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"BC3 Fields (Credit Limit)\n   Business Significance: Represents the maximum borrowing capacity for an account, a key factor in assessing credit utilization and potential risk.\n   Relationships: Directly related to account number and influences credit utilization ratio calculations when combined with balance information.\n\n3. Entity Type: Credit Score","entity_value":"credit_score","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"Asset Columns (credit_score from Consumer Credit Database)\n   Business Significance: A primary indicator of an individual's creditworthiness and likelihood to repay debt, essential for risk assessment.\n   Relationships: Can be correlated with credit limits and account payment behavior to identify risk patterns.\n\n4. Entity Type: Potential Credit Utilization","entity_value":"Potential Credit Utilization","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"BC3 Fields (Credit Limit), Asset Columns (credit_score)\nBusiness Significance: This derived metric represents the potential for an account to become over","entity_value":"utilized, a significant risk indicator. It's calculated by considering the credit limit in relation to typical spending patterns","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"}],"chat_state":{"session_id":"test_session_002","messages":[{"role":"user","content":"Please extract entities from the selected BC3 fields and asset columns to help me understand credit risk patterns.","timestamp":"2025-09-03T12:38:14.142845"}],"selected_segments":[],"selected_assets":[],"selected_bc3_fields":[],"selected_asset_columns":[],"extracted_entities":[{"entity_type":"metadata","entity_name":"Account Identifier","entity_value":"entity_value":"account_number","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"BC3 Fields (Account Number)\n   Business Significance: Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.\n   Relationships: Links to specific credit limits and consumer credit data.\n\n2. Entity Type: Credit Limit","entity_value":"credit_limit","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"BC3 Fields (Credit Limit)\n   Business Significance: Represents the maximum borrowing capacity for an account, a key factor in assessing credit utilization and potential risk.\n   Relationships: Directly related to account number and influences credit utilization ratio calculations when combined with balance information.\n\n3. Entity Type: Credit Score","entity_value":"credit_score","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"Asset Columns (credit_score from Consumer Credit Database)\n   Business Significance: A primary indicator of an individual's creditworthiness and likelihood to repay debt, essential for risk assessment.\n   Relationships: Can be correlated with credit limits and account payment behavior to identify risk patterns.\n\n4. Entity Type: Potential Credit Utilization","entity_value":"Potential Credit Utilization","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"},{"entity_type":"metadata","entity_name":"BC3 Fields (Credit Limit), Asset Columns (credit_score)\nBusiness Significance: This derived metric represents the potential for an account to become over","entity_value":"utilized, a significant risk indicator. It's calculated by considering the credit limit in relation to typical spending patterns","confidence":1.0,"source_field":"BC3 Fields (Account Number)","description":"Uniquely identifies each credit account, crucial for tracking and analysis of individual credit behavior.","relationships":{},"context_provider":"credit_domain"}],"metadata":{}},"confidence_score":0.9,"processing_time":2.9213061332702637,"metadata":{"session_id":"test_session_002"}}"""
    
    try:
        # Parse the JSON response
        response_data = json.loads(raw_response)
        
        # 1. LLM Response Analysis
        print("\n📝 LLM RESPONSE ANALYSIS:")
        print("-" * 40)
        llm_response = response_data["response"]
        
        # Check if response follows expected format
        if "EXTRACTED ENTITIES:" in llm_response:
            print("✅ Contains 'EXTRACTED ENTITIES:' section")
        else:
            print("❌ Missing 'EXTRACTED ENTITIES:' section")
            
        if "ANALYSIS:" in llm_response:
            print("✅ Contains 'ANALYSIS:' section")
        else:
            print("❌ Missing 'ANALYSIS:' section")
            
        if "SUGGESTIONS FOR ADDITIONAL CONTEXT:" in llm_response:
            print("✅ Contains 'SUGGESTIONS FOR ADDITIONAL CONTEXT:' section")
        else:
            print("❌ Missing 'SUGGESTIONS FOR ADDITIONAL CONTEXT:' section")
        
        # 2. Entity Extraction Analysis
        print("\n📊 ENTITY EXTRACTION ANALYSIS:")
        print("-" * 40)
        entities = response_data["extracted_entities"]
        print(f"Total entities extracted: {len(entities)}")
        
        # Analyze each entity
        for i, entity in enumerate(entities, 1):
            print(f"\nEntity #{i}:")
            print(f"  Type: {entity['entity_type']}")
            print(f"  Name: {entity['entity_name'][:50]}...")
            print(f"  Value: {entity['entity_value'][:50]}...")
            print(f"  Confidence: {entity['confidence']}")
            print(f"  Source: {entity['source_field']}")
            print(f"  Description: {entity['description'][:80]}...")
            print(f"  Relationships: {entity['relationships']}")
        
        # 3. Issues Identified
        print("\n⚠️ ISSUES IDENTIFIED:")
        print("-" * 40)
        
        # Check for parsing issues
        issues = []
        
        # Issue 1: Entity names are too long and contain formatting
        for entity in entities:
            if "\n" in entity['entity_name']:
                issues.append("Entity names contain newlines and formatting")
                break
        
        # Issue 2: All entities have same description
        descriptions = set(entity['description'] for entity in entities)
        if len(descriptions) == 1:
            issues.append("All entities have identical descriptions")
        
        # Issue 3: All entities have same source
        sources = set(entity['source_field'] for entity in entities)
        if len(sources) == 1:
            issues.append("All entities have identical source fields")
        
        # Issue 4: Relationships are empty
        if all(not entity['relationships'] for entity in entities):
            issues.append("All entities have empty relationships")
        
        if issues:
            for issue in issues:
                print(f"❌ {issue}")
        else:
            print("✅ No major issues identified")
        
        # 4. Performance Metrics
        print("\n📈 PERFORMANCE METRICS:")
        print("-" * 40)
        print(f"Processing Time: {response_data['processing_time']:.2f}s")
        print(f"Confidence Score: {response_data['confidence_score']}")
        print(f"Session ID: {response_data['chat_state']['session_id']}")
        
        # 5. Recommendations
        print("\n💡 RECOMMENDATIONS:")
        print("-" * 40)
        print("1. Fix entity parsing to handle multi-line entity names")
        print("2. Improve relationship extraction from LLM response")
        print("3. Ensure unique descriptions for each entity")
        print("4. Map entity types more accurately (not all 'metadata')")
        print("5. Extract relationships from LLM response properly")
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print("\n🔍 MANUAL ANALYSIS OF RESPONSE:")
        print("-" * 40)
        
        # Manual analysis of the response
        if "EXTRACTED ENTITIES:" in raw_response:
            print("✅ LLM Response: Contains 'EXTRACTED ENTITIES:' section")
            
            # Extract the entities section
            entities_start = raw_response.find("EXTRACTED ENTITIES:")
            entities_end = raw_response.find("ANALYSIS:")
            if entities_start != -1 and entities_end != -1:
                entities_section = raw_response[entities_start:entities_end]
                print(f"\n📝 Entities Section Preview:")
                print(entities_section[:500] + "...")
        
        # Count entities in the response
        entity_count = raw_response.count('"entity_type"')
        print(f"\n📊 Raw Entity Count: {entity_count}")
        
        # Check for parsing issues
        if "\\n" in raw_response:
            print("⚠️ Issue: Response contains escaped newlines")
        if "Business Significance:" in raw_response:
            print("✅ Good: Response contains business significance")
        if "Relationships:" in raw_response:
            print("✅ Good: Response contains relationships")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    analyze_response()
