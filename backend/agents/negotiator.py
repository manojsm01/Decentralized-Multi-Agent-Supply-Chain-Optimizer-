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

def run_negotiator_agent(product_name: str, quantity: int, supplier_name: str, current_price: float) -> dict:
    llm = get_llm()
    
    agent = Agent(
        role='Expert Contract Negotiator',
        goal='Secure the best possible bulk discount for large procurement orders.',
        backstory=(
            'You are a ruthless but professional supply chain contract negotiator. '
            'You use logic, market leverage, and purchase volume to argue for lower unit prices. '
            'You always find a reason why the supplier should drop their price for a bulk order.'
        ),
        llm=llm,
        max_iter=2, max_execution_time=30, verbose=True
    )
    
    task = Task(
        description=(
            f'Supplier: {supplier_name}\n'
            f'Product: {product_name}\n'
            f'Requested Bulk Quantity: {quantity}\n'
            f'Current Unit Price: ${current_price}\n\n'
            f'Formulate a negotiation argument to secure a discount based on the bulk quantity. '
            f'Determine a reasonable negotiated unit price (lower than the current price, usually 5-20% off depending on quantity). '
            f'Return ONLY a valid JSON object with exactly these keys:\n'
            f'"negotiated_price" (float),\n'
            f'"discount_percentage" (float),\n'
            f'"negotiation_summary" (string containing your argument to the supplier).'
        ),
        expected_output='JSON object containing negotiated_price, discount_percentage, and negotiation_summary.',
        agent=agent
    )
    
    crew = Crew(agents=[agent], tasks=[task], max_iter=2, max_execution_time=30, verbose=False)
    
    try:
        result = str(crew.kickoff())
        parsed = parse_json_from_text(result)
        if not parsed:
            # Fallback if AI fails to return JSON
            discount = min(20.0, max(5.0, quantity / 100.0))
            new_price = round(current_price * (1 - (discount/100)), 2)
            return {
                "negotiated_price": new_price,
                "discount_percentage": discount,
                "negotiation_summary": f"Fallback: AI negotiation parsing failed, but volume implies a {discount:.1f}% discount."
            }
        return parsed
    except Exception as e:
        error_msg = str(e)
        return {
            "negotiated_price": current_price,
            "discount_percentage": 0.0,
            "negotiation_summary": f"Negotiation failed: {error_msg}. Proceeding with standard price."
        }
