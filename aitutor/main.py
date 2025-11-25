import time
import random
from DashSystem.dash_system import DASHSystem

def main():
    """
    Main function to run the AI Tutor simulation.
    """
    user_id = "student123"
    dash_system = DASHSystem()

    # Load or create the user profile
    user_profile = dash_system.load_user_or_create(user_id)
    print(f"Welcome, {user_id}!")

    while True:
        # Get the next question
        current_time = time.time()
        next_question = dash_system.get_next_question(user_id, current_time)

        if not next_question:
            print("No more recommended questions. You're doing great!")
            break

        # Display the question
        print("\n" + "="*20)
        print(f"Question ID: {next_question.question_id}")
        print(f"Skills: {', '.join(next_question.skill_ids)}")
        print(f"Question: {next_question.content}")

        # Simulate user input
        start_time = time.time()
        # A real implementation would get input: user_answer = input("Your answer: ")
        # For this simulation, we'll randomize the answer
        is_correct = random.choice([True, False])
        end_time = time.time()

        response_time_seconds = end_time - start_time

        # Record the attempt
        dash_system.record_question_attempt(
            user_profile,
            next_question.question_id,
            next_question.skill_ids,
            is_correct,
            response_time_seconds
        )

        print(f"Your answer was {'Correct' if is_correct else 'Incorrect'}.")
        print(f"Response time: {response_time_seconds:.2f} seconds.")

        # Optional: Display updated skill scores
        # scores = dash_system.get_skill_scores(user_id, time.time())
        # print("\nUpdated Skill Scores:")
        # for skill_id, score in scores.items():
        #     if score['practice_count'] > 0:
        #         print(f"  - {score['name']}: Probability {score['probability']:.2f}")

        # Pause for a moment to simulate a real user
        time.sleep(2)

if __name__ == "__main__":
    main()
