import yaml

def load_providers():
    try:
        with open("providers.yaml", "r") as file:
            data = yaml.safe_load(file)

        if data is None or "providers" not in data:
            raise ValueError("Error: `providers.yaml` is empty or incorrectly formatted.")

        providers = data["providers"]
        
        # Debugging: Print loaded providers
        print("Loaded providers:", providers)

        # Sort providers based on cost (cheapest first)
        sorted_providers = sorted(providers, key=lambda x: x["cost_per_1k_tokens"])

        return sorted_providers
    except Exception as e:
        print("Error loading providers.yaml:", e)
        return []
