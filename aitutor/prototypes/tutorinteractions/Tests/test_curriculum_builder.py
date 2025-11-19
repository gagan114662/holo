#!/usr/bin/env python3
"""
Test script for Curriculum Builder Agent
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from CurriculumBuilderAgent import CurriculumBuilderAgent

def main():
    print("🧪 Testing Curriculum Builder Agent")
    print("=" * 50)
    
    try:
        # Initialize agent
        print("\n📚 Initializing Curriculum Builder Agent...")
        agent = CurriculumBuilderAgent()
        print("✅ Agent initialized successfully!")
        
        # Test finding questions for basic addition
        grade_level = "GRADE_1"
        skill_id = "addition_basic"
        
        print(f"\n🔍 Searching for new questions...")
        print(f"Grade: {grade_level}")
        print(f"Skill: {skill_id}")
        
        new_questions = agent.find_new_questions(
            grade_level=grade_level,
            skill_id=skill_id, 
            num_questions=3
        )
        
        print(f"\n✨ Found {len(new_questions)} new questions:")
        
        if len(new_questions) == 0:
            print("❌ No new questions were found!")
            print("\n💡 This could mean:")
            print("   1. OER/IXL scrapers need API keys or are being blocked")
            print("   2. No suitable content found for this skill")
            print("   3. All found questions were duplicates")
            print("\n❌ Test completed with no results")
            return False
        
        for i, question in enumerate(new_questions, 1):
            print(f"\n{i}. ID: {question['question_id']}")
            print(f"   Question: {question['content']}")
            print(f"   Answer: {question['correct_answer']}")
            print(f"   Source: {question['metadata'].get('source_url', 'N/A')}")
        
        # Optionally add to curriculum (commented out to avoid modifying curriculum during testing)
        # print(f"\n💾 Adding questions to curriculum...")
        # agent.add_questions_to_curriculum(grade_level, skill_id, new_questions)
        # print("✅ Questions added to curriculum!")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Internet connection for OER/IXL access")
        print("   2. Valid curriculum.json file")
        print("   3. All required dependencies installed")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)