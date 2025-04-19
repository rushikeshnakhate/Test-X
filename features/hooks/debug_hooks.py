"""
Debug hooks for Behave tests.
"""

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('behave')


def after_step(context, step):
    """Log after each step"""
    # Log the step that was executed
    logger.info(f"Step executed: {step.name} - {step.status}")

    # If the step failed, log the error
    if step.status == 'failed':
        logger.error(f"Step failed: {step.name}")
        logger.error(f"Error: {step.error_message}")

        # You can add additional debugging information here
        # For example, taking a screenshot, capturing logs, etc.


def after_scenario(context, scenario):
    """Log after each scenario"""
    # Log the scenario that was executed
    logger.info(f"Scenario completed: {scenario.name} - {scenario.status}")

    # If the scenario failed, log additional information
    if scenario.status == 'failed':
        logger.error(f"Scenario failed: {scenario.name}")

        # You can add additional debugging information here
        # For example, capturing the state of the system, logs, etc.
