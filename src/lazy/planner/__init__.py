"""lazy-planner package for Lazy OS dialogue and intent generation."""
from lazy.planner.base import PlannerInterface
from lazy.planner.mock import MockPlanner

__all__ = [
    "PlannerInterface",
    "MockPlanner",
]
