"""## Setup"""

!pip install -U -q "google-generativeai>=0.8.2"

import os
import google.generativeai as genai

genai.configure(api_key='key')

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 40,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-pro-002",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

import requests
from bs4 import BeautifulSoup
import time
from IPython.display import display
from IPython.display import Markdown

# Cache to store recommended tasks for different levels and technologies
task_cache = {}

# Define User and Task classes
class User:
    def __init__(self, user_id, username, age):
        self.user_id = user_id
        self.username = username
        self.age = age  # Add age attribute
        self.points = 0  # Initialize points to zero
        self.completed_tasks = []  # List to track completed tasks

    def add_points(self, points):
        """Add points to the user's score"""
        self.points += points

    def complete_task(self, task_id):
        """Record the task as completed by the user"""
        self.completed_tasks.append(task_id)

class Task:
    def __init__(self, task_id, description, difficulty, points, validator, hint=None):
        self.task_id = task_id
        self.description = description  # Task description
        self.difficulty = difficulty  # Difficulty level (e.g., beginner, intermediate, advanced)
        self.points = points  # Points to be awarded for completing the task
        self.validator = validator  # Validation function to check solution
        self.hint = hint  # Hint including breakdown steps and example code

    def validate_solution(self, user_solution):
        """Use the validator function to check if the user's solution is correct"""
        return self.validator(user_solution)

# Function to recommend a task with a specified difficulty level and points
def recommend_task(user, difficulty_level="beginner", technology="Python"):
    """
    Use the Gemini LLM to recommend a task based on user's age, selected difficulty level, and technology.
    Difficulty levels: beginner, intermediate, advanced
    Technologies: Python, JavaScript, etc.
    """
    # Set points based on difficulty level
    points_map = {
        "beginner": 5,
        "intermediate": 10,
        "advanced": 15
    }
    points = points_map.get(difficulty_level, 5)  # Default to 5 points if difficulty is unknown

    # Check cache first
    cache_key = (difficulty_level, technology)
    if cache_key in task_cache:
        print(f"Cache hit: Returning cached task for {difficulty_level} level in {technology}.")
        return task_cache[cache_key]

    # Generate a prompt with user age, difficulty level, and technology
    prompt = (
        f"Please recommend a {difficulty_level} programming task for a {user.age}-year-old student in {technology}. "
        f"The task should be interactive, educational, and engaging for their level, without giving specific hints or code. Only provide one task recommendation please, without any additional options. Thank you!"
    )

    print(f"Sending prompt to Gemini: {prompt}")  # Print the prompt

    # Send prompt to Gemini chat session and receive response
    try:
        response = chat_session.send_message(prompt)

        # Extract task description and hint from the response
        task_description = response.candidates[0].content.parts[0].text
        hint_prompt = (
            f"Please provide a breakdown of steps and example code for solving the task: {task_description}. "
            "This should serve as a hint, not a direct answer. Thank you!"
        )
        hint_response = chat_session.send_message(hint_prompt)
        hint_text = hint_response.candidates[0].content.parts[0].text
        #print(f"Task description extracted: {task_description}")  # Print extracted task description
    except Exception as e:
        print(f"Error occurred while retrieving task: {e}")
        task_description = "Error: Unable to extract task description."
        hint_text = "Error: Unable to extract hint."

    task_id = f"task_{len(user.completed_tasks) + 1}"  # Generate a simple unique task ID

    # Create Task object and store it in cache
    task = Task(task_id, task_description, difficulty_level, points, validator=lambda x: True, hint=hint_text)
    task_cache[cache_key] = task

    return task

# Function to request a hint for a specific task
def request_hint(task):
    """
    Provides breakdown steps and example code as a hint for the given task.
    """
    if task.hint:
        print(f"Hint for Task '{task.task_id}':\n{task.hint}")
    else:
        print("No hint available for this task.")

