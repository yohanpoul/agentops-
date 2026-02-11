"""
Example: Basic Agent Monitoring with AgentOps
This example shows how to monitor a simple AI agent
"""

import agentops
from openai import OpenAI
import time

# Initialize AgentOps monitoring
agentops.init(
    api_key="demo_key",
    project_name="customer_support_agent"
)

# Initialize your LLM client
client = OpenAI()


@agentops.record_action(action_type="support_chat")
def support_agent(user_message: str) -> str:
    """
    Simple customer support agent
    Automatically monitored by AgentOps
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful customer support agent."},
            {"role": "user", "content": user_message}
        ]
    )
    
    return response.choices[0].message.content


@agentops.record_action(action_type="intent_classification")
def classify_intent(message: str) -> str:
    """Classify user intent (monitored separately)"""
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Classify intent: billing, technical, or general"},
            {"role": "user", "content": message}
        ]
    )
    
    return response.choices[0].message.content


def main():
    print("🤖 Starting Customer Support Agent Demo\n")
    
    # Simulate customer interactions
    test_messages = [
        "I need help with my bill",
        "How do I reset my password?",
        "Your service is down!",
        "Can I upgrade my plan?",
        "Thanks for your help!"
    ]
    
    print("Processing messages...\n")
    
    for msg in test_messages:
        print(f"User: {msg}")
        
        # Classify intent
        intent = classify_intent(msg)
        print(f"Intent: {intent}")
        
        # Get support response
        try:
            response = support_agent(msg)
            print(f"Agent: {response[:100]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)
        time.sleep(1)  # Simulate real-time processing
    
    # Get monitoring stats
    print("\n📊 Monitoring Stats:")
    stats = agentops.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Export events for analysis
    agentops.export_events("agent_events.json")
    print("\n✅ Demo completed!")


if __name__ == "__main__":
    main()
