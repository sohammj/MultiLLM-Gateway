import os
import csv
import time

LOG_FILE = "logs.csv"

def log_request(model_name, tokens_used, cost, time_taken, success=True, error_reason=None):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    status = "success" if success else "failure"
    error_reason = error_reason or ""

    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, "a", newline="") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["timestamp", "model", "tokens_used", "cost", "time_taken_ms", "status", "error_reason"])
        writer.writerow([timestamp, model_name, tokens_used, cost, time_taken, status, error_reason])
