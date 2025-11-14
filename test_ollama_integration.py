#!/usr/bin/env python3
"""
Test script to validate Ollama integration in FANWS.
This script tests Ollama API connection and generation.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_ollama_connection():
    """Test Ollama server connection"""
    print("=" * 60)
    print("TEST 1: Ollama Server Connection")
    print("=" * 60)
    
    try:
        from src.system.api_manager import get_api_manager
        
        api_manager = get_api_manager()
        print("✓ API manager instance created")
        
        # Check if Ollama is running
        is_available = api_manager.check_ollama_availability()
        
        if is_available:
            print("✓ Ollama server is available at http://localhost:11434")
            return True
        else:
            print("✗ Ollama server is NOT available")
            print("  Please start Ollama with: ollama serve")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ollama_models():
    """Test listing Ollama models"""
    print("\n" + "=" * 60)
    print("TEST 2: List Ollama Models")
    print("=" * 60)
    
    try:
        from src.system.api_manager import get_api_manager
        
        api_manager = get_api_manager()
        
        # List available models
        models = api_manager.list_ollama_models()
        
        if models:
            print(f"✓ Found {len(models)} Ollama model(s):")
            for model in models:
                print(f"  - {model}")
            return True
        else:
            print("✗ No Ollama models found")
            print("  Pull a model with: ollama pull llama2")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ollama_generation():
    """Test Ollama text generation"""
    print("\n" + "=" * 60)
    print("TEST 3: Ollama Text Generation")
    print("=" * 60)
    
    try:
        from src.system.api_manager import get_api_manager
        
        api_manager = get_api_manager()
        
        # Get available models
        models = api_manager.list_ollama_models()
        if not models:
            print("✗ No models available for testing")
            return False
        
        test_model = models[0]
        print(f"Testing with model: {test_model}")
        
        # Simple test prompt
        test_prompt = "Write a single sentence about artificial intelligence."
        print(f"Prompt: {test_prompt}")
        print("Generating... (this may take a minute)")
        
        response = api_manager.generate_text_ollama(
            prompt=test_prompt,
            max_tokens=100,
            model=test_model,
            temperature=0.7
        )
        
        if response and 'choices' in response and response['choices']:
            content = response['choices'][0]['message']['content']
            print(f"✓ Generation successful!")
            print(f"Response: {content[:200]}...")
            
            # Check usage stats
            if 'usage' in response:
                usage = response['usage']
                print(f"Tokens - Prompt: {usage.get('prompt_tokens', 0)}, "
                      f"Completion: {usage.get('completion_tokens', 0)}, "
                      f"Total: {usage.get('total_tokens', 0)}")
            
            return True
        else:
            print("✗ Generation failed - empty response")
            return False
            
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_workflow_ollama_integration():
    """Test workflow integration with Ollama"""
    print("\n" + "=" * 60)
    print("TEST 4: Workflow Ollama Integration")
    print("=" * 60)
    
    try:
        from src.workflow.automated_novel_workflow import AutomatedNovelWorkflowThread
        import tempfile
        
        print("✓ AutomatedNovelWorkflowThread imported")
        
        # Create test workflow with Ollama
        test_dir = tempfile.mkdtemp()
        
        workflow = AutomatedNovelWorkflowThread(
            project_dir=test_dir,
            idea="A sci-fi story about AI",
            tone="Mysterious",
            target_words=50000,
            ai_provider="ollama",
            ollama_model="llama2"
        )
        
        print("✓ Workflow created with Ollama provider")
        
        # Check provider setting
        if workflow.ai_provider == "ollama":
            print(f"✓ Provider set to: {workflow.ai_provider}")
            print(f"✓ Model set to: {workflow.ollama_model}")
        else:
            print(f"⚠ Provider is: {workflow.ai_provider} (expected 'ollama')")
            if workflow.ai_provider == "simulation":
                print("  (This is expected if Ollama server is not running)")
        
        # Check call_ai_api method exists
        if hasattr(workflow, 'call_ai_api'):
            print("✓ call_ai_api() method exists")
        else:
            print("✗ call_ai_api() method missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_provider_switching():
    """Test switching between providers"""
    print("\n" + "=" * 60)
    print("TEST 5: Provider Switching")
    print("=" * 60)
    
    try:
        from src.workflow.automated_novel_workflow import create_workflow_thread
        import tempfile
        
        test_dir = tempfile.mkdtemp()
        
        # Test OpenAI provider
        workflow_openai = create_workflow_thread(
            project_dir=test_dir,
            idea="Test",
            tone="Test",
            target_words=1000,
            ai_provider="openai"
        )
        print(f"✓ Created workflow with provider: {workflow_openai.ai_provider}")
        
        # Test Ollama provider
        workflow_ollama = create_workflow_thread(
            project_dir=test_dir,
            idea="Test",
            tone="Test",
            target_words=1000,
            ai_provider="ollama",
            ollama_model="mistral"
        )
        print(f"✓ Created workflow with provider: {workflow_ollama.ai_provider}")
        print(f"✓ Ollama model: {workflow_ollama.ollama_model}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Ollama integration tests"""
    print("\n")
    print("=" * 60)
    print("FANWS Ollama Integration Test Suite")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Ollama Connection", test_ollama_connection()))
    results.append(("Ollama Models", test_ollama_models()))
    results.append(("Ollama Generation", test_ollama_generation()))
    results.append(("Workflow Integration", test_workflow_ollama_integration()))
    results.append(("Provider Switching", test_provider_switching()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 60)
    
    # Provide helpful messages
    if passed < total:
        print("\n⚠ Some tests failed. Common issues:")
        print("  1. Ollama not installed: curl https://ollama.ai/install.sh | sh")
        print("  2. Ollama not running: ollama serve")
        print("  3. No models installed: ollama pull llama2")
        print("\nFor more info: https://ollama.ai")
    else:
        print("\n🎉 All tests passed! Ollama integration is working perfectly.")
        print("You can now use FANWS with local Ollama models!")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
