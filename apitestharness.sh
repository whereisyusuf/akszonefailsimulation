#!/bin/bash

# Configuration
URL="http://<your-ip-address-here>/mysql-data"  # Replace with your API endpoint
INTERVAL=0.25  # Interval in seconds between requests
MAX_FAILURE_DURATION=300  # Maximum failure state duration in seconds

# Variables
start_failure_time=0
end_failure_time=0
is_in_failure=0

echo "Monitoring API at $URL..."

while true; do
  # Get HTTP status code with a timeout
  if ! status_code=$(curl -o /dev/null -s -w "%{http_code}" --max-time 5 "$URL"); then
    echo "$(date): Failed to connect to the API."
    status_code=0  # Treat as a failure
  fi
  echo "Status Code: $status_code"  # Debug output

  # Check for failure
  if [[ "$status_code" -ne 200 ]]; then
    echo "Non-200 status detected: $status_code"
    if [[ $is_in_failure -eq 0 ]]; then
      # First failure detected
      start_failure_time=$(date +%s)
      echo "$(date): API entered failure state with status $status_code"
      is_in_failure=1
    fi
  else
    echo "API is successful"
    # API is successful
    if [[ $is_in_failure -eq 1 ]]; then
      # Recovery detected
      if [[ $end_failure_time -eq 0 ]]; then
        end_failure_time=$(date +%s)
        recovery_time=$((end_failure_time - start_failure_time))
        echo "$(date): API recovered. Downtime: ${recovery_time} seconds"
        is_in_failure=0
        start_failure_time=0
        end_failure_time=0
      fi
    fi
  fi

  # Check for excessive failure time
  if [[ $is_in_failure -eq 1 ]]; then
    current_time=$(date +%s)
    if (( current_time - start_failure_time > MAX_FAILURE_DURATION )); then
      echo "$(date): Failure state exceeded max duration. Resetting state."
      is_in_failure=0
      start_failure_time=0
      end_failure_time=0
    fi
  fi

  sleep $INTERVAL
done
