"""lazy-dialogue package for dialogue management, corrections, and interactive flows."""
from lazy.dialogue.corrections import CorrectionEngine
from lazy.dialogue.manager import DialogueManager

__all__ = [
    "DialogueManager",
    "CorrectionEngine",
]
