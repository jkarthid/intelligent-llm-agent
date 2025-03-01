#!/usr/bin/env python
"""
Local test script for the Intelligent LLM Agent System.
This script simulates a Lambda invocation locally.
"""

import json
import os
import sys
import time
from datetime import datetime

from dotenv import load_dotenv

from src.aws.lambda_handler import lambda_handler

# Load environment variables from .env file
load_dotenv()

def main():
    """Main function to run the local test."""
    # Check if environment variables are set
    required_env_vars = ["LLM_PROVIDER", "LLM_MODEL"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please create a .env file based on .env.example")
        sys.exit(1)
    
    # Create a sample event
    event = {
        "feedback": [
            {
                "feedback_id": "test-" + str(int(time.time())),
                "feedback_text": "I really love your product! The quality is excellent and it has made my life so much easier. However, the delivery was a bit delayed which was frustrating.",
                "customer_name": "John Doe",
                "timestamp": datetime.now().isoformat(),
                "instructions": "Analyze the sentiment and provide a summary."
            }
        ]
    }
    
    # Print the event
    print("Input event:")
    print(json.dumps(event, indent=2))
    print("\n" + "-" * 80 + "\n")
    
    # Invoke the Lambda handler
    try:
        start_time = time.time()
        response = lambda_handler(event, {})
        end_time = time.time()
        
        # Print the response
        print("Response:")
        print(json.dumps(response, indent=2))
        print(f"\nExecution time: {end_time - start_time:.2f} seconds")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
