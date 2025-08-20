import json
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from core.config import settings
from schemas.plan import GeneratedPlanSchema

def generate_meal_plan(user_profile: dict, food_items: List[Dict], days: int = 1) -> GeneratedPlanSchema:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.7,
        google_api_key=settings.GEMINI_API_KEY
    )

    prompt = PromptTemplate.from_template("""
    You are a nutritionist AI.
    Based on the user's profile and available foods, generate a meal plan for {days} day(s).

    User Profile:
    Dietary Preference: {dietary_prefs}
    Goal: {goals}
    BMI: {bmi}

    Available Food Items (name, calories, protein, carbs, fats per reference unit):
    {food_list}

    Format the output strictly as JSON:
    {{
        "days": [
            {{
                "day": 1,
                "meals": [
                    {{
                        "meal": "Breakfast",
                        "items": [
                            {{"food_id": 1, "quantity": 100, "unit": "g"}}
                        ]
                    }}
                ]
            }}
        ]
    }}
    """)

    formatted_prompt = prompt.format(
        days=days,
        dietary_prefs=user_profile["dietary_prefs"],
        goals=user_profile["goals"],
        bmi=user_profile["bmi"],
        food_list=json.dumps(food_items, indent=2)
    )

    response = llm.invoke(formatted_prompt)

    try:
        parsed_data = json.loads(response.content)
    except json.JSONDecodeError:
        raise ValueError("AI response not in expected JSON format")

    # Validate with Pydantic
    return GeneratedPlanSchema(**parsed_data)
