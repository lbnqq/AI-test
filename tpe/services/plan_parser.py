"""
Module for parsing Markdown pressure test plans.
"""
import re

class PlanParser:
    """
    Parses a Markdown file containing pressure test scenarios.
    """
    def __init__(self, file_path: str):
        """
        Initializes the parser with the path to the Markdown file.

        Args:
            file_path (str): Path to the Markdown plan file.
        """
        self.file_path = file_path

    def parse(self) -> list[dict]:
        """
        Parses the Markdown file and extracts test scenarios.

        Returns:
            list[dict]: A list of dictionaries, each representing a scenario.
                        Example: [{'id': 'Scenario 1', 'conflict': 'Duty vs. Empathy', 'prompt': '...'}, ...]
        """
        scenarios = []
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Regex to match the scenario blocks
        # This regex is based on the example format provided in the task description.
        pattern = r"### (Scenario \d+): (.*?)\n\n.*?```.*?\n(.*?)\n```"
        matches = re.findall(pattern, content, re.DOTALL)

        for match in matches:
            scenario_id, conflict, prompt = match
            # Clean up the prompt by stripping leading/trailing whitespace
            # which might include newlines from the markdown code block
            clean_prompt = prompt.strip()
            scenarios.append({
                'id': scenario_id,
                'conflict': conflict.strip(),
                'prompt': clean_prompt
            })

        return scenarios