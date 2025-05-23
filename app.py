# test_classifier.py
# ------------------
# This Streamlit app demonstrates a simple goal classifier and lets you send valid goals to OpenAI's GPT models.
# It is written for beginners, with detailed comments explaining each part of the code.

# --- Import required libraries ---
import streamlit as st  # Streamlit is used to create the web app UI
import openai           # openai is used to interact with OpenAI's GPT models
import os               # os is used to access environment variables
from dotenv import load_dotenv  # dotenv loads environment variables from a .env file

# ===================================================
# LOAD ENVIRONMENT VARIABLES
# ===================================================
# Load environment variables from a .env file
# This is useful for storing sensitive information like API keys
# The override parameter is set to True to ensure the variables are loaded
load_dotenv(override=True)

# ===================================================
# SET PAGE CONFIGURATION
# ===================================================
# Set the page configuration - MUST be called before any other Streamlit commands
# This configures the page title that appears in the browser tab
# and sets the layout to centered (vs. wide)
st.set_page_config(page_title="Achieve your Goals", layout="centered")

# ===================================================
# CUSTOM CSS FOR APP STYLING
# ===================================================
# This block adds custom CSS to optimize the app's appearance
# It reduces vertical spacing and improves the overall layout
st.markdown("""
<style>
    /* ===== CONTAINER SPACING ===== */
    /* Set appropriate padding for the main container to prevent content from being cut off */
    /* Top padding ensures the title is fully visible */
    /* Bottom padding ensures there's enough space at the bottom of the page for content */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 3rem !important;
    }
    
    /* ===== BUTTON STYLING ===== */
    /* Reduce the vertical space around buttons to make the interface more compact */
    /* The !important flag ensures these styles override Streamlit's default styling */
    div.stButton > button {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    
    /* ===== ELEMENT CONTAINERS ===== */
    /* Reduce spacing between general Streamlit elements for a more compact layout */
    .element-container {
        margin-bottom: 0.3rem !important;
    }
    
    /* ===== RADIO BUTTON STYLING ===== */
    /* Minimize space around radio button groups while keeping them readable */
    .stRadio > div {
        margin-top: 0.1rem !important;
        margin-bottom: 0.1rem !important;
    }
    
    /* ===== TEXT AREA STYLING ===== */
    /* Reduce spacing around text input areas */
    .stTextArea > div {
        margin-bottom: 0.1rem !important;
    }
    
    /* ===== HEADING STYLING ===== */
    /* Make the title (h1) more compact while maintaining readability */
    /* Reduced font size and line height for better space efficiency */
    h1 {
        margin-top: 0 !important;
        margin-bottom: 0.1rem !important;
        font-size: 1.6rem !important;
        line-height: 1.2 !important;
    }
    
    /* ===== PARAGRAPH STYLING ===== */
    /* Optimize paragraph spacing for readability while minimizing vertical space */
    p {
        margin-bottom: 0.5rem !important;
        margin-top: 0 !important;
        line-height: 1.3 !important;
    }
    
    /* ===== OUTPUT CONTENT STYLING ===== */
    /* Ensure the markdown output (AI responses) has proper spacing */
    .stMarkdown {
        margin-bottom: 1rem !important;
    }
    
    /* Ensure list items in the output have proper spacing between them */
    /* This improves readability of bullet points and numbered lists */
    .stMarkdown li {
        margin-bottom: 0.5rem !important;
    }
    
    /* Add appropriate spacing for containers that hold markdown content */
    /* This ensures AI responses have enough breathing room */
    .element-container:has(.stMarkdown) {
        margin-bottom: 2rem !important;
    }
    
    /* Ensure there's enough space at the bottom of the page for scrolling */
    /* This prevents content from being cut off at the bottom */
    .main .block-container {
        padding-bottom: 5rem !important;
    }
    
    /* ===== FORM STYLING ===== */
    /* Remove extra padding in form elements to make them more compact */
    .stForm {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    
    /* Optimize spacing for text input labels */
    .stTextInput > label {
        margin-bottom: 0 !important;
        line-height: 1 !important;
    }
    
    /* Optimize text area size and padding */
    /* Minimum height ensures enough space for user input while being compact */
    textarea {
        padding: 0.3rem !important;
        min-height: 5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ===================================================
# MAIN PAGE HEADER AND DESCRIPTION
# ===================================================
# Display the main title with a racing flag emoji to represent achievement
# The title is the first thing users see and establishes the app's purpose
st.title("🏁 Achieve your Goals")

# Add a concise description below the title
# - Uses custom styling to reduce space between title and description
# - Explains the app's purpose in a simple, user-friendly way
# - unsafe_allow_html=True allows the use of HTML for styling
st.markdown("<p style='margin-top:-0.5rem; font-size:0.95rem;'>This page allows you to enter your goals and gives you a concrete plan to achieve them.</p>", unsafe_allow_html=True)

# ===================================================
# SIDEBAR CONFIGURATION
# ===================================================
# The sidebar contains model selection options and temperature controls
# It's separated from the main content area for a cleaner interface
# Apply custom styling to the sidebar
# This CSS customizes the appearance of the sidebar where model selection and API key input are located
st.markdown("""
    <style>
    /* Set a light blue background color for the sidebar */
    /* This creates a visual separation between the sidebar and main content */
    section[data-testid='stSidebar'] {
        background-color: #EAF4FB !important;
    }
    
    /* Set dark text color for all sidebar elements for better readability */
    section[data-testid='stSidebar'] * {
        color: #222 !important;
    }
    
    /* Style for the model selection label in the sidebar */
    /* Makes the label more prominent with larger font and proper spacing */
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

# ===================================================
# MODEL OPTIONS CONFIGURATION
# ===================================================
# Define the list of available AI models that can be selected in the sidebar
# This includes OpenAI's API and various locally-hosted models
# The first option (OpenAI API) requires an API key, while others use local processing
MODEL_OPTIONS = [
    "OpenAI API",      # Uses OpenAI's cloud-based models (requires API key)
    "dolphin-phi:latest",  # Local Dolphin-Phi model
    "gemma3:1b",       # Google's Gemma 1B parameter model
    "smollm:135m",     # Small language model (135M parameters)
    "llama3.1:8b",     # Meta's LLaMA 3.1 (8B parameters)
    "llama2-uncensored:latest",  # Uncensored version of LLaMA 2
    "phi3.5:latest",   # Microsoft's Phi-3.5 model
    "wizard-vicuna-uncensored:30b",  # Large 30B parameter model
    "dolphin-mistral:latest",  # Dolphin model based on Mistral architecture
    "llama2-uncensored:7b",    # Smaller 7B parameter version of LLaMA 2 uncensored
    "llama3.2:3b",            # Compact 3B parameter version of LLaMA 3.2
    "llava:latest"             # Multimodal model that can process both text and images
]

# ===================================================
# SIDEBAR MODEL SELECTION UI
# ===================================================
# Add a styled heading for the model selection dropdown
# The 'sidebar-model-label' class applies the custom styling defined earlier
st.sidebar.markdown('<span class="sidebar-model-label">Choose Model</span>', unsafe_allow_html=True)

# Create a dropdown (selectbox) for model selection
# - Empty label ("") keeps the interface clean since we already have a heading
# - MODEL_OPTIONS provides the list of available models
# - key="selected_model" gives this element a unique identifier for Streamlit
selected_model = st.sidebar.selectbox(
    "",  # No visible label for accessibility, but styled above
    MODEL_OPTIONS,
    key="selected_model_test"
)

# ===================================================
# API KEY INPUT FIELD
# ===================================================
# Create a password-type text input field for the OpenAI API key
# - Password type ensures the API key is masked for security
# - Default value is loaded from environment variables if available
# - The API key is never stored permanently - only kept in session memory
api_key = st.sidebar.text_input(
    "Enter your OpenAI API Key",
    type="password",  # Masks the input for security
    value=os.environ.get("OPENAI_API_KEY", "")  # Pre-fill from environment if available
)

# ===================================================
# TEMPERATURE CONTROL SLIDER
# ===================================================
# Add a heading for the temperature slider with custom styling
# Temperature controls the randomness/creativity of the AI's responses
st.sidebar.markdown('<div style="margin-top:1.5em; margin-bottom:0.3em;"><strong>Model Temperature</strong></div>', unsafe_allow_html=True)

# Create a slider for adjusting the model's temperature parameter
# - Range from 0.0 (deterministic) to 1.0 (creative)
# - Default value of 0.7 provides a good balance
# - Help text explains what temperature does in user-friendly terms
model_temperature = st.sidebar.slider(
    "",  # Empty label (heading is provided above)
    min_value=0.0,  # Minimum temperature (most deterministic)
    max_value=1.0,  # Maximum temperature (most random/creative)
    value=0.7,      # Default value - balanced creativity
    step=0.1,       # Increment by 0.1
    help="Controls randomness: lower values = more focused and predictable; higher = more creative and diverse."
)

# ===================================================
# GOAL CLASSIFIER FUNCTION
# ===================================================
# This function determines if the user's input is a valid goal
# A goal should be actionable and represent something the user wants to achieve
# Examples of valid goals: "Bake a cake", "Learn Spanish", "Start a business"
def is_goal(text):
    """
    Very basic rule-based classifier for demo purposes.
    Returns True if the input is likely a goal, False otherwise.
    
    This function implements a simple heuristic approach to determine if text represents a goal:
    1. It checks if the input has enough substance (at least 3 words)
    2. It filters out common question/command patterns that aren't goals
    
    A more sophisticated implementation could use NLP techniques or a trained model.
    """
    # Normalize the text by removing extra whitespace and converting to lowercase
    # This ensures consistent processing regardless of input format
    text = text.strip().lower()
    
    # Check if the input has enough substance to be a goal
    # Goals typically need at least a few words to express an actionable intent
    if len(text.split()) < 3:
        return False
    
    # Filter out inputs that start with question or command words
    # These patterns typically indicate queries or commands rather than goals
    # For example: "what is the weather" or "show me directions" aren't goals
    if any(text.startswith(x) for x in [
        "show ", "get ", "what ", "who ", "when ", "where ", "how ", 
        "display ", "give ", "tell ", "list ", "find ", "fetch "
    ]):
        return False
    
    # If the input passes all filters, consider it a valid goal
    return True

# ===================================================
# MAIN INPUT AREA
# ===================================================
# Create a text area for users to enter their goals
# This is the primary input mechanism for the application
user_input = st.text_area(
    "Enter your goal:",                # Label shown above the input field
    placeholder="e.g. Bake a cake",   # Example text shown when field is empty
    height=68                         # Height in pixels (68 is Streamlit's minimum)
)

# ===================================================
# SUBMIT BUTTON
# ===================================================
# Create a button that users click to process their input
# When clicked, this triggers the goal validation and API request flow
submit_button = st.button("Submit")

# ===================================================
# OUTPUT FORMAT SELECTION
# ===================================================
# Add a heading for the output format options with minimal spacing
# This allows users to choose how they want their task breakdown formatted
st.write("""<div style='margin-top: 0.1em; margin-bottom: 0.1em;'><strong>Select Output Format:</strong></div>""", unsafe_allow_html=True)

# Create radio buttons for selecting the output format
# - Standard: Mix of paragraphs, bullet points, and numbered lists
# - Bullet List: Entire response formatted as bullet points
# - Numbered List: Sequential steps presented as a numbered list
output_format = st.radio(
    "",                                  # Empty label (heading is provided above)
    ["Standard", "Bullet List", "Numbered List"],  # Available format options
    horizontal=True,                      # Display options horizontally
    index=0,                              # Default to Standard format
    key="output_format"                   # Unique identifier for this component
)

# ===================================================
# GOAL DEFINITION AND EXAMPLES
# ===================================================
# Define what constitutes a "goal" for the purpose of this application
# This definition is shown to users when their input is not recognized as a goal
definition = "the object of a person's ambition or effort; an aim or desired result."

# Provide a list of example goals to help users understand what inputs are valid
# These examples cover various domains like business, fitness, learning, etc.
# They demonstrate the expected format and level of specificity for goals
goal_examples = [
    "Start a small online business selling handmade jewelry",  # Business goal
    "Run a marathon in under 4 hours",                      # Fitness goal with specific metric
    "Learn to play the piano",                              # Skill acquisition
    "Write and publish a book",                             # Creative project
    "Save $10,000 for a vacation",                          # Financial goal
    "Lose 20 pounds in 6 months",                           # Health goal with timeframe
    "Build a mobile app for tracking expenses",              # Technical project
    "Get a promotion at work",                               # Career goal
    "Plant a vegetable garden in my backyard",               # Hobby/lifestyle goal
    "Learn conversational Spanish"                           # Language learning
]

# ===================================================
# MAIN APPLICATION LOGIC
# ===================================================
# This section contains the core logic that runs when the user submits their input
# It validates the input, processes it if valid, and displays appropriate feedback
if submit_button:
    # -----------------------------------------------
    # EMPTY INPUT VALIDATION
    # -----------------------------------------------
    # Check if the user submitted an empty input
    # If so, display a warning message prompting them to enter text
    if user_input.strip() == "":
        st.warning("Please enter some text.")
        
    # -----------------------------------------------
    # INVALID GOAL HANDLING
    # -----------------------------------------------
    # If the input doesn't meet our criteria for a goal (using the is_goal function)
    # Show a styled message explaining what constitutes a valid goal with examples
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
        
    # -----------------------------------------------
    # VALID GOAL PROCESSING
    # -----------------------------------------------
    # If the input is a valid goal, proceed with processing it
    # This will involve sending the goal to the AI model for generating a plan
    else:
        # -----------------------------------------------
        # API KEY VALIDATION
        # -----------------------------------------------
        # Check if the user has provided an API key
        # If not, display a message prompting them to enter one
        if not api_key:
            st.info("Enter your OpenAI API key in the sidebar to enable OpenAI calls.")
        else:
            # -----------------------------------------------
            # API KEY CONFIGURATION
            # -----------------------------------------------
            # Set the OpenAI API key for this session using the provided key
            # This key is not stored permanently and only exists for the current session
            openai.api_key = api_key
            
            # -----------------------------------------------
            # MODEL SELECTION AND DISPLAY PREPARATION
            # -----------------------------------------------
            # Determine which provider/model is being used to customize the UI
            # This affects the spinner message and the provider name shown with the response
            if selected_model == "OpenAI API" or selected_model.lower() == "gpt-3.5-turbo":
                spinner_message = "Sending to OpenAI..."  # Message shown during API call
                provider_name = "OpenAI"                  # Provider name shown with response
            else:
                spinner_message = f"Sending to {selected_model}..."  # Custom message for other models
                provider_name = selected_model                      # Use selected model name as provider
            
            # -----------------------------------------------
            # API REQUEST WITH VISUAL FEEDBACK
            # -----------------------------------------------
            # Display a spinner while waiting for the API response
            # This provides visual feedback that the app is working
            with st.spinner(spinner_message):
                try:
                    # -----------------------------------------------
                    # MODEL API CALL
                    # -----------------------------------------------
                    # Currently using a fixed model (gpt-3.5-turbo)
                    # Future enhancement: Make this dynamic based on user selection
                    model = "gpt-3.5-turbo"
                    
                    # Make the API call to OpenAI's chat completions endpoint
                    # This sends the user's goal and formatting instructions to the AI
                    response = openai.chat.completions.create(
                        model=model,  # The AI model to use
                        messages=[
                            # System message defines the AI's role and behavior
                            {"role": "system", "content": "You are an assistant that helps users break down their goals into actionable steps."},
                            
                            # User message contains the goal and formatting instructions
                            # The formatting varies based on the user's selected output format
                            {"role": "user", "content": f"My goal: {user_input}\n" + (
                                # Standard format: Mix of paragraphs, bullets, and numbered lists
                                "Please break this down into actionable steps. Use a mix of regular paragraphs for overview and context, bullet points for general items, and numbered lists for sequential steps. Make it visually organized and easy to follow." if output_format == "Standard" else
                                # Bullet List format: Entire response as bullet points only
                                "Please break this down into actionable steps. Format your ENTIRE response as a bullet list ONLY. Do not use paragraphs or numbered lists." if output_format == "Bullet List" else
                                # Numbered List format: Entire response as a numbered list only
                                "Please break this down into actionable steps. Format your ENTIRE response as a numbered list ONLY. Do not use paragraphs or bullet points."
                            )}
                        ],
                        max_tokens=300,                # Limit response length
                        temperature=model_temperature  # Use the temperature from the slider
                    )
                    
                    # -----------------------------------------------
                    # RESPONSE DISPLAY - HEADER
                    # -----------------------------------------------
                    # Select the appropriate logo based on the model used
                    if selected_model == "OpenAI API" or model == "gpt-3.5-turbo":
                        logo_path = "Graphics/openai.svg"             # OpenAI logo for OpenAI models
                        model_cap = model[:1].upper() + model[1:]     # Capitalize model name (e.g., Gpt-3.5-turbo)
                        model_disp = model_cap                        # Display name for the model
                    else:
                        logo_path = "static/ai-generic.png"           # Generic AI logo for other models
                        model_disp = selected_model                   # Use the selected model name
                    
                    # Create a three-column layout for the response header
                    # This displays the model icon, provider name, and "response" label
                    col1, col2, col3 = st.columns([1, 6, 8])          # Column width ratio
                    
                    # Column 1: Display the model/provider icon
                    with col1:
                        st.image(logo_path, width=28)                 # Show model icon at appropriate size
                    
                    # Column 2: Display the provider name and "response" label
                    with col2:
                        st.markdown(
                            f"<b>{provider_name}</b> <span style='font-size:1.13em; font-weight:600; color:#444;'>response</span>",
                            unsafe_allow_html=True
                        )
                    
                    # Add spacing below the header for visual separation
                    st.write("")  
                    
                    # -----------------------------------------------
                    # RESPONSE DISPLAY - CONTENT
                    # -----------------------------------------------
                    # Display the AI's response, removing any extra whitespace
                    # The markdown formatting preserves the structure (paragraphs, lists, etc.)
                    st.markdown(response.choices[0].message.content.strip())
                    
                # -----------------------------------------------
                # ERROR HANDLING
                # -----------------------------------------------
                # Catch and display any errors that occur during the API call
                # Common errors: invalid API key, network issues, rate limiting
                except Exception as e:
                    st.error(f"OpenAI API error: {e}")  # Show error message with details
