#!/usr/bin/env python3
"""
Curriculum Developer Agent - Uses AutomatedComputerUseAgent to navigate to IXL
"""
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from AutomatedComputerUseAgent import create_agent

def main():
    """Main function to run the curriculum developer agent"""
    print("=== Curriculum Developer Agent ===")
    print("Using Natural Language Automation to navigate to IXL\n")
    
    # Create automated computer agent
    agent = create_agent()
    
    # Define curriculum development workflow using natural language
    workflow = [
        "open Chrome",
        "wait 5 seconds",
        "click on Vandan's profile",
        "wait 2 seconds", 
        "navigate to ixl.com",
        "wait 3 seconds",
        "find the Math section"
    ]
    
    print("🚀 Executing curriculum development workflow...")
    print("📝 Steps:")
    for i, step in enumerate(workflow, 1):
        print(f"   {i}. {step}")
    print()
    
    # Execute the workflow
    success = agent.execute_instructions(workflow)
    
    if success:
        print("\n✅ Successfully navigated to IXL!")
        print("\n🎯 Curriculum Developer Agent can now:")
        print("   - Analyze IXL content using vision")
        print("   - Extract questions and skills")
        print("   - Build curriculum data")
        print("   - Use natural language commands for complex navigation")
        
        # Demonstrate additional natural language capabilities
        print("\n🔍 Demonstrating additional automation...")
        agent.execute_instruction("find the Grade 3 section")
        agent.execute_instruction("wait 2 seconds")
        agent.execute_instruction("find the multiplication section")
        
    else:
        print("\n❌ Some steps in the workflow failed")
        print("Check the logs above for details")
    
    print("\n🏁 Curriculum Developer Agent completed!")

if __name__ == "__main__":
    main()