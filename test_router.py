from router import call_llm

# Test prompt
test_prompt = "Tell me a joke."

# Call API
response = call_llm(test_prompt)

# Print response
print("API Response:")
print(response)

# Check logs
try:
    with open("logs.csv", "r") as log_file:
        print("\nLogs:")
        print(log_file.read())
except FileNotFoundError:
    print("No logs found yet.")