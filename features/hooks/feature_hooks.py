"""
Feature hooks for Behave tests.
"""


def before_feature(context, feature):
    """Setup before each feature"""
    # Log the feature being executed
    print(f"\nExecuting feature: {feature.name}")

    # You can add feature-specific setup here
    # For example, setting up feature-specific configuration
    if hasattr(feature, 'tags') and 'requires_special_setup' in feature.tags:
        # Do special setup for features with this tag
        pass


def after_feature(context, feature):
    """Cleanup after each feature"""
    # Log the feature completion
    print(f"Completed feature: {feature.name}")

    # You can add feature-specific cleanup here
    # For example, cleaning up feature-specific resources
    if hasattr(feature, 'tags') and 'requires_special_cleanup' in feature.tags:
        # Do special cleanup for features with this tag
        pass
