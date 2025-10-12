# streamlit run app.py   --- run
# Ctrl + c  --- Stop 

# from dotenv import load_dotenv
# load_dotenv()
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Configure Gemini
# insert your Gemini API key https://aistudio.google.com/apikey

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# ------------------------
# INITIALIZE SESSION STATE
# ------------------------
if 'health_profile' not in st.session_state:
    st.session_state.health_profile = {
        "goals": "Lose 20 pounds in 5 months, Improve cardiovascular health",
        "conditions": "None",
        "routines": "50-minute walk 3x/week",
        "preferences": ["Vegetarian", "Low carb"],
        "restrictions": ["No dairy", "No nuts"]
    }

#-----------------------------
# GEMINI AI RESPONSE FUNCTION 
# ----------------------------
def get_gemini_response(input_prompt, image_data=None):
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    content =[input_prompt]

    if image_data:
        content.extend(image_data)

    # -------------------------
    # FOR GENERATING CONTENT FROM MODEL
    # -------------------------
    try:
        response = model.generate_content(content)
        return response.text
    except Exception as e:
        return f"Error generating response:{str(e)}"
    

# -------------------------
# IMAGE SET UP FUNCTION
# -------------------------
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts =[{
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }]
        return image_parts
    return None

# ---------------------
# STREAMLIT APP LAYOUT
# ---------------------
st.set_page_config(page_title="MetaMeal", layout="wide")
st.header("MetaMeal")

# -----------------------------------
# SIDEBAR FOR BETTER HEALTH PROFILE
# -----------------------------------
with st.sidebar:
    st.subheader("Personal Health Blueprint ")
    health_goals = st.text_area("Your Health Goals 🎯",
          value = st.session_state.health_profile['goals'])
    medical_conditions = st.text_area("Personal Health Status ⚕️",
          value=st.session_state.health_profile['conditions'])
    fitness_routines = st.text_area("Workout & Activity Tracker 🏃‍♂️",
          value=st.session_state.health_profile['routines'])
    food_preferences = st.text_area("Nutrition Choices 🌿",
          value=st.session_state.health_profile['preferences'])
    restrictions = st.text_area("Food Restrictions & Alerts ⚠️",
          value=st.session_state.health_profile['restrictions'])
    
# ----------------------------------------------------------------------------
# IF USER WANTS TO CHANGE ANY CHANGES UPDATED INTO MAIN "HEALTH PROFILE STATE"
# ----------------------------------------------------------------------------
    if st.button("🔥 Apply Changes Now!"):
        st.session_state.health_profile ={
            'goals': health_goals,
            'conditions': medical_conditions,
            'routines': fitness_routines,
            'preferences': food_preferences,
            'restrictions': restrictions
        }
        st.success("⚡ Profile updated! Let's crush those health goals!")

#-------------------
# MAIN CONTENT TABS
# ------------------
tab1, tab2, tab3 = st.tabs(["Smart Meal Plan 🔍","Analyze Your Meal 🥙","Health Insights 🧠"])

# ---------------------
# TAB1 = MEAL PLANNING 
# ----------------------
with tab1:
    st.subheader("Personalized Meal Pathway 🍏")

    col1, col2 = st.columns(2)
    with col1:
        st.write("### What You Need Today 🥗")
        user_input = st.text_area("Tell Me What Matters Most for Your Meals Right Now 🥗",
                        placeholder="e.g.,Meals That Fit Your Day 🍴")
    with col2:
        st.write("### Personal Health Blueprint 🧬")
        st.json(st.session_state.health_profile)

        if st.button("Build My Smart Meal Plan 🚀", key="meal_plan_btn"):
            if not any(st.session_state.health_profile.values()):
                st.warning("🥗 Almost there! Complete your health profile to unlock your personalized meal plan.")
            else:
                with st.spinner("Generating your goal-based meals..."):
                    # Construct the prompt
                    prompt=f'''
                            You are an expert nutrition assistant. Using the user's health profile below, generate a personalized 7-day meal plan that aligns with their goals, dietary preferences, restrictions, and lifestyle.

                            📌 **User Health Profile**
                            - Goals: {st.session_state.health_profile['goals']}
                            - Medical Conditions: {st.session_state.health_profile['conditions']}
                            - Fitness Routine: {st.session_state.health_profile['routines']}
                            - Food Preferences: {', '.join(st.session_state.health_profile['preferences'])}
                            - Dietary Restrictions: {', '.join(st.session_state.health_profile['restrictions'])}
                            - Additional Requirements: {user_input if user_input else "None"}

                            🎯 **Required Output**
                            1. A 7-day meal plan with:
                            - Breakfast
                            - Lunch
                            - Dinner
                            - Snacks
                            2. Daily nutritional breakdown:
                            - Calories
                            - Protein
                            - Carbs
                            - Fats
                            3. Brief rationale for each meal choice, explaining how it supports the user's goals and respects dietary restrictions
                            4. Consolidated shopping list organized by category (produce, pantry, protein, etc.)
                            5. Practical prep tips, batch-cooking suggestions, and time-saving ideas

                            📐 **Formatting Instructions**
                            - Use numbered days (Day 1, Day 2, …)
                            - Present meals as bullet points with ingredients and portion sizes
                            - Use tables for nutritional breakdown if possible
                            - Keep explanations concise, actionable, and goal-focused
                            - Output must be clearly structured for easy reading and copy-paste

                            ⚡ **Tone and Style**
                            - Friendly and encouraging
                            - Professional and science-based
                            - Focus on actionable, practical advice
                            '''

                    response = get_gemini_response(prompt)

                    st.subheader("Your Personalized Nutrition Roadmap 🚀")
                    st.markdown(response)
                
                # -------------------
                # DOWNLOAD BUTTON
                # -------------------
                st.download_button(
                    label="🥗 Download Personalized Plan",
                    data=response,
                    file_name="personalized_meal_plan.txt",
                    mime="text/plain"
                )
    
