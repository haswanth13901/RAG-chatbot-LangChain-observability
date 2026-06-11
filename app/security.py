import re
from dataclasses import dataclass


@dataclass
class SecurityCheckResult:
    is_safe:   bool
    reason:    str
    sanitized: str


_INJECTION_PATTERNS: list[tuple[str, str]] = [
    (r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?", "instruction override"),
    (r"forget\s+(everything|all|your\s+instructions?)",           "memory wipe"),
    (r"you\s+are\s+now\s+(a\s+)?(different|new|another)",         "persona hijack"),
    (r"(pretend|act|behave)\s+(like|as(\s+if)?)\s+you\s+are",     "persona hijack"),
    (r"(disregard|bypass|override)\s+(your\s+)?(system|rules?|guidelines?|instructions?)", "rule bypass"),
    (r"do\s+not\s+follow\s+(your\s+)?(rules?|guidelines?|instructions?)",                  "rule bypass"),
    (r"reveal\s+(your\s+)?(system\s+)?(prompt|instructions?|context)", "prompt extraction"),
    (r"(show|print|display|output)\s+(your\s+)?(system\s+)?(prompt|instructions?)",        "prompt extraction"),
    (r"jailbreak",                                                 "jailbreak attempt"),
    (r"dan\s+mode",                                               "jailbreak attempt"),
    (r"developer\s+mode",                                         "jailbreak attempt"),
    (r"</?(system|human|assistant|prompt|context)>",              "prompt tag injection"),
    (r"\[INST\]|\[/INST\]|\[SYS\]",                              "prompt tag injection"),
]

MAX_INPUT_LENGTH = 2000


def check_injection(user_input: str) -> SecurityCheckResult:
    if not user_input or not user_input.strip():
        return SecurityCheckResult(
            is_safe=False,
            reason="empty input",
            sanitized="",
        )

    if len(user_input) > MAX_INPUT_LENGTH:
        return SecurityCheckResult(
            is_safe=False,
            reason=f"input too long ({len(user_input)} chars, max {MAX_INPUT_LENGTH})",
            sanitized=user_input[:MAX_INPUT_LENGTH],
        )

    lowered = user_input.lower()
    for pattern, label in _INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            return SecurityCheckResult(
                is_safe=False,
                reason=f"injection pattern detected: {label}",
                sanitized=user_input,
            )

    sanitized = _sanitize(user_input)
    return SecurityCheckResult(is_safe=True, reason="ok", sanitized=sanitized)


def _sanitize(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s{3,}", "  ", text)
    return text.strip()