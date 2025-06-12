import streamlit as st
import requests
import re

# Page configuration
st.set_page_config(page_title="Recipe Generator", layout="centered")

st.title("🍽️ AI Recipe Generator")
st.markdown("Enter ingredients you have and choose a meal type to discover delicious recipes!")

# --- User Input ---
ingredients = st.text_input("📝 Ingredients (comma-separated)", placeholder="e.g., tomato, cheese, bread")
meal_type = st.selectbox("🍴 Meal Type", ["breakfast", "lunch", "dinner", "snack"])

# --- API Setup ---
API_KEY = st.secrets["api"]["spoonacular_key"]
SEARCH_URL = "https://api.spoonacular.com/recipes/findByIngredients"
DETAILS_URL = "https://api.spoonacular.com/recipes/{}/information"

# --- Utility Functions ---
def extract_steps_from_instructions(instruction_html):
    if not instruction_html:
        return []
    # Extract <li> items
    steps = re.findall(r"<li>(.*?)</li>", instruction_html, re.DOTALL)
    if steps:
        return [re.sub('<[^<]+?>', '', step).strip() for step in steps]

    # Fallback: clean and split
    instruction_text = re.sub('<[^<]+?>', '', instruction_html)
    return [step.strip() for step in re.split(r'(?<=[.?!])\s+', instruction_text) if step.strip()]

def fetch_recipes(ingredients, meal_type):
    params = {
        "apiKey": API_KEY,
        "ingredients": ingredients,
        "number": 5,
        "ranking": 1
    }
    res = requests.get(SEARCH_URL, params=params)
    return res.json()

def fetch_recipe_details(recipe_id):
    res = requests.get(DETAILS_URL.format(recipe_id), params={"apiKey": API_KEY})
    return res.json()

# --- Recipe Search ---
if st.button("🔍 Find Recipes"):
    if not ingredients:
        st.warning("Please enter some ingredients.")
    else:
        with st.spinner("Fetching recipes..."):
            recipes = fetch_recipes(ingredients, meal_type)

            if not recipes:
                st.error("No recipes found with the given ingredients.")
            else:
                for recipe in recipes:
                    detail = fetch_recipe_details(recipe["id"])

                    # --- Display Image ---
                    st.image(detail.get("image", ""), caption=recipe.get("title", ""), use_container_width=True)

                    # --- Title and Ingredients ---
                    st.subheader(recipe.get("title", "Recipe"))
                    st.markdown("**✅ Used Ingredients:**")
                    for ing in recipe.get('usedIngredients', []):
                        name = ing.get('name', '')
                        amt = ing.get('amount', '')
                        unit = ing.get('unit', '')
                        line = f"- {amt} {unit} {name}".strip()
                        st.markdown(line)

                    # --- Instructions ---
                    steps = extract_steps_from_instructions(detail.get("instructions", ""))
                    if steps:
                        st.markdown("### 📋 Instructions")
                        for i, step in enumerate(steps, start=1):
                            st.markdown(f"**{i}.** {step}")
                    else:
                        st.info("No instructions provided.")

                    st.markdown("---")