# Solution validation and task completion function
def complete_task(user, task, user_solution):
    """
    Handles user task completion, validation, and point allocation.
    """
    # Validate user's solution using the task's validator function
    if task.validate_solution(user_solution):
        user.add_points(task.points)  # Award points to the user
        user.complete_task(task.task_id)  # Mark task as completed
        print("--------------------------------------------------\n")
        print(f"Task '{task.task_id}' completed! You earned {task.points} points.")
    else:
        print("Incorrect solution. Please try again.")

# Main function to demonstrate the usage
def main():
    # Create a new user with age attribute and get a recommended task for them
    user = User(user_id=1, username="Zoe", age=10)
    print(f"User profile: {user.username}, Age: {user.age}, Initial Points:{user.points}")  # Print user info

    # Recommend tasks of different difficulty levels
    technology = "Python"  # User-selected technology
    difficulty_level="advanced"
    task1 = recommend_task(user, difficulty_level=difficulty_level, technology=technology)
    print("\n--------------------------------------------------------------------------------------------------------------------------------")
    print(f"\nHere is the coding exercise for {technology} at {difficulty_level} level: {task1.description}")

    # Request hint for task1
    print("\n--------------------------------------------------------------------------------------------------------------------------------")
    print("\nRequesting hint...")
    request_hint(task1)

    # Simulate user completing the task with a correct solution
    user_solution = 4

    complete_task(user, task1, user_solution)

    # Display user's updated points
    print("--------------------------------------------------\n")
    print(f"{user.username} has total {user.points} points.")  # Print final points

# Run the main function
if __name__ == "__main__":
    main()

"""## Call `generate_content`"""



"""<table class="tfo-notebook-buttons" align="left">
  <td>
    <a target="_blank" href="https://ai.google.dev/gemini-api/docs"><img src="https://ai.google.dev/static/site-assets/images/docs/notebook-site-button.png" height="32" width="32" />Docs on ai.google.dev</a>
  </td>
  <td>
    <a target="_blank" href="https://github.com/google-gemini/cookbook/blob/main/quickstarts"><img src="https://www.tensorflow.org/images/GitHub-Mark-32px.png" />More notebooks in the Cookbook</a>
  </td>
</table>

## [optional] Show the conversation

This section displays the conversation received from Google AI Studio.
"""

# @title Show the conversation, in colab.
import mimetypes

def show_file(file_data):
    mime_type = file_data["mime_type"]

    if drive_id := file_data.get("drive_id", None):
        path = next(
            pathlib.Path(f"/gdrive/.shortcut-targets-by-id/{drive_id}").glob("*")
        )
        name = path
        # data = path.read_bytes()
        kwargs = {"filename": path}
    elif url := file_data.get("url", None):
        name = url
        kwargs = {"url": url}
        # response = requests.get(url)
        # data = response.content
    elif data := file_data.get("inline_data", None):
        name = None
        kwargs = {"data": data}
    elif name := file_data.get("filename", None):
        if not pathlib.Path(name).exists():
            raise IOError(
                f"local file: `{name}` does not exist. You can upload files to "
                'Colab using the file manager ("📁 Files"in the left toolbar)'
            )
    else:
        raise ValueError("Either `drive_id`, `url` or `inline_data` must be provided.")

        print(f"File:\n    name: {name}\n    mime_type: {mime_type}\n")
        return

    format = mimetypes.guess_extension(mime_type).strip(".")
    if mime_type.startswith("image/"):
        image = IPython.display.Image(**kwargs, width=256)
        IPython.display.display(image)
        print()
        return

    if mime_type.startswith("audio/"):
        if len(data) < 2**12:
            audio = IPython.display.Audio(**kwargs)
            IPython.display.display(audio)
            print()
            return

    if mime_type.startswith("video/"):
        if len(data) < 2**12:
            audio = IPython.display.Video(**kwargs, mimetype=mime_type)
            IPython.display.display(audio)
            print()
            return

    print(f"File:\n    name: {name}\n    mime_type: {mime_type}\n")


for content in gais_contents:
    if role := content.get("role", None):
        print("Role:", role, "\n")

    for n, part in enumerate(content["parts"]):
        if text := part.get("text", None):
            print(text, "\n")

        elif file_data := part.get("file_data", None):
            show_file(file_data)

    print("-" * 80, "\n")
