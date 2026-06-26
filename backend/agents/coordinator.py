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

def run_coordinator_agent(inventory_data: dict, supplier_data: dict, risk_data: dict, logistics_data: dict, procurement_data: dict) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Supply Chain Coordinator',
        goal='Combine all departmental outputs into a final cohesive executive summary.',
        backstory='You are the head of the supply chain. You synthesize reports from all departments into a clear summary for stakeholders.',
        llm=llm,
        max_iter=2, max_execution_time=20, verbose=True
    )
    
    context = (f"Inventory: {json.dumps(inventory_data)}\n"
               f"Supplier: {json.dumps(supplier_data)}\n"
               f"Risk: {json.dumps(risk_data)}\n"
               f"Logistics: {json.dumps(logistics_data)}\n"
               f"Procurement: {json.dumps(procurement_data)}")
               
    task = Task(
        description=(f'Review the following departmental reports:\n{context}\n\n'
                     f'Write a concise final "procurement_summary" paragraph combining all these insights. '
                     f'Return ONLY a valid JSON object with key "procurement_summary" (string).'),
        expected_output='JSON object containing procurement_summary.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], max_iter=2, max_execution_time=20, verbose=False)
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            return {"procurement_summary": result}
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            summary = "NVIDIA API quota exceeded. Please try again later. Supply chain coordination summary unavailable."
        else:
            summary = f"AI Analysis temporarily unavailable: {error_msg}. Coordination summary unavailable."
        return {"procurement_summary": summary}
