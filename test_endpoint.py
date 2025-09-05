#!/usr/bin/env python3
"""
Test script for the Credit Domain Entity Extraction Agent
"""

import requests
import json
from datetime import datetime

# Test data
test_request = {
    "message": "Please extract entities from the selected BC3 fields and asset columns to help me understand credit risk patterns.",
    "session_id": "test_session_001",
    "selected_bc3_fields": [
        {
            "field": {
                "uuid": "field_006",
                "known_implementations": ["account_number", "credit_account"],
                "valid_values": ["1234567890", "0987654321", "1122334455"],
                "definition": "Unique identifier for the credit account",
                "notes": "Masked for security in production",
                "description": "Account Number"
            },
            "segment_context": {
                "segment_name": "Credit Accounts"
            }
        },
        {
            "field": {
                "uuid": "field_007",
                "known_implementations": ["credit_limit", "max_credit"],
                "valid_values": ["5000", "10000", "25000", "50000"],
                "definition": "Maximum amount of credit available on the account",
                "notes": "Expressed in dollars without currency symbol",
                "description": "Credit Limit"
            },
            "segment_context": {
                "segment_name": "Credit Accounts"
            }
        },
        {
            "field": {
                "uuid": "field_008",
                "known_implementations": ["balance", "current_balance"],
                "valid_values": ["1250.50", "5000.00", "0.00"],
                "definition": "Current outstanding balance on the credit account",
                "notes": "Expressed in dollars with decimal precision",
                "description": "Current Balance"
            },
            "segment_context": {
                "segment_name": "Credit Accounts"
            }
        }
    ],
    "selected_asset_columns": [
        {
            "column": {
                "column_name": "credit_score",
                "column": "credit_score"
            },
            "asset_context": {
                "asset_name": "Consumer Credit Database",
                "workspace_name": "Credit Analytics Workspace",
                "big_query_table_name": "credit_analytics.consumer_credit_data"
            }
        },
        {
            "column": {
                "column_name": "total_debt",
                "column": "total_debt"
            },
            "asset_context": {
                "asset_name": "Consumer Credit Database",
                "workspace_name": "Credit Analytics Workspace",
                "big_query_table_name": "credit_analytics.consumer_credit_data"
            }
        },
        {
            "column": {
                "column_name": "credit_utilization",
                "column": "credit_utilization"
            },
            "asset_context": {
                "asset_name": "Consumer Credit Database",
                "workspace_name": "Credit Analytics Workspace",
                "big_query_table_name": "credit_analytics.consumer_credit_data"
            }
        }
    ],
    "context_provider": "credit_domain",
    "tools_enabled": True,
    "metadata": {
        "test": True,
        "timestamp": datetime.now().isoformat()
    }
}

def test_chat_endpoint():
    """Test the chat endpoint"""
    try:
        print("🚀 Testing Credit Domain Entity Extraction Agent...")
        print("=" * 60)
        
        # Send request to the chat endpoint
        response = requests.post(
            "http://localhost:8000/chat",
            json=test_request,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS! Response received:")
            print(f"📝 Response: {result['response'][:200]}...")
            print(f"🔍 Extracted Entities: {len(result['extracted_entities'])}")
            
            # Display extracted entities
            if result['extracted_entities']:
                print("\n📊 EXTRACTED ENTITIES:")
                print("=" * 40)
                for i, entity in enumerate(result['extracted_entities'], 1):
                    print(f"Entity #{i}:")
                    print(f"  Type: {entity['entity_type']}")
                    print(f"  Name: {entity['entity_name']}")
                    print(f"  Value: {entity['entity_value']}")
                    print(f"  Confidence: {entity['confidence']}")
                    print(f"  Source: {entity['source_field']}")
                    print(f"  Description: {entity['description']}")
                    if 'relationships' in entity and entity['relationships']:
                        print(f"  Relationships: {entity['relationships']}")
                    print("  " + "-" * 30)
            else:
                print("⚠️ No entities were extracted")
            
            print(f"⏱️ Processing Time: {result['processing_time']:.2f}s")
            print(f"🎯 Confidence Score: {result['confidence_score']}")
            
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the service is running on port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat_endpoint()

