import csv
import os
import time

LOG_FILE = "logs.csv"

# Function to log request details
def log_request(model_name, tokens_used, cost, time_taken):
    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)

        # Write headers if the file is new
        if not file_exists:
            writer.writerow(["Model", "Tokens Used", "Cost", "Time Taken (ms)"])

        # Log the request
        writer.writerow([model_name, tokens_used, cost, time_taken])
