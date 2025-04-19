"""
Behave hooks package for test setup and teardown.
"""

# Import all hooks to make them available
from features.hooks.connection_hooks import (
    before_all,
    after_all,
    before_scenario,
    after_scenario
)

from features.hooks.feature_hooks import (
    before_feature,
    after_feature
)

from features.hooks.debug_hooks import (
    after_step,
    after_scenario
)

__all__ = [
    'before_all',
    'after_all',
    'before_feature',
    'after_feature',
    'before_scenario',
    'after_scenario',
    'after_step'
] 