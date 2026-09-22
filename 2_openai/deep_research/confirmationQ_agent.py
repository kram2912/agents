from pydantic import BaseModel, Field
from agents import Agent
import os
from dotenv import load_dotenv
load_dotenv(override=True)

MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "gpt-5.4-mini")

INSTRUCTIONS = """
You are a research assistant. Given a user query, come up with one follow-up question
to help clarify the user query.
Present the question as a series of options the user can answer with a single response,
e.g. A, B, C or 1, 2, 3.
"""


class ClarifyQResponse(BaseModel):
    question: str = Field(
        description="A follow-up question with options (A/B/C or 1/2/3) for the user to pick from."
    )


confirmationQ_agent = Agent(
    name="Confirmation Agent",
    instructions=INSTRUCTIONS,
    model=MODEL_NAME,
    output_type=ClarifyQResponse,
)
