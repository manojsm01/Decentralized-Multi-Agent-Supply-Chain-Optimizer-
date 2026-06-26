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

def run_supplier_agent(suppliers_data: list, required_delivery_days: int) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Supplier Sourcing Specialist',
        goal='Select the optimal supplier based on price, delivery days, and rating.',
        backstory='You are a strategic sourcing expert who finds the best suppliers considering cost, speed, and reliability.',
        llm=llm,
        max_iter=2, max_execution_time=20, verbose=True
    )
    
    suppliers_str = "\n".join([f"- {s['name']}: Price=${s['price']}, Delivery={s['delivery_days']} days, Rating={s['rating']}" for s in suppliers_data])
    
    task = Task(
        description=(f'Compare these suppliers:\n{suppliers_str}\n\n'
                     f'The required delivery time is {required_delivery_days} days. '
                     f'Select the best supplier balancing low price, high rating, and meeting delivery requirements. '
                     f'Return ONLY a valid JSON object with keys "selected_supplier_name" (string), "price" (float), "delivery_days" (integer), "rating" (float), and "analysis" (string).'),
        expected_output='JSON object with selected_supplier_name, price, delivery_days, rating, and analysis.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], max_iter=2, max_execution_time=20, verbose=False)
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            return {"selected_supplier_name": "Unknown", "price": 0.0, "delivery_days": 0, "rating": 0.0, "analysis": result}
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            analysis = "NVIDIA API quota exceeded. Please try again later. Supplier data unavailable."
        else:
            analysis = f"AI Analysis temporarily unavailable: {error_msg}. Supplier data unavailable."
        return {"selected_supplier_name": "Fallback Supplier", "price": 0.0, "delivery_days": 0, "rating": 0.0, "analysis": analysis}
