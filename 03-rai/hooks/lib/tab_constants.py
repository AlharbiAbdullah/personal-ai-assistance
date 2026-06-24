"""Tab title states and phase configuration."""

# Phase config for Algorithm phases
PHASE_CONFIG = {
    "OBSERVE": {"symbol": "O", "label": "Observing"},
    "THINK":   {"symbol": "T", "label": "Thinking"},
    "PLAN":    {"symbol": "P", "label": "Planning"},
    "BUILD":   {"symbol": "B", "label": "Building"},
    "EXECUTE": {"symbol": "X", "label": "Executing"},
    "VERIFY":  {"symbol": "V", "label": "Verifying"},
    "LEARN":   {"symbol": "L", "label": "Learning"},
    "COMPLETE": {"symbol": "D", "label": "Done"},
}

# Tab states
TAB_STATES = {
    "thinking": "...",
    "working": "Working",
    "question": "Awaiting input",
    "completed": "Done",
    "error": "Error",
    "idle": "Idle",
}
