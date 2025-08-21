# Add references


def get_agents() -> list[Agent]:
    # Create a summarizer agent
    

    # Create a classifier agent
    

    # Create a recommmended action agent
    

    # Return a list of agents
    

def agent_response_callback(message: ChatMessageContent) -> None:
    print(f"# {message.name}\n{message.content}")


async def main():
    # Initialize the input task
    

    # Create a sequential orchestration with a response callback to observe the output from each agent.
    

    # Create a runtime and start it
    

    # Invoke the orchestration with a task and the runtime
    

    # Wait for the results
    

    # Stop the runtime when idle
    

if __name__ == "__main__":
    asyncio.run(main())