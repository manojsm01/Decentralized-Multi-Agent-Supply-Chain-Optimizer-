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

def run_forecast_agent(product_name: str, quantity: int) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Demand Forecaster',
        goal='Predict future demand and recommend adjustments to the ordered quantity.',
        backstory='You are an expert demand forecaster. You analyze trends to ensure optimal stock levels are maintained.',
        llm=llm,
        max_iter=2, max_execution_time=20, verbose=True
    )
    
    task = Task(
        description=(f'Product: {product_name}. Requested Quantity: {quantity}. '
                     f'Given general market knowledge (simulate if necessary), recommend an adjusted quantity to order to meet future demand without overstocking. '
                     f'Return ONLY a valid JSON object with keys "quantity_to_order" (integer) and "analysis" (string).'),
        expected_output='JSON object containing quantity_to_order, and analysis.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], max_iter=2, max_execution_time=20, verbose=False)
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            return {"quantity_to_order": quantity, "analysis": result}
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            analysis = "NVIDIA API quota exceeded. Please try again later. Proceeding with requested quantity."
        else:
            analysis = f"AI Analysis temporarily unavailable: {error_msg}"
        return {"quantity_to_order": quantity, "analysis": analysis}
