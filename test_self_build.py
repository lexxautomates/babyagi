#!/usr/bin/env python3
"""Test script for self_build functionality"""

from dotenv import load_dotenv
load_dotenv()

import babyagi

# Load the self_build and code_writing_functions packs
babyagi.load_functions('drafts/code_writing_functions')
babyagi.load_functions('drafts/self_build')
print('✓ All packs loaded!')

# Test self_build with a simple persona
print('\nTesting self_build with a sales person persona...')
result = babyagi.self_build('A sales person at an enterprise SaaS company.', 2)

print('\n=== SELF_BUILD RESULT ===')
for r in result:
    print(f"Query: {r['query']}")
    print(f"Output: {r['output']}")
    print('---')