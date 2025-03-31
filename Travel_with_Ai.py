import streamlit as st
from datetime import date, timedelta
import google.generativeai as genai

# Initialize Gemini model
genai.configure(api_key="AIzaSyBJBu1iX2cY8MEthn5KcqUVpBbgL4RPIOM")  # Replace with your actual API key
model = genai.GenerativeModel("gemini-1.5-pro")

# Placeholder for Web Search - You'll need to implement this
def web_search(query):
    """
    This is a placeholder for a web search function.
    You'll need to replace this with actual code that uses a web search API
    (e.g., Google Search API) to fetch information.
    For now, it returns a generic response.
    """
    return "Web search results for " + query

# --- System Prompts ---

# System Prompt 1: Input Refinement
SYSTEM_PROMPT_INPUT_REFINEMENT = """
You are a helpful travel planning assistant. Your goal is to gather user preferences and generate a detailed travel itinerary.
First, collect the following information from the user:
- Destination
- Start Location
- Budget
- Start Date
- Duration (in days)
- Purpose of Travel
- Travel Preferences (e.g., "Local Food", "Nature & Scenery")
- Type of Trip (e.g., Solo, Couple, Family, Group)
- Number of People
"""

# System Prompt 2: Itinerary Generation
SYSTEM_PROMPT_ITINERARY_GENERATION = """
You are an expert travel planner. Generate a detailed {duration}-day travel itinerary for {destination} starting from {start_date} for {type_of_trip} of {number_of_people} people.
Consider these preferences: {preferences}.
Dietary preferences: {dietary_preferences}.
Specific interests: {specific_interests}.
Walking tolerance: {walking_tolerance}.
Accommodation preference: {accommodation_type}.
Ensure the itinerary includes a mix of activities, dining, and relaxation.
Use web search to find up-to-date top attractions, activities, and cost estimates. Provide a detailed cost breakdown for each day, including accommodation, food, activities, and transportation, ensuring it fits within the budget of ${budget}.
Provide the itinerary in the following format:

Day 1:
- Activity 1: Description (Cost Estimate)
- Activity 2: Description (Cost Estimate)
...
Day 2:
- Activity 1: Description (Cost Estimate)
- Activity 2: Description (Cost Estimate)
...
"""

# --- Streamlit App ---

st.title("AI-Powered Travel Planner")
st.subheader("Get a personalized itinerary with cost breakdown")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Collect user inputs
st.header("Tell us about your trip!")

# Budget
budget = st.number_input("Enter your budget ($):", min_value=0, step=100)

# Travel Dates
start_date = st.date_input("Select your start date:", min_value=date.today())
duration = st.number_input("How many days are you planning to stay?", min_value=1, step=1)

# Destination & Starting Location
start_location = st.text_input("Enter your starting location:")
destination = st.text_input("Enter your travel destination:")

# Purpose of Travel
purpose = st.selectbox("What is the purpose of your travel?",
                     ["Leisure", "Business", "Honeymoon", "Adventure", "Backpacking", "Other"])

# Preferences
preferences = st.multiselect("Select your preferences:",
                             ["Local Food", "Nature & Scenery", "Adventure Activities",
                              "Cultural & Historical Sites",
                              "Relaxation", "Shopping", "Nightlife"])

# Type of Trip & Number of People
type_of_trip = st.selectbox("Type of Trip", ["Solo", "Couple", "Family", "Group"])
number_of_people = st.number_input("Number of People", min_value=1, step=1)

# --- Input Refinement Prompts ---

# User Prompt 1: Gather additional details
USER_PROMPT_INPUT_REFINEMENT = """
Can you please provide the following additional details for your trip planning:
- Dietary preferences
- Specific interests within your chosen preferences
- Your comfort level with walking/mobility concerns (Minimal, Moderate, High)
- Accommodation preferences (e.g., luxury, budget, central location)
"""

# Get additional details from the user
dietary_preferences = st.text_input("Any dietary preferences?")
specific_interests = st.text_area("Specify any particular interests within your preferences:")
walking_tolerance = st.selectbox("How comfortable are you with walking during the trip?",
                                 ["Minimal", "Moderate", "High"])
accommodation_type = st.selectbox("What type of accommodation do you prefer?",
                                     ["Luxury", "Budget", "Central Location", "Hostel", "Other"])

# --- Itinerary Generation ---
def generate_itinerary(destination, start_date, duration, preferences, budget,
                        dietary_preferences, specific_interests, walking_tolerance,
                        accommodation_type, type_of_trip, number_of_people):
    """Generates a personalized travel itinerary with cost breakdown."""

    #  Use web search to get information for the prompt
    search_results = web_search(f"top attractions in {destination}")
    #  Include web search results in the prompt to Gemini
    prompt = SYSTEM_PROMPT_ITINERARY_GENERATION.format(
        duration=duration,
        destination=destination,
        start_date=start_date,
        preferences=", ".join(preferences),
        budget=budget,
        dietary_preferences=dietary_preferences,
        specific_interests=specific_interests,
        walking_tolerance=walking_tolerance,
        accommodation_type=accommodation_type,
        web_search_results=search_results,  # Add search results to the prompt
        type_of_trip=type_of_trip,
        number_of_people=number_of_people
    )

    try:
        response = model.generate_content(prompt)
        return response.text if response else "Error generating itinerary."
    except Exception as e:
        return f"An error occurred: {e}"

# Submit Button
if st.button("Generate Itinerary"):
    # Check for empty required fields and display a single warning
    missing_fields = []
    if not destination.strip():
        missing_fields.append("Destination")
    if not start_location.strip():
        missing_fields.append("Starting Location")
    if not preferences:
        missing_fields.append("Preferences")

    if missing_fields:
        st.warning(f"Please fill in the following required fields: {', '.join(missing_fields)}")
    else:
        st.success("Here is your personalized AI-generated itinerary with a cost breakdown:")
        itinerary = generate_itinerary(destination, start_date, duration, preferences, budget,
                                       dietary_preferences, specific_interests,
                                       walking_tolerance, accommodation_type, type_of_trip,
                                       number_of_people)
        st.markdown(itinerary)