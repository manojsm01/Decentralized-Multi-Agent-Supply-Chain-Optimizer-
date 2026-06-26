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

def run_logistics_agent(routes_data: list, destination: str) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Logistics Manager',
        goal='Calculate the best delivery route minimizing distance and delivery time.',
        backstory='You are a logistics expert responsible for routing shipments efficiently to save costs and time.',
        llm=llm,
        max_iter=2, max_execution_time=20, verbose=True
    )
    
    routes_str = "\n".join([f"- {r['name']}: {r['distance_km']} km" for r in routes_data])
    
    task = Task(
        description=(f'Destination: {destination}.\n'
                     f'Available Routes:\n{routes_str}\n\n'
                     f'Select the best route based on the shortest distance. '
                     f'Return ONLY a valid JSON object with keys "recommended_route_name" (string), "distance_km" (float), and "analysis" (string).'),
        expected_output='JSON object containing recommended_route_name, distance_km, and analysis.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], max_iter=2, max_execution_time=20, verbose=False)
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            return {"recommended_route_name": "Unknown", "distance_km": 0.0, "analysis": result}
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            analysis = "NVIDIA API quota exceeded. Please try again later. Route cannot be optimized."
        else:
            analysis = f"AI Analysis temporarily unavailable: {error_msg}. Route cannot be optimized."
        return {"recommended_route_name": "Fallback Route", "distance_km": 0.0, "analysis": analysis}
