#!/usr/bin/env python3
"""
Minimal test to isolate the recursion error
"""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("Testing minimal AI provider initialization...")

try:
    from ai_provider_abstraction import initialize_multi_provider_ai
    print("✓ AI provider module imported successfully")

    print("Calling initialize_multi_provider_ai()...")
    result = initialize_multi_provider_ai()
    print(f"✓ Function returned: {result}")
    print(f"✓ Result type: {type(result)}")

    # Test if we can access the result
    print(f"✓ Providers dict: {result.providers}")
    print(f"✓ Default provider: {result.default_provider}")

    print("✓ All tests passed - no recursion error")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
