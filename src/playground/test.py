from vertexai.preview.reasoning_engines import ReasoningEngine
from vertexai.preview.reasoning_engines import LangchainAgent
from src.config.logging import logger
from src.config.setup import config
from typing import Dict
from typing import Any 
import vertexai
import requests


vertexai.init(project=config.PROJECT_ID, location=config.REGION, staging_bucket=config.BUCKET)


def get_exchange_rate(currency_from: str = "USD", currency_to: str = "EUR", currency_date: str = "latest") -> Dict[str, Any]:
    """
    Retrieves the exchange rate between two currencies on a specified date.

    Args:
        currency_from (str): The base currency to convert from. Default is 'USD'.
        currency_to (str): The target currency to convert to. Default is 'EUR'.
        currency_date (str): The date of the exchange rate. Use 'latest' for the most recent rate. Default is 'latest'.

    Returns:
        Dict[str, Any]: A dictionary containing the exchange rate information.

    Raises:
        requests.exceptions.RequestException: An error occurred while making the HTTP request.
    """
    try:
        logger.info(f"Requesting exchange rate from {currency_from} to {currency_to} for date {currency_date}.")
        response = requests.get(
            f"https://api.frankfurter.app/{currency_date}",
            params={"from": currency_from, "to": currency_to},
        )
        response.raise_for_status()  # Raise an exception for HTTP errors
        logger.info("Exchange rate retrieved successfully.")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"An error occurred while retrieving the exchange rate: {e}")
        return {"error": str(e)}



def create_agent(func_name: str) -> LangchainAgent:
    """
    Creates a Langchain agent using the specified function name.

    Args:
        func_name (str): The name of the function to use with the agent.

    Returns:
        reasoning_engines.LangchainAgent: The created Langchain agent.
    """
    try:
        logger.info(f"Creating agent with function: {func_name}")
        agent = LangchainAgent(model=config.TEXT_GEN_MODEL_NAME, 
                               tools=[func_name], 
                               # agent_executor_kwargs={"return_intermediate_steps": True}
                               )
        logger.info("Agent created successfully.")
        return agent
    except Exception as e:
        logger.error(f"An error occurred while creating the agent: {e}")
        raise


def deploy_agent(agent: LangchainAgent) -> ReasoningEngine:
    """
    Deploys a Langchain agent using VertexAI's ReasoningEngine.

    Args:
        agent (LangchainAgent): The agent to be deployed.

    Returns:
        ReasoningEngine: The deployed remote agent.

    Raises:
        Exception: An error occurred while deploying the agent.
    """
    try:
        requirements = [
            "google-cloud-aiplatform==1.51.0",
            "langchain==0.1.20",
            "langchain-google-vertexai==1.0.3",
            "cloudpickle==3.0.0",
            "pydantic==2.7.1",
            "requests==2.32.3"
        ]

        logger.info("Deploying the agent with the following requirements:")
        # for requirement in requirements:
        #    logger.info(requirement)

        remote_agent = ReasoningEngine.create(agent, requirements=requirements)
        logger.info("Agent deployed successfully.")
        return remote_agent
    except Exception as e:
        logger.error(f"An error occurred while deploying the agent: {e}")
        raise


if __name__ == '__main__':
    response = get_exchange_rate(currency_from="USD", currency_to="INR")
    print(response)
    current_converter = agent = create_agent(func_name=get_exchange_rate)
    query = "What is 700k USD equivalent in Indian Rupees. Specify the answer in terms of Lakhs and Crores. Use indian decimals."
    response = current_converter.query(input=query)
    answer = response['output']
    print(f'Answer = {answer}')
    """
    intermediate_steps = response['intermediate_steps']
    tool = intermediate_steps[0][0]['kwargs']['tool']
    tool_input = intermediate_steps[0][0]['kwargs']['tool_input']
    action = intermediate_steps[0][0]['kwargs']['log'].strip()
    logger.info(f'Tool ==> {tool}')
    logger.info(f'Tool Input  ==> {tool}')
    logger.info(f'Action ==> {action}')
    """
    remote_agent = deploy_agent(agent=current_converter)
    print(remote_agent.resource_name)







