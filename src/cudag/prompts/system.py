# Copyright (c) 2025 Tylt LLC. All rights reserved.
# Derivative works may be released by researchers,
# but original files may not be redistributed or used beyond research purposes.

"""System prompts for VLM training datasets.

These prompts define the tool interface presented to the model during training.
Projects can use built-in prompts or provide custom ones.

IMPORTANT: System prompts are managed by the system-prompt project.
Run `system-prompt/scripts/sync.sh` to update prompts from the canonical source.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

# Load prompts from text files (managed by system-prompt project)
_PROMPTS_DIR = Path(__file__).parent


def _load_prompt(filename: str) -> str:
    """Load a prompt from a text file."""
    filepath = _PROMPTS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(
            f"System prompt file not found: {filepath}\n"
            "Run system-prompt/scripts/sync.sh to generate prompt files."
        )
    return filepath.read_text().strip()


# Computer Using Agent (CUA) verbose system prompt
CUA_SYSTEM_PROMPT = _load_prompt("SYSTEM_PROMPT.txt")

# Compact system prompt (used by claim-window)
SYSTEM_PROMPT_COMPACT = _load_prompt("SYSTEM_PROMPT_COMPACT.txt")

# Available prompt styles
PROMPT_STYLES = {
    "computer-use": CUA_SYSTEM_PROMPT,  # Primary key
    "cua": CUA_SYSTEM_PROMPT,  # Alias
    "compact": SYSTEM_PROMPT_COMPACT,
}

PromptStyle = Literal["computer-use", "cua", "compact"]


def get_system_prompt(style: PromptStyle | str = "computer-use") -> str:
    """Get a system prompt by style name.

    Args:
        style: Prompt style name - use "computer-use" for CUA prompt

    Returns:
        System prompt string

    Raises:
        ValueError: If style is not recognized
    """
    if style in PROMPT_STYLES:
        return PROMPT_STYLES[style]

    raise ValueError(f"Unknown prompt style: {style}. Available: {list(PROMPT_STYLES.keys())}")
