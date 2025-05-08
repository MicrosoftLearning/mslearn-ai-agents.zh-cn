import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path


# Add references

def main(): 

    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Load environment variables from .env file
    load_dotenv()
    PROJECT_CONNECTION_STRING= os.getenv("AZURE_AI_AGENT_PROJECT_CONNECTION_STRING")
    MODEL_DEPLOYMENT = os.getenv("AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME")


    # Connect to the Azure AI Foundry project
    


    # Define an agent that can use the custom functions


    
        # Loop until the user types 'quit'
        while True:
            # Get input text
            user_prompt = input("Enter a prompt (or type 'quit' to exit): ")
            if user_prompt.lower() == "quit":
                break
            if len(user_prompt) == 0:
                print("Please enter a prompt.")
                continue

            # Send a prompt to the agent


            # Check the run status for failures

                
            # Show the latest response from the agent


        # Get the conversation history


        # Clean up

    



if __name__ == '__main__': 
    main()