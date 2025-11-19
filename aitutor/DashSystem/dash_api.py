import time
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from DashSystem.dash_system import DASHSystem, Question

app = FastAPI()
dash_system = DASHSystem()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows the React frontend to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/next-question/{user_id}", response_model=Question)
def get_next_question(user_id: str):
    """
    Gets the next recommended question for a given user.
    """
    # Ensure the user exists and is loaded
    dash_system.load_user_or_create(user_id)
    
    # Get the next question
    next_question = dash_system.get_next_question(user_id, time.time())
    
    if next_question:
        return next_question
    else:
        # If no specific question is recommended, you could return a default
        # or a message indicating the student is proficient in all areas.
        # For now, we'll return a 404, but this can be improved.
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No recommended question found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
