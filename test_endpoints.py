#!/usr/bin/env python3
"""
Test script to demonstrate the different payloads for each endpoint
"""

import json
import requests
from sample_payloads import (
    SAMPLE_GENERIC_ENDPOINT_REQUEST,
    SAMPLE_GENERIC_ENDPOINT_REQUEST_2,
    SAMPLE_BC3_ENDPOINT_REQUEST,
    SAMPLE_GENERIC_SPECIFIC_REQUEST,
    SAMPLE_BC3_DATA,
    SAMPLE_GENERIC_DATA
)

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("="*60)
    print("1. TESTING HEALTH ENDPOINT")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_context_providers():
    """Test the context providers endpoint"""
    print("="*60)
    print("2. TESTING CONTEXT PROVIDERS ENDPOINT")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/context-providers")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_main_generic_endpoint_bc3():
    """Test the main generic endpoint with BC3 data"""
    print("="*60)
    print("3. TESTING MAIN GENERIC ENDPOINT (BC3 Data)")
    print("="*60)
    print("Endpoint: POST /extract-entities")
    print("Payload: SAMPLE_GENERIC_ENDPOINT_REQUEST")
    print()
    
    response = requests.post(
        f"{BASE_URL}/extract-entities",
        json=SAMPLE_GENERIC_ENDPOINT_REQUEST
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Entities Extracted: {len(result.get('extracted_entities', []))}")
        print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"Response Preview: {result.get('response', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
    print()

def test_main_generic_endpoint_generic():
    """Test the main generic endpoint with generic data"""
    print("="*60)
    print("4. TESTING MAIN GENERIC ENDPOINT (Generic Data)")
    print("="*60)
    print("Endpoint: POST /extract-entities")
    print("Payload: SAMPLE_GENERIC_ENDPOINT_REQUEST_2")
    print()
    
    response = requests.post(
        f"{BASE_URL}/extract-entities",
        json=SAMPLE_GENERIC_ENDPOINT_REQUEST_2
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Entities Extracted: {len(result.get('extracted_entities', []))}")
        print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"Response Preview: {result.get('response', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
    print()

def test_bc3_specific_endpoint():
    """Test the BC3-specific endpoint"""
    print("="*60)
    print("5. TESTING BC3-SPECIFIC ENDPOINT")
    print("="*60)
    print("Endpoint: POST /extract-entities/bc3")
    print("Payload: SAMPLE_BC3_ENDPOINT_REQUEST")
    print()
    
    response = requests.post(
        f"{BASE_URL}/extract-entities/bc3",
        json=SAMPLE_BC3_ENDPOINT_REQUEST
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Entities Extracted: {len(result.get('extracted_entities', []))}")
        print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"Response Preview: {result.get('response', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
    print()

def test_generic_specific_endpoint():
    """Test the generic-specific endpoint"""
    print("="*60)
    print("6. TESTING GENERIC-SPECIFIC ENDPOINT")
    print("="*60)
    print("Endpoint: POST /extract-entities/generic")
    print("Payload: SAMPLE_GENERIC_SPECIFIC_REQUEST")
    print()
    
    response = requests.post(
        f"{BASE_URL}/extract-entities/generic",
        json=SAMPLE_GENERIC_SPECIFIC_REQUEST
    )
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Entities Extracted: {len(result.get('extracted_entities', []))}")
        print(f"Confidence Score: {result.get('confidence_score', 0):.2f}")
        print(f"Processing Time: {result.get('processing_time', 0):.2f}s")
        print(f"Response Preview: {result.get('response', '')[:200]}...")
    else:
        print(f"Error: {response.text}")
    print()

def print_summary():
    """Print a summary of all endpoints and their payloads"""
    print("="*80)
    print("SUMMARY: ENDPOINTS AND THEIR PAYLOADS")
    print("="*80)
    print()
    print("1. GET /health")
    print("   • No payload needed")
    print("   • Returns: Health status")
    print()
    print("2. GET /context-providers")
    print("   • No payload needed")
    print("   • Returns: Available context providers")
    print()
    print("3. POST /extract-entities (Main Generic Endpoint)")
    print("   • Payload: SAMPLE_GENERIC_ENDPOINT_REQUEST (BC3 data)")
    print("   • Payload: SAMPLE_GENERIC_ENDPOINT_REQUEST_2 (Generic data)")
    print("   • Supports: Both BC3 and generic via context_provider field")
    print()
    print("4. POST /extract-entities/bc3 (BC3-Specific Endpoint)")
    print("   • Payload: SAMPLE_BC3_ENDPOINT_REQUEST")
    print("   • Supports: Only BC3 data (context_provider auto-set)")
    print()
    print("5. POST /extract-entities/generic (Generic-Specific Endpoint)")
    print("   • Payload: SAMPLE_GENERIC_SPECIFIC_REQUEST")
    print("   • Supports: Only generic data (context_provider auto-set)")
    print()
    print("="*80)
    print("PAYLOAD SELECTION GUIDE")
    print("="*80)
    print("• For BC3 data: Use /extract-entities/bc3 or /extract-entities with context_provider='bc3'")
    print("• For Generic data: Use /extract-entities/generic or /extract-entities with context_provider='generic'")
    print("• For flexibility: Use /extract-entities with appropriate context_provider")
    print()

if __name__ == "__main__":
    print("🧪 TESTING CUSTOM ENTITY EXTRACTION AGENT ENDPOINTS")
    print("="*80)
    print()
    
    try:
        # Test all endpoints
        test_health()
        test_context_providers()
        test_main_generic_endpoint_bc3()
        test_main_generic_endpoint_generic()
        test_bc3_specific_endpoint()
        test_generic_specific_endpoint()
        
        # Print summary
        print_summary()
        
        print("✅ All tests completed successfully!")
        print("\n📋 Next steps:")
        print("1. Check the responses above for entity extraction results")
        print("2. Use the sample payloads in sample_payloads.py for your own testing")
        print("3. Modify the payloads to test with your own data")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running on http://localhost:8000")
        print("Run: python main.py --port 8000")
    except Exception as e:
        print(f"❌ Error: {e}")
