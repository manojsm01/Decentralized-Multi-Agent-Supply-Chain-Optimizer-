from crewai import Agent, Task, Crew
from . import get_llm
import json
import re

def parse_json_from_text(text: str) -> dict:
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    return {}

def run_procurement_agent(product_name: str, quantity_to_order: int, supplier_name: str, supplier_price: float, risk_level: str, route_name: str) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Procurement Officer',
        goal='Generate final purchase recommendations and calculate total costs.',
        backstory='You are a procurement officer who authorizes purchases and ensures all financial calculations are accurate.',
        llm=llm,
        verbose=True
    )
    
    task = Task(
        description=(f'Product: {product_name}. Quantity to Order: {quantity_to_order}. '
                     f'Supplier: {supplier_name} at ${supplier_price} per unit. '
                     f'Risk Level: {risk_level}. Route: {route_name}. '
                     f'Calculate the total cost (quantity * price). Provide a final recommendation on whether to proceed with this procurement. '
                     f'Return ONLY a valid JSON object with keys "total_cost" (float), "recommendation" (string), and "analysis" (string).'),
        expected_output='JSON object containing total_cost, recommendation, and analysis.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    
    total_cost = quantity_to_order * supplier_price
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            return {"total_cost": total_cost, "recommendation": "Proceed", "analysis": result}
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            analysis = "Gemini API quota exceeded. Please try again later. Mathematical fallback applied."
        else:
            analysis = f"AI Analysis temporarily unavailable: {error_msg}. Mathematical fallback applied."
        return {"total_cost": total_cost, "recommendation": "Proceed (Fallback)", "analysis": analysis}
