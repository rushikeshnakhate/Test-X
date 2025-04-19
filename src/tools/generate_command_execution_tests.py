import os
from jinja2 import Environment, FileSystemLoader
import hydra
from omegaconf import DictConfig, OmegaConf

@hydra.main(version_base=None, config_path="config", config_name="command_execution_config")
def generate_feature_files(cfg: DictConfig) -> None:
    """
    Generate feature files based on Hydra configuration and template.
    
    Args:
        cfg: Hydra configuration object containing all parameters
    """
    # Set up Jinja2 environment
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('command_execution.feature.j2')
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), "generated")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate feature files for each combination
    for service_type in cfg.service_types:
        for service_name in cfg.service_names:
            for command in cfg.commands:
                for timeout in cfg.timeouts:
                    # Create context for template
                    context = {
                        'service_type': service_type,
                        'service_name': service_name,
                        'command': command,
                        'timeout': timeout
                    }
                    
                    # Generate feature file content
                    content = template.render(**context)
                    
                    # Create filename
                    filename = f"{service_type}_{service_name}_{command}.feature"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Write feature file
                    with open(filepath, 'w') as f:
                        f.write(content)
                    print(f"Generated: {filename}")

if __name__ == '__main__':
    generate_feature_files() 