# streamlit run app.py
import streamlit as st
from PIL import Image
import google.generativeai as genai

# ---------------------------
# Gemini API Configuration
# ---------------------------
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# ---------------------------
# Initialize Session State
# ---------------------------
if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
        "goals": "Lose 10 pounds in 3 months, Improve cardiovascular health",
        "conditions": "None",
        "routines": "30-minute walk 3x/week",
        "preferences": ["Vegetarian", "Low carb"],
        "restrictions": ["No dairy", "No nuts"]
    }

# ---------------------------
# Gemini AI Response Function
# ---------------------------
def get_gemini_response(json_prompt, image_data=None):
    """
    Generates a response from Gemini AI using a structured JSON prompt.
    Can optionally include image data for analysis.
    """
    model = genai.GenerativeModel("models/gemini-2.5-flash")  # Confirm model
    content = [json_prompt]

    if image_data:
        content.extend(image_data)

# -----------------------------------------------------------------
# Error if Model Doesn't Get Doesn't work or Don't get Any Response
# -----------------------------------------------------------------
    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# ---------------------------
# Image Setup Function
# ---------------------------
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    return None

# ---------------------------
# Streamlit Layout
# ---------------------------
st.set_page_config(page_title="MetaMeal", layout="wide")
st.title("MetaMeal")

# ---------------------------
# Sidebar: Health Profile
# ---------------------------
with st.sidebar:
    st.subheader("Your Health Profile")
    health_goals = st.text_area("Health Goals", value=st.session_state.health_profile['goals'])
    medical_conditions = st.text_area("Medical Conditions", value=st.session_state.health_profile['conditions'])
    fitness_routines = st.text_area("Fitness Routines", value=st.session_state.health_profile['routines'])
    food_preferences = st.text_area(
        "Food Preferences",
        value="\n".join(st.session_state.health_profile['preferences'])
    )
    restrictions = st.text_area(
        "Dietary Restrictions",
        value="\n".join(st.session_state.health_profile['restrictions'])
    )
    if st.button("Update Profile"):
        st.session_state.health_profile = {
            "goals": health_goals,
            "conditions": medical_conditions,
            "routines": fitness_routines,
            "preferences": [p.strip() for p in food_preferences.split("\n") if p],
            "restrictions": [r.strip() for r in restrictions.split("\n") if r]
        }
        st.success("Profile updated!")

# ---------------------------
# Main Tabs
# ---------------------------
tab1, tab2, tab3 = st.tabs(["Meal Planning", "Food Analysis", "Health Insights"])

# ---------------------------
# Tab 1: Meal Planning
# ---------------------------
with tab1:
    st.subheader("Personalized Meal Planning")
    col1, col2 = st.columns(2)
    with col1:
        user_input = st.text_area(
            "Specific requirements for your meal plan:",
            placeholder="e.g., 'Quick meals for work days'"
        )
    with col2:
        st.write("### Your Health Profile")
        st.json(st.session_state.health_profile)

    if st.button("Generate Personalized Meal Plan", key="meal_plan_btn"):
        if not any(st.session_state.health_profile.values()):
            st.warning("Please complete your health profile in the sidebar first")
        else:
            with st.spinner("Creating your personalized meal plan..."):
                meal_plan_prompt = {
                    "task": "Generate a personalized 7-day meal plan",
                    "user_profile": st.session_state.health_profile,
                    "additional_requirements": user_input if user_input else "None provided",
                    "output_format": {
                        "days": [
                            {
                                "day": "Day 1-7",
                                "meals": {
                                    "breakfast": "",
                                    "lunch": "",
                                    "dinner": "",
                                    "snacks": ""
                                },
                                "context": "",
                                "preparation_tips": "",
                                "shopping_list": []
                            }
                        ]
                    }
                }
                response = get_gemini_response(meal_plan_prompt)
                st.subheader("Your Personalized Meal Plan")
                st.markdown(response)
                st.download_button(
                    label="Download Meal Plan",
                    data=response,
                    file_name="personalized_meal_plan.txt",
                    mime="text/plain"
                )

# ---------------------------
# Tab 2: Food Analysis
# ---------------------------
with tab2:
    st.subheader("Food Analysis")
    uploaded_file = st.file_uploader("Upload an image of your food", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Food Image", use_column_width=True)

        if st.button("Analyze Food", key="analyze_food_btn"):
            with st.spinner("Analyzing your food..."):
                image_data = input_image_setup(uploaded_file)

                food_analysis_prompt = {
                    "task": "Analyze food image",
                    "image_data": image_data,
                    "analysis_criteria": [
                        "Estimated calories",
                        "Macronutrient breakdown",
                        "Potential health benefits",
                        "Concerns based on dietary restrictions",
                        "Suggested portion sizes"
                    ],
                    "output_format": {
                        "items": [
                            {
                                "name": "",
                                "calories": "",
                                "macros": {"protein": "", "carbs": "", "fat": ""},
                                "benefits": "",
                                "concerns": "",
                                "recommended_portion": ""
                            }
                        ]
                    }
                }

                response = get_gemini_response(food_analysis_prompt, image_data=image_data)
                st.markdown(response)

# ---------------------------
# Tab 3: Health Insights
# ---------------------------
with tab3:
    st.subheader("Health Insights")
    health_query = st.text_input(
        "Ask a health/nutrition-related question",
        placeholder="e.g., 'How can I improve my gut health?'"
    )
    if st.button("Get Expert Insights", key="health_insights_btn"):
        if not health_query:
            st.warning("Please enter a health question")
        else:
            with st.spinner("Researching your question..."):
                health_insights_prompt = {
                    "task": "Provide health and nutrition advice",
                    "user_query": health_query,
                    "user_profile": st.session_state.health_profile,
                    "output_format": {
                        "explanation": "",
                        "recommendations": [],
                        "precautions": "",
                        "references": ""
                    }
                }
                response = get_gemini_response(health_insights_prompt)
                st.markdown(response)
