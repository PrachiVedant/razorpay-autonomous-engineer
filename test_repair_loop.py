from agents.repair_loop import repair_loop
from agents.repository import write_file


issue = {
    "title": "Fix addition function",
    "body": "The add function should return the sum of two numbers."
}


changed_files = [
    {
        "path": "calculator.py",
        "content": """def add(a, b):
    return a - b
"""
    }
]


# Create the intentionally broken file
write_file(
    "calculator.py",
    changed_files[0]["content"],
)


result = repair_loop(
    issue=issue,
    changed_files=changed_files,
    test_command="pytest tests/",
)


print("\n")
print("=" * 60)
print("FINAL RESULT")
print("=" * 60)

print(
    f"Success: {result['success']}"
)

print(
    f"Attempts: {result['attempts']}"
)