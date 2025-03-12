from router import call_llm

test_prompt = "Tell me a joke."

response = call_llm(test_prompt)

print("API Response:")
print(response)

try:
    with open("logs.csv", "r") as log_file:
        print("\nLogs:")
        print(log_file.read())
except FileNotFoundError:
    print("No logs found yet.")