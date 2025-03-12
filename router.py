import requests
import time
from config import load_providers
from logger import log_request

# Load AI providers
providers = load_providers()

# Function to call the cheapest available AI model
def call_llm(prompt):
    for provider in providers:
        print(f"Trying provider: {provider['name']}")  # Debugging

        try:
            # Start timing the API request
            start_time = time.time()

            # Prepare request payload
            # For Gemini, we use a different format
            if provider["name"] == "Gemini-Pro":
                # Append the API key as query parameter already handled in URL by our YAML?
                # Otherwise, you may need to append here.
                url = provider["api_url"] + "?key=" + provider["api_key"]
                json_payload = {
                    "contents": [
                        {
                            "parts": [
                                {"text": prompt}
                            ]
                        }
                    ]
                }
                headers = {"Content-Type": "application/json"}
            else:
                url = provider["api_url"]
                json_payload = {"prompt": prompt, "max_tokens": 100}
                if "model" in provider and provider["model"]:
                    json_payload["model"] = provider["model"]
                # Hugging Face uses "inputs" instead of "prompt"
                if "huggingface" in provider["api_url"]:
                    json_payload = {"inputs": prompt}
                headers = {
                    "Authorization": f"Bearer {provider['api_key']}",
                    "Content-Type": "application/json"
                }

            # Make the API request
            response = requests.post(url, headers=headers, json=json_payload)

            # End timing the request
            end_time = time.time()
            time_taken = int((end_time - start_time) * 1000)  # in milliseconds

            print(f"Response from {provider['name']}: {response.status_code} - {response.text}")

            if response.status_code == 200:
                response_json = response.json()

                # Handle Gemini-Pro response differently
                if provider["name"] == "Gemini-Pro":
                    if isinstance(response_json, dict) and "candidates" in response_json:
                        candidate = response_json["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                            ai_response = candidate["content"]["parts"][0].get("text", "No output generated")
                        else:
                            ai_response = "No output generated"
                    else:
                        ai_response = "Unexpected Gemini response format"
                else:
                    # Handle other provider responses
                    if isinstance(response_json, dict) and "choices" in response_json:
                        ai_response = response_json["choices"][0].get("text", "No output generated")
                    elif isinstance(response_json, list):
                        ai_response = response_json[0].get("generated_text", "No output generated")
                    else:
                        ai_response = "Unexpected response format"

                tokens_used = 100  # Approximate token usage
                cost = provider["cost_per_1k_tokens"] * (tokens_used / 1000)

                # Log the request
                log_request(provider["name"], tokens_used, cost, time_taken)

                return {
                    "modelUsed": provider["name"],
                    "response": ai_response,
                    "tokens": tokens_used,
                    "cost": cost,
                    "timeTakenMs": time_taken
                }

        except Exception as e:
            print(f"Error with {provider['name']}: {e}")

    return {"error": "All providers failed"}

if __name__ == "__main__":
    test_prompt = "Tell me a joke."
    resp = call_llm(test_prompt)
    print("API Response:")
    print(resp)
