from vertexai.preview.reasoning_engines import ReasoningEngine
from vertexai.preview.reasoning_engines import LangchainAgent
from src.config.logging import logger
from src.config.setup import config
import vertexai
import yaml


vertexai.init(project=config.PROJECT_ID, location=config.REGION, staging_bucket=config.BUCKET)

yaml_file_path = './config/agents.yml'

with open(yaml_file_path, 'r') as file:
    config = yaml.safe_load(file)

current_converter = config.get('current_converter')

# PROJECT_ID = "YOUR_PROJECT_ID"
# LOCATION = "YOUR_LOCATION"
# REASONING_ENGINE_ID = "YOUR_REASONING_ENGINE_ID"

remote_agent = ReasoningEngine(current_converter)
query = "What's the exchange rate from US dollars to Swedish currency today?"
response = remote_agent.query(input=query)
print(response)