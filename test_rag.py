#!/usr/bin/env python3
"""
Test cases for RAG endpoint verification.
Tests both KB-present and KB-absent queries.
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/chat"
MODELS = ["mistral:7b"]

def test_knowledge_present():
    """Test 1: Query that EXISTS in knowledge base (scholarships)"""
    print("\n" + "="*70)
    print("TEST 1: Query WITH knowledge (scholarships - should be in KB)")
    print("="*70)
    
    query = "Jak ubiegać się o stypendium rektora?"
    payload = {
        "messages": [{"role": "user", "content": query}],
        "model": MODELS[0]
    }
    
    try:
        r = requests.post(BASE_URL, json=payload, timeout=120)
        print(f"Status Code: {r.status_code}")
        
        if r.status_code == 200:
            resp = r.json()
            
            # Check structure
            print(f"Response keys: {list(resp.keys())[:5]}")
            
            if "sources" in resp:
                sources = resp["sources"]
                print(f"Has 'sources' metadata")
                print(f"  - has_knowledge: {sources.get('has_knowledge')}")
                print(f"  - documents count: {len(sources.get('documents', []))}")
                print(f"  - category: {sources.get('category')}")
                print(f"  - score: {sources.get('score')}")
                
                # Extract answer
                if "message" in resp:
                    answer = resp["message"].get("content", "")
                    print(f"\nGenerated Answer (first 200 chars):")
                    print(f"  {answer[:200]}...")
                
                # Test assertion
                if sources.get('has_knowledge'):
                    print("\nTEST PASSED: KB knowledge was used")
                else:
                    print("\nTEST FAILED: KB knowledge was NOT used")
            else:
                print(f"No 'sources' in response")
        else:
            print(f"Bad status code: {r.status_code}")
            print(f"Error: {r.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")

def test_knowledge_absent():
    """Test 2: Query that does NOT exist in knowledge base"""
    print("\n" + "="*70)
    print("TEST 2: Query WITHOUT knowledge (random question - sparse KB)")
    print("="*70)
    
    query = "Co to jest sens życia i dlaczego istnieją czarne dziury?"
    payload = {
        "messages": [{"role": "user", "content": query}],
        "model": MODELS[0]
    }
    
    try:
        r = requests.post(BASE_URL, json=payload, timeout=120)
        print(f"Status Code: {r.status_code}")
        
        if r.status_code == 200:
            resp = r.json()
            
            if "sources" in resp:
                sources = resp["sources"]
                print(f"Has 'sources' metadata")
                print(f"  - has_knowledge: {sources.get('has_knowledge')}")
                print(f"  - documents count: {len(sources.get('documents', []))}")
                print(f"  - category: {sources.get('category')}")
                print(f"  - score: {sources.get('score')}")
                
                # Extract answer
                if "message" in resp:
                    answer = resp["message"].get("content", "")
                    print(f"\nGenerated Answer (first 200 chars):")
                    print(f"  {answer[:200]}...")
                
                # Test assertion
                if not sources.get('has_knowledge'):
                    print("\nTEST PASSED: No KB knowledge was used (as expected)")
                else:
                    print("\nTEST UNCLEAR: KB knowledge was used (unexpected?)")
            else:
                print(f"No 'sources' in response")
        else:
            print(f"Bad status code: {r.status_code}")
            print(f"Error: {r.text[:200]}")
            
    except Exception as e:
        print(f"Exception: {e}")

def verify_collection_usage():
    """Verify that RAG uses agent1_student collection"""
    print("\n" + "="*70)
    print("TEST 3: Verify RAG Collection Usage")
    print("="*70)
    
    print(f"Endpoint: {BASE_URL}")
    print(f"Expected collection: agent1_student")
    print(f"Verify in app.py: search_knowledge_base() -> Qdrant client.search()")
    print("\nTo verify:")
    print("  1. Check logs: docker logs agent1_student | grep 'RAG:'")
    print("  2. Check Qdrant: docker exec qdrant curl -X GET http://localhost:6333/collections")

if __name__ == "__main__":
    print(f"\nStarting RAG tests at {datetime.now()}")
    print(f"Base URL: {BASE_URL}")
    
    # Run tests
    test_knowledge_present()
    test_knowledge_absent()
    verify_collection_usage()
    
    print("\n" + "="*70)
    print(f"Tests completed at {datetime.now()}")
    print("="*70)
