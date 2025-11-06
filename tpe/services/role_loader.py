"""
Module for loading role prompts from text files.
"""
import os

# Define the directory for role files.
# This assumes a 'roles' directory exists at the same level as the 'services' package.
# In a more robust setup, this might be configurable.
ROLES_DIR = os.path.join(os.path.dirname(__file__), "..", "roles")

def load_role_prompt(role_name: str) -> str:
    """
    Loads the role prompt from a text file.

    Args:
        role_name (str): Name of the role (e.g., 'a1', 'b2').

    Returns:
        str: The role prompt content, or an empty string if 'default', empty, or file not found.
    """
    # If role_name is "default" or None/empty, return an empty string for no role loading
    if not role_name or role_name == "default":
        return ""

    role_file_path = os.path.join(ROLES_DIR, f"{role_name}.txt")
    
    # Check if the file exists
    if not os.path.exists(role_file_path):
        # In a real scenario, we might want to log this warning instead of print
        print(f"Warning: Role file not found: {role_file_path}. Using empty prompt.")
        return ""

    try:
        with open(role_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return content if content else ""
    except Exception as e:
        # In a real scenario, we might want to log this error instead of print
        print(f"Warning: Error reading role file {role_file_path}: {e}. Using empty prompt.")
        return ""