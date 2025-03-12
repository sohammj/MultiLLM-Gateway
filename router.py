import requests
import time
from config import load_providers
from logger import log_request
from transformers import pipeline

# Initialize the summarization pipeline (ensure you have installed transformers and torch)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

providers = load_providers()

def count_tokens(prompt):
    return len(prompt.split())

def summarize_prompt(prompt, max_length=130, min_length=30):
    """
    Uses a transformer model to summarize a long prompt.
    Adjust max_length and min_length as needed.
    """
    try:
        summary = summarizer(prompt, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print("Summarization error:", e)
        # In case of any error, return the original prompt (fallback)
        return prompt

def optimize_prompt(prompt, threshold=200):
    """
    If the prompt exceeds the threshold (number of tokens), summarize it.
    Otherwise, return the original prompt.
    """
    tokens = prompt.split()
    if len(tokens) > threshold:
        print("Prompt too long; summarizing...")
        return summarize_prompt(prompt)
    return prompt

def call_llm(prompt):
    # Optimize the prompt before processing
    optimized_prompt = optimize_prompt(prompt)
    tokens_used = count_tokens(optimized_prompt)
    
    for provider in providers:
        print(f"Trying provider: {provider['name']}")
        retries = 0
        max_retries = 2
        while retries <= max_retries:
            try:
                start_time = time.time()
                if provider["name"] == "Gemini-Pro":
                    url = provider["api_url"] + "?key=" + provider["api_key"]
                    json_payload = {
                        "contents": [{"parts": [{"text": optimized_prompt}]}]
                    }
                    headers = {"Content-Type": "application/json"}
                else:
                    url = provider["api_url"]
                    json_payload = {"prompt": optimized_prompt, "max_tokens": tokens_used}
                    if "model" in provider:
                        json_payload["model"] = provider["model"]
                    if "huggingface" in provider["api_url"]:
                        json_payload = {"inputs": optimized_prompt}
                    headers = {
                        "Authorization": f"Bearer {provider['api_key']}",
                        "Content-Type": "application/json"
                    }

                response = requests.post(url, headers=headers, json=json_payload, timeout=10)
                end_time = time.time()
                time_taken = int((end_time - start_time) * 1000)

                if response.status_code == 200:
                    response_json = response.json()
                    if provider["name"] == "Gemini-Pro":
                        ai_response = response_json["candidates"][0]["content"]["parts"][0].get("text", "No output generated")
                    else:
                        if "choices" in response_json:
                            ai_response = response_json["choices"][0].get("text", "No output generated")
                        elif isinstance(response_json, list):
                            ai_response = response_json[0].get("generated_text", "No output generated")
                        else:
                            ai_response = "Unexpected response format"

                    cost = provider["cost_per_1k_tokens"] * (tokens_used / 1000)
                    log_request(provider["name"], tokens_used, cost, time_taken, success=True)
                    return {
                        "modelUsed": provider["name"],
                        "response": ai_response,
                        "tokens": tokens_used,
                        "cost": cost,
                        "timeTakenMs": time_taken
                    }
                else:
                    log_request(provider["name"], tokens_used, 0, time_taken, success=False, error_reason=f"status_code_{response.status_code}")
                    retries += 1
                    if retries <= max_retries:
                        print(f"Retrying {provider['name']} (retry {retries})")
                    else:
                        print(f"Exhausted retries for {provider['name']}")
                    continue

            except requests.exceptions.Timeout:
                log_request(provider["name"], tokens_used, 0, int((time.time() - start_time) * 1000), success=False, error_reason="timeout")
                retries += 1
                if retries <= max_retries:
                    print(f"Retrying {provider['name']} (retry {retries})")
                else:
                    print(f"Exhausted retries for {provider['name']}")
                continue
            except Exception as e:
                log_request(provider["name"], tokens_used, 0, int((time.time() - start_time) * 1000), success=False, error_reason=str(e))
                retries += 1
                if retries <= max_retries:
                    print(f"Retrying {provider['name']} (retry {retries})")
                else:
                    print(f"Exhausted retries for {provider['name']}")
                continue

    return {"error": "All providers failed to generate a response"}
