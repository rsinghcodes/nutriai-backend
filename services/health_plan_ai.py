import json
import re
from typing import List, Dict, Annotated, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from core.config import settings
from schemas.health_plan import CompleteHealthPlanSchema
from utils import get_day_name
from services.rag_service import get_rag_retriever

class GraphState(TypedDict):
    user_profile: dict
    food_items: List[Dict]
    day_name: str
    context: str
    meal_draft: str
    workout_draft: str
    critic_feedback: str
    iterations: int
    final_plan: dict

def extract_json(text) -> dict:
    if isinstance(text, list):
        text = "".join(part["text"] for part in text if "text" in part)
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in AI response")
    return json.loads(match.group(0))

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0.7,
    google_api_key=settings.GEMINI_API_KEY
)

def retrieve_context_node(state: GraphState):
    import os
    kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", "general_guidelines.txt")
    try:
        with open(kb_path, "r") as f:
            context = f.read()
    except Exception:
        context = "Follow general healthy guidelines."
    return {"context": context}

def meal_planner_node(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Meal Planner AI. Generate a meal plan for the day based on the profile, constraints, and RAG context.\n"
                   "Context: {context}\n"
                   "Profile: Diet={diet}, Goal={goal}, Allergies={allergies}, Budget={budget}\n"
                   "Available Foods: {food_list}\n"
                   "Feedback from Critic: {critic_feedback}\n\n"
                   "Output ONLY a JSON array of meals:\n"
                   "[{{\"meal\": \"Breakfast\", \"items\": [{{\"food_id\": 1, \"quantity\": 100, \"unit\": \"g\"}}]}}]"),
        ("human", "Generate the meal plan.")
    ])
    chain = prompt | llm
    res = chain.invoke({
        "context": state["context"],
        "diet": state["user_profile"]["dietary_prefs"],
        "goal": state["user_profile"]["goals"],
        "allergies": state["user_profile"].get("allergies", "None"),
        "budget": state["user_profile"].get("budget", "Standard"),
        "food_list": json.dumps(state["food_items"], indent=2),
        "critic_feedback": state.get("critic_feedback", "None")
    })
    return {"meal_draft": res.content}

def workout_planner_node(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Workout Planner AI. Generate a workout plan based on the profile.\n"
                   "Profile: Goal={goal}, BMI={bmi}\n"
                   "Feedback from Critic: {critic_feedback}\n\n"
                   "Output ONLY a JSON object:\n"
                   "{{\"focus_area\": \"Cardio\", \"exercises\": [{{\"name\": \"Running\", \"sets\": 1, \"reps\": \"30 mins\"}}]}}"),
        ("human", "Generate the workout plan.")
    ])
    chain = prompt | llm
    res = chain.invoke({
        "goal": state["user_profile"]["goals"],
        "bmi": state["user_profile"]["bmi"],
        "critic_feedback": state.get("critic_feedback", "None")
    })
    return {"workout_draft": res.content}

def critic_node(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a Safety Critic. Review the drafted meal and workout plans against the user's allergies, budget, and goals.\n"
                   "Profile: Diet={diet}, Goal={goal}, Allergies={allergies}, Budget={budget}\n"
                   "Available Foods (Cross-reference food_ids here): {food_list}\n\n"
                   "Draft Meal Plan: {meal_draft}\n"
                   "Draft Workout Plan: {workout_draft}\n\n"
                   "If there are any violations (e.g. allergens included, budget ignored), output feedback starting with 'REJECTED: ' followed by the reasons.\n"
                   "If it is safe and adheres to all constraints, output 'APPROVED'. You must be strict."),
        ("human", "Review the drafts.")
    ])
    chain = prompt | llm
    res = chain.invoke({
        "diet": state["user_profile"]["dietary_prefs"],
        "goal": state["user_profile"]["goals"],
        "allergies": state["user_profile"].get("allergies", "None"),
        "budget": state["user_profile"].get("budget", "Standard"),
        "food_list": json.dumps(state["food_items"], indent=2),
        "meal_draft": state["meal_draft"],
        "workout_draft": state["workout_draft"]
    })
    
    iters = state.get("iterations", 0) + 1
    return {"critic_feedback": res.content, "iterations": iters}

def compiler_node(state: GraphState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are the Compiler AI. Combine the approved drafts into the final complete health plan JSON.\n"
                   "Draft Meal Plan: {meal_draft}\n"
                   "Draft Workout Plan: {workout_draft}\n"
                   "Profile: Allergies={allergies}, Budget={budget}\n"
                   "Generate 'avoidance_list' and 'budget_tips' based on the profile.\n\n"
                   "Output strictly JSON matching CompleteHealthPlanSchema:\n"
                   "{{\n"
                   '  "day": "{day}",\n'
                   '  "meal_plan": [...],\n'
                   '  "workout_plan": {{...}},\n'
                   '  "avoidance_list": ["item1"],\n'
                   '  "budget_tips": ["tip1"]\n'
                   "}}"),
        ("human", "Compile the final plan.")
    ])
    chain = prompt | llm
    res = chain.invoke({
        "day": state["day_name"],
        "allergies": state["user_profile"].get("allergies", "None"),
        "budget": state["user_profile"].get("budget", "Standard"),
        "meal_draft": state["meal_draft"],
        "workout_draft": state["workout_draft"]
    })
    
    try:
        parsed = extract_json(res.content)
    except Exception as e:
        raise ValueError(f"Failed to parse final plan: {e}")
    return {"final_plan": parsed}

def route_critic(state: GraphState):
    feedback = state["critic_feedback"]
    if isinstance(feedback, list):
        feedback = str(feedback)
    print(f"--- CRITIC FEEDBACK (Iteration {state['iterations']}) ---")
    print(feedback)
    if "APPROVED" in feedback.upper() or state["iterations"] >= 3:
        return "compiler"
    return "meal_planner"

workflow = StateGraph(GraphState)
workflow.add_node("retrieve", retrieve_context_node)
workflow.add_node("meal_planner", meal_planner_node)
workflow.add_node("workout_planner", workout_planner_node)
workflow.add_node("critic", critic_node)
workflow.add_node("compiler", compiler_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "meal_planner")
workflow.add_edge("meal_planner", "workout_planner")
workflow.add_edge("workout_planner", "critic")

workflow.add_conditional_edges(
    "critic",
    route_critic,
    {
        "compiler": "compiler",
        "meal_planner": "meal_planner"
    }
)
workflow.add_edge("compiler", END)

health_plan_app = workflow.compile()

def generate_complete_health_plan(user_profile: dict, food_items: List[Dict], day: int = 1) -> CompleteHealthPlanSchema:
    day_name = get_day_name(day)
    initial_state = {
        "user_profile": user_profile,
        "food_items": food_items,
        "day_name": day_name,
        "iterations": 0
    }
    
    final_state = health_plan_app.invoke(initial_state)
    return CompleteHealthPlanSchema(**final_state["final_plan"])
