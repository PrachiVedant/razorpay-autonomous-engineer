from agents.repair import repair_code


issue = {
    "title": "Fix addition function",
    "body": "The add function should return the sum of two numbers."
}


file_contents = {
    "calculator.py": """
def add(a, b):
    return a - b
"""
}


test_output = """
FAILED tests/test_sample.py::test_addition

AssertionError:
assert add(1, 2) == 3
E       assert -1 == 3
"""


result = repair_code(
    issue,
    file_contents,
    test_output,
)


print("\nREPAIR RESULT")
print("-" * 50)

print("Reasoning:")
print(result["reasoning"])

print("\nChanges:")

for change in result["changes"]:
    print(f"\nFILE: {change['path']}")
    print(change["content"])