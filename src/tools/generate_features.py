#!/usr/bin/env python3

import os
import yaml
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def generate_feature_files(config, template_dir, output_dir):
    """Generate feature files based on configuration and template."""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template('command_execution.feature.template')
    
    # Generate feature files for each combination
    for service_type in config['service_types']:
        for service_name in config['service_names']:
            for command in config['commands']:
                for timeout in config['timeouts']:
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
                    filename = f"{service_type}_{service_name}_{command.replace(' ', '_')}.feature"
                    filepath = os.path.join(output_dir, filename)
                    
                    # Write feature file
                    with open(filepath, 'w') as f:
                        f.write(content)
                    print(f"Generated: {filename}")

def main():
    # Get the directory containing this script
    script_dir = Path(__file__).parent.absolute()
    
    # Define paths
    config_path = os.path.join(script_dir, 'config', 'command_execution_config.yaml')
    template_dir = os.path.join(script_dir, 'templates')
    output_dir = os.path.join(script_dir, 'generated')
    
    # Load configuration
    config = load_config(config_path)
    
    # Generate feature files
    generate_feature_files(config, template_dir, output_dir)
    print("\nFeature file generation completed!")

if __name__ == '__main__':
    main() 