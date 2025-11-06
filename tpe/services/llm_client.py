"""
A minimal LLM client for TPE, compatible with Ollama's OpenAI API.
This is a simplified version based on llm_assessment/services/llm_client.py
"""
import os
from typing import Dict, List, Any, Optional
from openai import OpenAI

class LLMClient:
    """
    A minimal LLM client for PsyAgent TPE, focusing on local Ollama models.
    """
    def __init__(self, api_base: str = "http://localhost:11434/v1", api_key: str = "ollama"):
        """
        Initialize LLM client for local Ollama.

        Args:
            api_base (str): The base URL for the Ollama API (must end with /v1). Defaults to "http://localhost:11434/v1".
            api_key (str): The API key. For Ollama, this is typically "ollama". Defaults to "ollama".
        """
        self.api_base = api_base.rstrip('/') # Remove trailing slash if present
        if not self.api_base.endswith('/v1'):
            self.api_base += '/v1'
        self.api_key = api_key
        print(f"\n--- TPE LLMClient Initialized ---", flush=True)
        print(f"  API Base (final): {self.api_base}", flush=True)
        print(f"  API Key: {self.api_key}", flush=True)
        print("----------------------------------\n", flush=True)

    def generate_response(self, messages: List[Dict[str, str]], 
                         model_identifier: str,
                         options: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate response from a local Ollama LLM.

        Args:
            messages (List[Dict[str, str]]): List of messages in OpenAI format.
            model_identifier (str): Specific model to use (e.g., 'gemma2:latest').
            options (Optional[Dict[str, Any]]): Generation options (tmpr, max_tokens, etc.).

        Returns:
            Optional[str]: Model response or None if failed.
        """
        print(f"LLMClient.generate_response called with model: {model_identifier}")
        print(f"Messages: {messages}")
        print(f"Options: {options}")
        try:
            # Ollama's OpenAI compatible endpoint is at /v1
            client = OpenAI(base_url=self.api_base, api_key=self.api_key)
            
            # For Ollama, the model identifier is just the model name (e.g., 'gemma2:latest')
            actual_model_id = model_identifier

            # Convert options to OpenAI format
            openai_options = {}
            if options:
                # Map common options, add more as needed
                if "tmpr" in options:
                    openai_options["tmpr"] = options["tmpr"]
                if "max_tokens" in options:
                    openai_options["max_tokens"] = options["max_tokens"]
            
            print(f"Calling OpenAI client with model={actual_model_id}, openai_options={openai_options}")
            response = client.chat.completions.create(
                model=actual_model_id,
                messages=messages,
                **openai_options
            )
            print(f"OpenAI client returned response: {response}")
            content = response.choices[0].message.content
            print(f"Extracted content: {content}")
            return content
            
        except Exception as e:
            print(f"LLM call failed: {e}")
            import traceback
            traceback.print_exc()
            return None