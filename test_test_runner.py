print("TEST SCRIPT STARTED")

from agents.test_runner import run_tests

print("IMPORT SUCCESS")

print("ABOUT TO RUN TESTS")

result = run_tests(
    "pytest tests/"
)

print("TESTS FINISHED")

print("\nTEST RESULT")
print("-" * 50)

print(f"Passed: {result['passed']}")
print(f"Return code: {result['return_code']}")

print("\nSTDOUT:")
print(result["stdout"])

print("\nSTDERR:")
print(result["stderr"])