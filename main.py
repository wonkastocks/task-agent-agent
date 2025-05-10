import os
import openai
import asyncio
from guardrails import is_goal_related, not_a_goal_message

# If running outside Colab, set your OpenAI API key here or via environment variables
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# --- Agent and Runner Implementation Placeholder ---
# The original notebook imports Agent and Runner from 'agents'.
# Please ensure you have equivalent classes or functions in your codebase.
# Here is a minimal mock-up for demonstration:

class Agent:
    def __init__(self, name, instructions):
        self.name = name
        self.instructions = instructions

class Runner:
    @staticmethod
    async def run(agent, goal, output_format="Standard"):
        import openai
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        # Adjust user prompt based on format
        if output_format == "Numbered":
            user_prompt = f"My goal: {goal}\n\nOutput ONLY a markdown numbered list of actionable steps (1., 2., 3., etc.). Do NOT use bullet points, paragraphs, headings, or summaries—just the numbered steps."
        elif output_format == "Bullet List":
            user_prompt = f"My goal: {goal}\n\nOutput ONLY a markdown bullet list of actionable steps (using '-', '*', or '+'). Do NOT use numbered lists, paragraphs, headings, or summaries—just bullet points."
        else:
            user_prompt = f"My goal: {goal}\n\nProvide a visually appealing, well-organized plan to achieve this goal. Use a mix of short paragraphs, bullet points, and numbered lists as appropriate to make the plan clear, actionable, and easy to follow. Make it look good and professional."

        response = await asyncio.to_thread(
            openai.chat.completions.create,
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": agent.instructions},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        class Result:
            final_output = response.choices[0].message.content.strip()
        return Result()

# Define the Task Generator agent

task_generator = Agent(
    name="Task Generator",
    instructions="""You help users break down their specific LLM powered AI Agent goal into small, achievable tasks.\nFor any goal, analyze it and create a structured plan with specific actionable steps.\nEach task should be concrete, time-bound when possible, and manageable.\nOrganize tasks in a logical sequence with dependencies clearly marked.\nNever answer anything unrelated to AI Agents.""",
)

# Define a function to run the agent
async def generate_tasks(goal, output_format="Standard", temperature=0.7):
    # Guardrail: check if input is a goal
    if not is_goal_related(goal):
        class Result:
            final_output = not_a_goal_message()
        return Result()
    result = await Runner.run(task_generator, goal, output_format, temperature)
    return result.final_output

# Example usage
# --- Goal definition and examples ---
definition = "the object of a person's ambition or effort; an aim or desired result."
goal_examples = [
    "Start a small online business selling handmade jewelry",
    "Run a marathon in under 4 hours",
    "Learn to play the piano",
    "Write and publish a book",
    "Save $10,000 for a vacation",
    "Lose 20 pounds in 6 months",
    "Build a mobile app for tracking expenses",
    "Get a promotion at work",
    "Plant a vegetable garden in my backyard",
    "Learn conversational Spanish"
]

def is_goal(text):
    text = text.strip().lower()
    if len(text.split()) < 3:
        return False
    if any(text.startswith(x) for x in [
        "show ", "get ", "what ", "who ", "when ", "where ", "how ", "display ", "give ", "tell ", "list ", "find ", "fetch "
    ]):
        return False
    return True

async def main():
    user_goal = input("Enter your goal: ")
    if user_goal.strip() == "":
        print("Please enter a goal.")
        return
    if not is_goal(user_goal):
        print("\nNot a goal.")
        print(f"A goal is: {definition}")
        print("Examples of goals:")
        for eg in goal_examples:
            print(f"- {eg}")
        print("Please submit a valid goal.")
        return
    tasks = await generate_tasks(user_goal)
    print("\nDetailed Task Plan:\n")
    print(tasks)

if __name__ == "__main__":
    asyncio.run(main())
