#!/usr/bin/env python3
"""
Simple test script for workflow coordinator
"""

from src.workflow_coordinator import WorkflowCoordinator

print("Creating coordinator...")
wc = WorkflowCoordinator()
print(f"Initialized: {wc.is_initialized}")
print(f"Steps available: {len(wc.get_workflow_steps())}")

steps = wc.get_workflow_steps()
if steps:
    print(f"First step: {steps[0]['name']}")
    print(f"Last step: {steps[-1]['name']}")

print("Test completed successfully!")

# Test initialization
print("\nTesting initialization...")
result = wc.initialize()
print(f"Initialization result: {result}")
print(f"Is initialized: {wc.is_initialized}")

if wc.is_initialized:
    steps = wc.get_workflow_steps()
    print(f"Steps after initialization: {len(steps)}")
    if steps:
        for i, step in enumerate(steps[:3]):  # Show first 3 steps
            print(f"  Step {step['number']}: {step['name']}")
