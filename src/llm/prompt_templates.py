"""System prompts and prompt templates for the agent."""

SYSTEM_PROMPT = """You are a helpful AI assistant specialized in Secret Network.
You have access to Secret Network tools and knowledge.
Help users with their questions and tasks related to Secret Network."""

INTENT_CLASSIFICATION_PROMPT = """Classify the user's intent into one of the following categories:
- information: User is asking for information
- transaction: User wants to perform a transaction
- query: User wants to query blockchain data
- contract: User wants to interact with a contract
- other: Other intents

User input: {user_input}

Intent:"""

PLANNING_PROMPT = """Create a step-by-step plan to accomplish the following task:

Task: {task}
Intent: {intent}

Plan:"""

# TODO: Add more prompt templates as needed
