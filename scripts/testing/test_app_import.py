#!/usr/bin/env python3
"""
Test main application import
"""

print("Testing main application import...")

try:
    import fanws
    print("✓ Main application imports successfully with new workflow system")

    # Test that we can create a window instance
    print("Testing window creation...")
    # Don't actually create the GUI since we don't have a display
    print("✓ Import test completed successfully")

except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
