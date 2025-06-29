import os
import config
from pathlib import Path
from datetime import date
from langchain_perplexity import ChatPerplexity
from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from supabase_api import *

from typing import Optional
from pydantic import BaseModel, Field

class TransactionData(BaseModel):
    """Feature formatter to extract features from user text. If the text is not a transaction, set is_transaction to False."""

    is_transaction: bool = Field(description="Set to True if the text describes a financial transaction, otherwise set to False.")
    date: Optional[str] = Field(description="Date of the transaction in ISO format (e.g., 2025-05-02). Should be null if not a transaction.")
    category_type: Optional[str] = Field(description="Category type of the transaction (e.g., Income, Expense). Should be null if not a transaction.")
    category_name: Optional[str] = Field(description="Category name of the transaction (e.g., Salary, Transport, Food). Should be null if not a transaction.")
    description: Optional[str] = Field(description="A concise summary of the transaction. Should be null if not a transaction.")
    currency: Optional[str] = Field("HKD", description="The currency of the transaction (e.g., USD, HKD, TWD).")
    price: Optional[float] = Field(description="Price of the transaction (must be a number). Should be null if not a transaction.")

class TransactionExtractorLLM:
    """A class to interact with the Perplexity LLM for transaction data extraction."""

    ### "deepseek-chat" / "sonar"
    def __init__(self, model_name: str = "sonar", temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature

        if model_name in ["sonar", "sonar-pro", "llama-3.1-sonar-small-128k-online"]:
            os.environ["PPLX_API_KEY"] = config.PERPLEXITY_API_KEY

            # Use Perplexity's Sonar model
            self.llm = ChatPerplexity(model=self.model_name, temperature=self.temperature)
        elif model_name == "deepseek-chat":
            os.environ["DEEPSEEK_API_KEY"] = config.DEEPSEEK_API_KEY

            # Use DeepSeek's Chat model
            self.llm = ChatDeepSeek(model=self.model_name, temperature=self.temperature)

        self.prompt = self._create_prompt_template()

    def _create_prompt_template(self):
        """Loads the system prompt from an external file and creates the ChatPromptTemplate."""
        prompt_path = Path(__file__).parent / "prompts" / "bookkeeping_system_prompt.txt"
        system_prompt = prompt_path.read_text(encoding="utf-8")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human","{user_message}")
            ]
        )

        return prompt


    def extract_bookkeeping_features(self, user_input: str, user_id: int) -> dict:
        """
        Extracts bookkeeping features by LLM to generate structured output.
        """
        # 1. Chain the prompt with the LLM and the structured output parser
        structured_llm = self.llm.with_structured_output(TransactionData)
        chain = self.prompt | structured_llm

        # 2. Invoke the chain with the user message and current date
        response_model = chain.invoke({
            "user_message": user_input,
            "current_date": date.today().isoformat(),
            "user_categories": get_user_categories_info(user_id)
        })
        
        # 3. Return the model's output as a dictionary
        return response_model.model_dump()
        