import itertools
import os
from typing import List, Dict, Any
import hydra
from omegaconf import DictConfig, OmegaConf

class FeatureGenerator:
    def __init__(self, template_dir: str = "features/templates", output_dir: str = "features/generated"):
        self.template_dir = template_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def load_template(self, template_name: str) -> str:
        """Load a feature template file"""
        template_path = os.path.join(self.template_dir, f"{template_name}.feature.template")
        with open(template_path, 'r') as f:
            return f.read()

    def generate_combinations(self, parameters: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """Generate all possible combinations of parameters"""
        keys = parameters.keys()
        values = parameters.values()
        combinations = list(itertools.product(*values))
        return [dict(zip(keys, combo)) for combo in combinations]

    def generate_feature(self, template_name: str, parameters: Dict[str, List[Any]], 
                        output_name: str = None) -> str:
        """Generate a feature file from a template with parameter combinations"""
        template = self.load_template(template_name)
        combinations = self.generate_combinations(parameters)
        
        # Generate scenarios for each combination
        scenarios = []
        for combo in combinations:
            scenario = template
            for key, value in combo.items():
                scenario = scenario.replace(f"<{key}>", str(value))
            scenarios.append(scenario)

        # Combine all scenarios
        feature_content = "\n\n".join(scenarios)
        
        # Save to file if output_name is provided
        if output_name:
            output_path = os.path.join(self.output_dir, f"{output_name}.feature")
            with open(output_path, 'w') as f:
                f.write(feature_content)
            return output_path
        
        return feature_content

@hydra.main(version_base=None, config_path="../../config", config_name="command_execution_config")
def generate_from_config(cfg: DictConfig) -> List[str]:
    """Generate features from a Hydra configuration"""
    generator = FeatureGenerator()
    generated_files = []

    # Convert Hydra config to parameters dictionary
    parameters = {
        'service_type': cfg.service_types,
        'service_name': cfg.service_names,
        'command': cfg.commands,
        'timeout': cfg.timeouts
    }
    
    output_path = generator.generate_feature(
        template_name='command_execution',
        parameters=parameters,
        output_name='command_execution_combinations'
    )
    generated_files.append(output_path)
    
    return generated_files

if __name__ == '__main__':
    generate_from_config() 