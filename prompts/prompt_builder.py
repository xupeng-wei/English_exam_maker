import yaml
from jinja2 import Template, Environment, Undefined
import os
import re

import logging

logging.basicConfig(
    filename="/tmp/runtime.log",  # Save logs to a file (optional)
    level=logging.INFO,  # Set logging level (INFO, ERROR, DEBUG, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Add timestamp
    datefmt="%Y-%m-%d %H:%M:%S",  # Customize timestamp format
    force=True,
)

class PromptBuilder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._prompt_path = os.path.dirname(__file__)
            cls._instance._recipe = {}
            cls._instance.refresh_prompt_templates()
        return cls._instance

    def build(self, prompt_name: str, **kwargs):
        if prompt_name not in self._recipe:
            raise ValueError(f"Prompt {prompt_name} not found.")
        return Template(self._recipe[prompt_name]["template"]).render(**kwargs)

    def list_prompts(self):
        return list(self._recipe.keys())
    
    def get_template(self, prompt_name: str):
        if prompt_name not in self._recipe:
            raise ValueError(f"Prompt {prompt_name} not found.")
        return self._recipe[prompt_name]
    
    def _fill_in_template_vars(self, value):
        if type(value) is not dict:
            return value
        if "template" not in value:
            return value
        template = value["template"]
        kwargs = {}
        for k, v in value.items():
            if k == "template":
                continue
            # kwargs[k] = v
            value["template"] = re.sub("{{ " + k + " }}", str(v), template)
        # env = Environment(undefined=Undefined)
        # value["template"] = env.from_string(template).render(**kwargs)
        return value

    def refresh_prompt_templates(self):
        updated_this_time = set()
        for file in os.listdir(self._prompt_path):
            if file.endswith(".yaml"):
                with open(os.path.join(self._prompt_path, file), "r", encoding="utf-8") as f:
                    prompt_configs = yaml.safe_load(f)
                    if prompt_configs is None:
                        logging.warning(f"Prompt config in {file} is empty.")
                        continue
                    for key, value in prompt_configs.items():
                        original_key = key
                        suffix = 1
                        while key in updated_this_time:
                            logging.warning(f"Duplicate prompt name '{key}' found. Appending suffix to make it unique.")
                            key = f"{original_key}_{suffix}"
                            suffix += 1
                        self._recipe[key] = self._fill_in_template_vars(value)
                        updated_this_time.add(key)
        return self