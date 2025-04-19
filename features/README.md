# Feature File Generator

This tool generates Gherkin feature files for network device command execution testing based on a template and configuration.

## Prerequisites

- Python 3.6 or higher
- Required Python packages:
  - PyYAML
  - Jinja2

## Installation

1. Install the required packages:
```bash
pip install pyyaml jinja2
```

## Usage

1. Configure your test cases in `config/command_execution_config.yaml`:
   - Define service types (ssh, telnet, snmp)
   - Specify service names (device names)
   - List commands to test
   - Set timeout values

2. Customize the feature template in `templates/command_execution.feature.template` if needed.

3. Run the generator:
```bash
python generate_features.py
```

4. Generated feature files will be created in the `generated` directory.

## File Structure

- `generate_features.py`: Main script for generating feature files
- `config/command_execution_config.yaml`: Configuration file
- `templates/command_execution.feature.template`: Feature file template
- `generated/`: Directory containing generated feature files

## Example

For a configuration with:
- Service type: ssh
- Service name: router1
- Command: show version
- Timeout: 30

The generator will create a feature file named `ssh_router1_show_version.feature` with the appropriate test scenarios. 