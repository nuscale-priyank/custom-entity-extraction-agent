#!/usr/bin/env python3
"""
Test script for the Custom Entity Extraction Agent

This script tests the agent functionality with sample data.
"""

import os
import sys
import json
from typing import Dict, Any

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import CustomEntityExtractionAgent
from models import AgentRequest, BC3Segment
from sample_payloads import SAMPLE_BC3_DATA, SAMPLE_GENERIC_DATA


def test_agent_initialization():
    """Test agent initialization"""
    print("Testing agent initialization...")
    
    try:
        # Check if environment variable is set
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            print("  GOOGLE_CLOUD_PROJECT not set. Using dummy project for testing.")
            project_id = "test-project"
        
        agent = CustomEntityExtractionAgent(project_id=project_id)
        print(" Agent initialized successfully")
        return agent
    except Exception as e:
        print(f" Failed to initialize agent: {e}")
        return None


def test_bc3_entity_extraction(agent: CustomEntityExtractionAgent):
    """Test BC3 entity extraction"""
    print("Testing BC3 entity extraction...")
    
    try:
        # Create BC3 segment from sample data
        bc3_segment = BC3Segment(**SAMPLE_BC3_DATA)
        
        # Create request
        request = AgentRequest(
            message="Extract all entities from this BC3 Account History segment and provide insights about the data quality.",
            data=bc3_segment,
            context_provider="bc3",
            chat_history=[],
            session_id="test_session_bc3",
            tools_enabled=True,
            metadata={
                "test": True,
                "source": "sample_data"
            }
        )
        
        # Process request
        response = agent.process_request(request)
        
        print(f" BC3 extraction successful")
        print(f"   - Extracted {len(response.extracted_entities)} entities")
        print(f"   - Confidence score: {response.confidence_score:.2f}")
        print(f"   - Processing time: {response.processing_time:.2f}s")
        print(f"   - Session ID: {response.session_id}")
        
        # Print some extracted entities
        print("\n   📋 Sample extracted entities:")
        for i, entity in enumerate(response.extracted_entities[:3]):
            print(f"     {i+1}. {entity.entity_type}: {entity.entity_name} = {entity.entity_value}")
        
        return True
        
    except Exception as e:
        print(f" BC3 extraction failed: {e}")
        return False


def test_generic_entity_extraction(agent: CustomEntityExtractionAgent):
    """Test generic entity extraction"""
    print(" Testing generic entity extraction...")
    
    try:
        # Create request with generic data
        request = AgentRequest(
            message="Analyze this user profile data and extract all meaningful entities including nested objects and arrays.",
            data=SAMPLE_GENERIC_DATA,
            context_provider="generic",
            chat_history=[],
            session_id="test_session_generic",
            tools_enabled=True,
            metadata={
                "test": True,
                "source": "sample_data"
            }
        )
        
        # Process request
        response = agent.process_request(request)
        
        print(f"Generic extraction successful")
        print(f"   - Extracted {len(response.extracted_entities)} entities")
        print(f"   - Confidence score: {response.confidence_score:.2f}")
        print(f"   - Processing time: {response.processing_time:.2f}s")
        print(f"   - Session ID: {response.session_id}")
        
        # Print some extracted entities
        print(" Sample extracted entities:")
        for i, entity in enumerate(response.extracted_entities[:3]):
            print(f"     {i+1}. {entity.entity_type}: {entity.entity_name} = {entity.entity_value}")
        
        return True
        
    except Exception as e:
        print(f" Generic extraction failed: {e}")
        return False


def test_chat_history(agent: CustomEntityExtractionAgent):
    """Test chat history functionality"""
    print(" Testing chat history functionality...")
    
    try:
        # First request
        request1 = AgentRequest(
            message="What entities can you extract from BC3 data?",
            data=SAMPLE_BC3_DATA,
            context_provider="bc3",
            chat_history=[],
            session_id="test_session_chat",
            tools_enabled=True
        )
        
        response1 = agent.process_request(request1)
        
        # Second request with chat history
        request2 = AgentRequest(
            message="Now extract entities from the same data and provide detailed analysis.",
            data=SAMPLE_BC3_DATA,
            context_provider="bc3",
            chat_history=response1.chat_history,
            session_id="test_session_chat",
            tools_enabled=True
        )
        
        response2 = agent.process_request(request2)
        
        print(f" Chat history test successful")
        print(f"   - First response entities: {len(response1.extracted_entities)}")
        print(f"   - Second response entities: {len(response2.extracted_entities)}")
        print(f"   - Chat history length: {len(response2.chat_history)}")
        
        return True
        
    except Exception as e:
        print(f" Chat history test failed: {e}")
        return False


def test_data_quality_analysis(agent: CustomEntityExtractionAgent):
    """Test data quality analysis"""
    print(" Testing data quality analysis...")
    
    try:
        # Test BC3 data quality
        bc3_segment = BC3Segment(**SAMPLE_BC3_DATA)
        request = AgentRequest(
            message="Analyze the data quality of this BC3 segment and provide insights.",
            data=bc3_segment,
            context_provider="bc3",
            chat_history=[],
            session_id="test_session_quality",
            tools_enabled=True
        )
        
        response = agent.process_request(request)
        
        # Check if analysis metadata is present
        if "analysis" in response.metadata:
            analysis = response.metadata["analysis"]
            print(f" Data quality analysis successful")
            print(f"   - Context provider: {analysis.get('context_provider', 'unknown')}")
            
            if "data_quality_score" in analysis:
                print(f"   - Data quality score: {analysis['data_quality_score']:.2f}")
            
            if "total_fields" in analysis:
                print(f"   - Total fields: {analysis['total_fields']}")
            
            return True
        else:
            print(" No analysis metadata found in response")
            return False
        
    except Exception as e:
        print(f" Data quality analysis failed: {e}")
        return False


def main():
    """Main test function"""
    print(" Starting Custom Entity Extraction Agent Tests")
    print("=" * 50)
    
    # Test agent initialization
    agent = test_agent_initialization()
    if not agent:
        print(" Cannot proceed without agent initialization")
        return
    
    # Run tests
    tests = [
        ("BC3 Entity Extraction", test_bc3_entity_extraction),
        ("Generic Entity Extraction", test_generic_entity_extraction),
        ("Chat History", test_chat_history),
        ("Data Quality Analysis", test_data_quality_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(agent)
            results.append((test_name, result))
        except Exception as e:
            print(f" {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print(" All tests passed! The agent is working correctly.")
    else:
        print(" Some tests failed. Check the output above for details.")
    
    print("\n💡 Next steps:")
    print("   1. Set GOOGLE_CLOUD_PROJECT environment variable")
    print("   2. Run 'python main.py' to start the API server")
    print("   3. Visit http://localhost:8000/docs for API documentation")
    print("   4. Use sample_payloads.py for testing the API endpoints")


if __name__ == "__main__":
    main()
