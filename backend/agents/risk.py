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
            
    # Fallback to manual extraction using regex
    risk_match = re.search(r'"risk_level"\s*:\s*"([^"]+)"', text, re.IGNORECASE)
    reasoning_match = re.search(r'"(?:analysis|reasoning)"\s*:\s*"([^"]+)"', text, re.IGNORECASE)
    
    if risk_match or reasoning_match:
        return {
            "risk_level": risk_match.group(1) if risk_match else "Unknown",
            "reasoning": reasoning_match.group(1) if reasoning_match else text
        }
        
    return {}

def run_risk_agent(supplier_name: str, delivery_days: int, required_delivery_days: int) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Risk Analyst',
        goal='Analyze potential risks associated with the selected supplier and delivery timeline.',
        backstory='You are a supply chain risk analyst. You detect potential delays and violations of deadlines.',
        llm=llm,
        verbose=True
    )
    
    task = Task(
        description=(f'Supplier: {supplier_name}. Estimated Delivery: {delivery_days} days. '
                     f'Required Deadline: {required_delivery_days} days. '
                     f'Determine the risk level of deadline violations or delays. '
                     f'Return ONLY a valid JSON object with keys "risk_level" (string: "Low", "Medium", "High") and "reasoning" (string).'),
        expected_output='JSON object containing risk_level and reasoning.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], verbose=False)
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            return {"risk_level": "Unknown", "reasoning": result}
        
        # If the LLM returned "analysis" instead of "reasoning"
        if "analysis" in parsed and "reasoning" not in parsed:
            parsed["reasoning"] = parsed.pop("analysis")
            
        return parsed
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            reasoning = "Gemini API quota exceeded. Please try again later. Risk cannot be calculated."
        else:
            reasoning = f"AI Analysis temporarily unavailable: {error_msg}. Risk cannot be calculated."
        
        risk_level = "High" if delivery_days > required_delivery_days else "Low"
        return {"risk_level": risk_level, "reasoning": reasoning}