# ----------------------
# ANALYZE YOUR MEAL 🥙
# ----------------------

with tab2:
    st.subheader("Smart Food Analysis 🥗")

    uploaded_file = st.file_uploader("Upload Your Food Image 🍽️",
                                     type=["jpg","jpeg","png"])
    
    # -------------------------------------
    # IMAGE SET UP FUNCTION
    # -------------------------------------
    image_data = input_image_setup(uploaded_file)

    # ---------------------------------
    # ERROR HANDLING FOR UPLOADING FILE 
    # ---------------------------------
    if uploaded_file is not None and image_data is not None:
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Your Meal Image 🍽️", use_container_width=True)
        except Exception as e:
            st.error(f"⚠️ Could not open the image: {str(e)}")

        if st.button("🔍 Analyze My Meal", key="analyze_food_btn"):
            with st.spinner("🍏 Analyzing your meal… almost ready!"):
                image_data = input_image_setup(uploaded_file)

                prompt =f"""
                    You are an expert nutritionist and dietitian. Analyze the uploaded food image thoroughly.

                        📌 **Instructions:**
                        1. Identify all visible food items in the image.
                        2. Provide for each item:
                        - Estimated calories
                        - Macronutrient breakdown (protein, carbs, fats)
                        - Key vitamins and minerals
                        - Potential health benefits
                        - Any dietary concerns (e.g., allergens, restrictions)
                        - Suggested portion sizes
                        3. If multiple foods are present, analyze each separately.
                        4. Provide practical serving suggestions if relevant.
                        5. Format output clearly using headings and bullet points.

                        Keep the analysis **concise, actionable, and easy to read** for a user aiming for healthy eating.
                    """
                response = get_gemini_response(prompt, image_data=image_data)
                st.markdown(response)

# --------------------------------
# HEALTH INSIGHTS 🧠
# ---------------------------------
with tab3:
    st.subheader("Wellness Insights 🌿")

    health_query = st.text_input("💡 Ask your health or nutrition question",
                                placeholder="e.g.,'How can I boost my gut health?'")
    if st.button("🧠 Unlock Health Tips", key="health_insights_btn"):
        if not health_query:
            st.warning("❗ Please provide a health or nutrition question to get insights.")
        else:
            with st.spinner("🧠 Digging up expert insights for you…"):
                prompt=f"""
                    You are a top-tier nutritionist and health coach. Provide **personalized, actionable, science-backed insights** based on the user's query.

                    📝 **User Question:**  
                    {health_query}

                    📌 **User Health Profile:**  
                    - Goals: {st.session_state.health_profile['goals']}  
                    - Medical Conditions: {st.session_state.health_profile['conditions']}  
                    - Fitness Routine: {st.session_state.health_profile['routines']}  
                    - Food Preferences: {st.session_state.health_profile['preferences']}  
                    - Dietary Restrictions: {st.session_state.health_profile['restrictions']}

                    🎯 **Your Response Should Include:**  
                    1. Clear, science-backed explanation of the topic.  
                    2. Practical, actionable recommendations (diet, lifestyle, supplements).  
                    3. Any relevant precautions or warnings.  
                    4. References to studies or evidence when applicable.  
                    5. Suggested foods, routines, or strategies tailored to the user.

                    ⚡ **Tone & Style:**  
                    - Friendly, motivating, and modern.  
                    - Easy-to-understand without sacrificing accuracy.  
                    - Structured using headings, bullet points, or numbered lists for readability.

                    Keep the response **concise, empowering, and focused on the user’s health journey**.
                """
                response = get_gemini_response(prompt)
                st.markdown(response)
