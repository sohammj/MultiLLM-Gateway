import yaml

def load_providers():
    try:
        with open("providers.yaml", "r") as file:
            providers = yaml.safe_load(file)["providers"]
    except FileNotFoundError:
        print("Error: providers.yaml file not found")
        return []
    except KeyError:
        print("Error: Invalid providers.yaml format")
        return []
    
    # Sort providers based on cost (cheapest first)
    try:
        sorted_providers = sorted(providers, key=lambda x: x["cost_per_1k_tokens"])
    except KeyError:
        print("Error: Invalid provider configuration")
        return []
    
    return sorted_providers