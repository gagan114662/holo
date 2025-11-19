#!/usr/bin/env python3
"""
Test script for Question Generator Agent
"""

import sys
import os
import random
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from QuestionGeneratorAgent import QuestionGeneratorAgent

def main():
    print("🧪 Testing Question Generator Agent")
    print("=" * 50)
    
    # Note: Make sure you have set your OPENROUTER_API_KEY in .env file
    
    try:
        # Initialize generator
        print("\n📚 Initializing Question Generator Agent...")
        generator = QuestionGeneratorAgent()
        print("✅ Agent initialized successfully!")
        
        # Get all available question IDs
        all_question_ids = []
        with open('curriculum.json', 'r') as f:
            curriculum = json.load(f)
            for grade_data in curriculum['grades'].values():
                for skill_data in grade_data['skills']:
                    for question in skill_data['questions']:
                        all_question_ids.append(question['question_id'])
        
        # Randomly select a question
        source_question_id = random.choice(all_question_ids)
        source_question = generator._find_question(source_question_id)
        
        print(f"\n🎯 Randomly selected question: {source_question_id}")
        print(f"📋 Original Question: {source_question['content']}")
        print(f"✅ Original Answer: {source_question['correct_answer']}")
        print(f"\n🔄 Generating {3} variations...")
        
        # Determine subject based on question content (simple heuristic)
        subject = "math"  # Default to math for most K-12 curriculum
        if any(word in source_question['content'].lower() for word in ['history', 'president', 'war', 'country']):
            subject = "history"
        elif any(word in source_question['content'].lower() for word in ['science', 'element', 'atom', 'cell']):
            subject = "science"
        
        generated_ids = generator.generate_variations(
            source_question_id, 
            num_variations=3,
            subject=subject
        )
        
        print(f"\n✨ Generated {len(generated_ids)} variations for {subject}:")
        
        if len(generated_ids) == 0:
            print("❌ No variations were generated!")
            print("\n💡 This usually means:")
            print("   1. OpenRouter API authentication failed")
            print("   2. Run: python Tests/test_openrouter.py to diagnose")
            print("\n❌ Test FAILED!")
            return False
        
        for qid in generated_ids:
            question = generator._find_question(qid)
            if question:
                print(f"\n  📝 ID: {qid}")
                print(f"     Question: {question['content']}")
                print(f"     Answer: {question['correct_answer']}")
                if 'metadata' in question:
                    print(f"     Explanation: {question['metadata'].get('explanation', 'N/A')}")
        
        print("\n✅ Test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\n💡 Make sure you have:")
        print("   1. Set OPENROUTER_API_KEY in your .env file")
        print("   2. Installed required packages: pip install requests python-dotenv")
        print("   3. Run: python Tests/test_openrouter.py to diagnose API issues")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)