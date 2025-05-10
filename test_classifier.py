# test_classifier.py
# ------------------
# This Streamlit app demonstrates a simple goal classifier and lets you send valid goals to OpenAI's GPT models.
# It is written for beginners, with detailed comments explaining each part of the code.

# --- Import required libraries ---
import streamlit as st  # Streamlit is used to create the web app UI
import openai           # openai is used to interact with OpenAI's GPT models
import os               # os is used to access environment variables
from dotenv import load_dotenv  # dotenv loads environment variables from a .env file

# --- Load environment variables from .env (like your OpenAI API key) ---
load_dotenv(override=True)

# --- Set up Streamlit page configuration (title and layout) ---
st.set_page_config(page_title="Test Classifier", layout="centered")

# --- Main page title and description ---
st.title("🧪 Goal Classifier Test Page")
st.write("This page lets you test a simple goal classifier and send valid goals to OpenAI.")

# --- Sidebar for Model Selection ---
# This section adds a dropdown in the sidebar to let you choose which model to use.
# The CSS block customizes the sidebar's appearance.
st.markdown("""
    <style>
    section[data-testid='stSidebar'] {
        background-color: #EAF4FB !important;
    }
    section[data-testid='stSidebar'] * {
        color: #222 !important;
    }
    .sidebar-model-label {
        font-size: 1.7em;
        font-weight: bold;
        margin-bottom: 0.15em;
        margin-top: 0.4em;
        display: block;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

# List of available models (OpenAI and local models)
MODEL_OPTIONS = [
    "OpenAI API",
    "dolphin-phi:latest",
    "gemma3:1b",
    "smollm:135m",
    "llama3.1:8b",
    "llama2-uncensored:latest",
    "phi3.5:latest",
    "wizard-vicuna-uncensored:30b",
    "dolphin-mistral:latest",
    "llama2-uncensored:7b",
    "llama3.2:3b",
    "llava:latest"
]

# Sidebar label and dropdown selector for models
st.sidebar.markdown('<span class="sidebar-model-label">Choose Model</span>', unsafe_allow_html=True)
selected_model = st.sidebar.selectbox(
    "",  # No visible label for accessibility, but styled above
    MODEL_OPTIONS,
    key="selected_model_test"
)

# Sidebar field for the OpenAI API key
# This allows the user to securely enter their OpenAI API key (not stored anywhere)
api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key",
    type="password",
    value=os.environ.get("OPENAI_API_KEY", "")
)

# --- Classifier Agent ---
# This function checks if the user's input is a valid "goal".
# A goal is defined as something actionable (e.g., "Bake a cake").
def is_goal(text):
    """
    Very basic rule-based classifier for demo purposes.
    Returns True if the input is likely a goal, False otherwise.
    """
    text = text.strip().lower()
    # Require at least 3 words for a goal
    if len(text.split()) < 3:
        return False
    # If the input starts with a common command/question word, it's probably not a goal
    if any(text.startswith(x) for x in [
        "show ", "get ", "what ", "who ", "when ", "where ", "how ", "display ", "give ", "tell ", "list ", "find ", "fetch "
    ]):
        return False
    return True

# --- Main input area ---
# This is where the user types something to test if it's a goal
user_input = st.text_area(
    "Enter something to classify as a goal or not:",
    placeholder="e.g. Bake a cake"
)

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

# --- Main logic when the user clicks 'Submit' ---
if st.button("Submit"):
    # If the input is empty, prompt the user
    if user_input.strip() == "":
        st.warning("Please enter some text.")
    # If the input is NOT a goal, show a styled message with definition and examples
    elif not is_goal(user_input):
        st.markdown(f"""
            <div style='background: #fff; border-radius: 10px; padding: 1.2em 1.5em; margin-top: 1em; color: #222; font-size: 1.08em; box-shadow: 0 2px 12px rgba(0,0,0,0.06); border: 1px solid #e5e7eb;'>
                <div style='font-size:1.3em; font-weight: bold; margin-bottom: 0.3em;'>❌ This is NOT classified as a goal.</div>
                <div style='margin-bottom: 0.7em;'>
                    <span style='font-weight: 500;'>A goal is defined as:</span> <span style='font-style: italic;'>'{definition}'</span>
                </div>
                <div style='font-weight: 500; margin-bottom: 0.2em;'>Examples of goals:</div>
                <ul style='margin-top:0;margin-bottom:0.7em;'>
                    {''.join(f'<li style="margin-bottom:0.18em;">{eg}</li>' for eg in goal_examples)}
                </ul>
                <div style='margin-top:0.7em;'>Please submit a valid goal.</div>
            </div>
        """, unsafe_allow_html=True)
    # If the input IS a goal, send it to OpenAI (if API key provided)
    else:
        if not api_key:
            st.info("Enter your OpenAI API key in the sidebar to enable OpenAI calls.")
        else:
            # Set the OpenAI API key for this session
            openai.api_key = api_key
            # Show a spinner while waiting for the OpenAI response
            # Determine which provider/model is being used for spinner and output
            if selected_model == "OpenAI API" or selected_model.lower() == "gpt-3.5-turbo":
                spinner_message = "Sending to OpenAI..."
                provider_name = "OpenAI"
            else:
                spinner_message = f"Sending to {selected_model}..."
                provider_name = selected_model
            with st.spinner(spinner_message):
                try:
                    # Call OpenAI's chat.completions.create to get a response from the model
                    # This uses the selected model (currently always gpt-3.5-turbo)
                    # Define the model name to use (currently hardcoded, but could be dynamic)
                    model = "gpt-3.5-turbo"
                    response = openai.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "You are an assistant that helps users break down their goals into actionable steps."},
                            {"role": "user", "content": f"My goal: {user_input}\nPlease break this down into actionable steps."}
                        ],
                        max_tokens=300,
                        temperature=0.7
                    )
                    # --- Model Icon and Name Display ---
                    # For OpenAI models, use the OpenAI SVG from Graphics; for others, use the generic AI icon from static.
                    if selected_model == "OpenAI API" or model == "gpt-3.5-turbo":
                        logo_path = "Graphics/openai.svg"  # Local SVG for OpenAI
                        model_cap = model[:1].upper() + model[1:]  # Capitalize model name
                        model_disp = model_cap
                    else:
                        logo_path = "static/ai-generic.png"  # Local PNG for generic/other models
                        model_disp = selected_model
                    # Display the icon, model/provider name, and the word 'response' in a visually aligned row using columns
                    col1, col2, col3 = st.columns([1, 6, 8])
                    with col1:
                        st.image(logo_path, width=28)  # Show model icon
                    with col2:
                        st.markdown(
                            f"<b>{provider_name}</b> <span style='font-size:1.13em; font-weight:600; color:#444;'>response</span>",
                            unsafe_allow_html=True
                        )
                    st.write("")  # Add spacing below the header row
                    # Display the response from the model
                    st.markdown(response.choices[0].message.content.strip())
                except Exception as e:
                    # If there's an error (e.g., invalid API key), show the error message
                    st.error(f"OpenAI API error: {e}")
