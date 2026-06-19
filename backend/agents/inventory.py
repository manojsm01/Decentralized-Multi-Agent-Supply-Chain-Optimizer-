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

def run_inventory_agent(product_name: str, required_quantity: int, current_stock: int) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Inventory Manager',
        goal='Analyze the current stock levels and determine if procurement is necessary.',
        backstory='You are an expert supply chain inventory manager. You ensure that stock levels meet demand without overstocking.',
        llm=llm,
        verbose=True
    )
    
    task = Task(
        description=(f'Product: {product_name}. Required Quantity: {required_quantity}. Current Stock: {current_stock}. '
                     f'Calculate the shortage (if any) and whether we need to order more. '
                     f'Return ONLY a valid JSON object with keys "needs_procurement" (boolean), "quantity_to_order" (integer), and "analysis" (string).'),
        expected_output='JSON object containing needs_procurement, quantity_to_order, and analysis.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    
    shortage = max(0, required_quantity - current_stock)
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            return {"needs_procurement": shortage > 0, "quantity_to_order": shortage, "analysis": result}
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            analysis = "Gemini API quota exceeded. Please try again later. Using simple mathematical fallback."
        else:
            analysis = f"AI Analysis temporarily unavailable: {error_msg}. Using simple mathematical fallback."
        return {"needs_procurement": shortage > 0, "quantity_to_order": shortage, "analysis": analysis}
