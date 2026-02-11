"""
Example: Basic Agent Monitoring with AgentOps (No API Key Required)
This example shows how to monitor a simple agent without external APIs
"""

import agentops
import time
import random

# Initialize AgentOps monitoring (no API key needed for local monitoring)
agentops.init(
    api_key="demo_key",
    project_name="demo_agent"
)


@agentops.record_action(action_type="process_data")
def process_data(data: str) -> str:
    """
    Simulate data processing agent
    Automatically monitored by AgentOps
    """
    # Simulate processing time
    time.sleep(random.uniform(0.1, 0.5))
    
    # Simulate success/failure
    if random.random() > 0.8:
        raise Exception("Random processing error")
    
    return f"Processed: {data.upper()}"


@agentops.record_action(action_type="analyze_text")
def analyze_text(text: str) -> dict:
    """Simulate text analysis agent"""
    time.sleep(random.uniform(0.05, 0.3))
    
    word_count = len(text.split())
    char_count = len(text)
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "sentiment": random.choice(["positive", "neutral", "negative"])
    }


def main():
    print("🤖 AgentOps Demo - Basic Monitoring\n")
    print("=" * 50)
    
    # Simulate agent interactions
    test_inputs = [
        "Hello world",
        "This is a test message",
        "AgentOps monitoring example",
        "Simulate data processing",
        "Another test input"
    ]
    
    print("\nProcessing messages...\n")
    
    for i, text in enumerate(test_inputs, 1):
        print(f"[{i}/5] Input: {text}")
        
        # Process data
        try:
            result = process_data(text)
            print(f"      ✓ Processed: {result[:30]}...")
        except Exception as e:
            print(f"      ✗ Error: {e}")
        
        # Analyze text
        try:
            analysis = analyze_text(text)
            print(f"      ✓ Analysis: {analysis['word_count']} words, {analysis['sentiment']}")
        except Exception as e:
            print(f"      ✗ Analysis error: {e}")
        
        print("-" * 50)
        time.sleep(0.5)
    
    # Get monitoring stats
    print("\n📊 Monitoring Stats:")
    print("=" * 50)
    stats = agentops.get_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2f}")
        else:
            print(f"  {key}: {value}")
    
    # Export events for analysis
    print("\n💾 Exporting events...")
    agentops.export_events("agent_events_demo.json")
    print("   Events saved to: agent_events_demo.json")
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\nNext steps:")
    print("  1. Check agent_events_demo.json for detailed logs")
    print("  2. Integrate with your real agent using @agentops.record_action")
    print("  3. See README.md for more examples")


if __name__ == "__main__":
    main()
