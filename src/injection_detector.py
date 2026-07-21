"""Prompt injection detection and prevention."""

import re
import logging
from enum import Enum

logger = logging.getLogger(__name__)


class InjectionThreatLevel(Enum):
    """Threat level classification for injection attempts."""
    SAFE = "safe"
    SUSPICIOUS = "suspicious"
    BLOCKED = "blocked"


class PromptInjectionDetector:
    """Detect and classify prompt injection attempts."""

    # Suspicious patterns that may indicate injection
    SUSPICIOUS_PATTERNS = {
        "system_override": r"(?i)(SYSTEM|ADMIN|OVERRIDE|FUNCTION|TASK|INSTRUCTION)[\s:]+",
        "rule_override": r"(?i)(ignore|forget|disregard|bypass|override).{0,40}(rule|constraint|guideline|instruction)",
        "persona_swap": r"(?i)(developer|admin|unrestricted|hacker|jailbreak).{0,20}mode",
        "delimiter_reset": r"(?i)-{2,}\s*(END|STOP|RESET|FINISH|CLOSE)",
        "role_injection": r"(?i)(now you are|you are|pretend|act as|assume role).{0,30}(developer|admin|unrestricted)",
        "encoding_bypass": r"(?i)(base64|encoded|decrypt|decode|rot13|cipher)",
        "metacomment": r"(?i)<!--\s*(SYSTEM|ADMIN|OVERRIDE)",
    }

    # Blocked patterns - high confidence injection attempts
    BLOCKED_PATTERNS = {
        "explicit_override": r"(?i)(OVERRIDE|JAILBREAK|UNFILTERED):\s*true",
        "system_reset": r"(?i)sys\.reset\(\)|system\.reset\(\)|reset_system",
    }

    def __init__(self, sensitivity: float = 0.5):
        """
        Initialize injection detector.

        Args:
            sensitivity: Threshold for flagging suspicious patterns (0.0-1.0)
                        Higher = more aggressive detection (more false positives)
                        Default 0.5: 2+ patterns trigger block
        """
        self.sensitivity = sensitivity

    def detect(self, user_input: str) -> dict:
        """
        Detect injection attempts in user input.

        Args:
            user_input: User's question/prompt

        Returns:
            {
                "threat_level": InjectionThreatLevel,
                "detected_patterns": [list of pattern names],
                "confidence": float (0.0-1.0),
                "reason": str,
                "is_blocked": bool,
            }
        """
        if not user_input or len(user_input.strip()) < 1:
            return {
                "threat_level": InjectionThreatLevel.SAFE,
                "detected_patterns": [],
                "confidence": 0.0,
                "reason": "Empty input",
                "is_blocked": False,
            }

        # Check for blocked patterns first (highest confidence)
        blocked_patterns = self._check_patterns(user_input, self.BLOCKED_PATTERNS)
        if blocked_patterns:
            return {
                "threat_level": InjectionThreatLevel.BLOCKED,
                "detected_patterns": blocked_patterns,
                "confidence": 1.0,
                "reason": f"Explicit injection attempt detected: {', '.join(blocked_patterns)}",
                "is_blocked": True,
            }

        # Check for suspicious patterns
        suspicious_patterns = self._check_patterns(user_input, self.SUSPICIOUS_PATTERNS)
        if suspicious_patterns:
            # Confidence increases with pattern count: 1 pattern = 0.3, 2 = 0.6, 3+ = 0.9
            confidence = min(1.0, len(suspicious_patterns) * 0.3)
            # Block if confidence meets sensitivity threshold
            is_blocked = confidence >= self.sensitivity

            return {
                "threat_level": InjectionThreatLevel.BLOCKED if is_blocked else InjectionThreatLevel.SUSPICIOUS,
                "detected_patterns": suspicious_patterns,
                "confidence": confidence,
                "reason": f"Suspicious patterns detected: {', '.join(suspicious_patterns)}",
                "is_blocked": is_blocked,
            }

        # No injection detected
        return {
            "threat_level": InjectionThreatLevel.SAFE,
            "detected_patterns": [],
            "confidence": 0.0,
            "reason": "No injection patterns detected",
            "is_blocked": False,
        }

    def _check_patterns(self, text: str, patterns: dict) -> list:
        """Check which patterns match in text."""
        matched = []
        for pattern_name, pattern in patterns.items():
            if re.search(pattern, text):
                matched.append(pattern_name)
        return matched

    def explain(self, detection_result: dict) -> str:
        """Generate human-readable explanation of detection result."""
        if detection_result["threat_level"] == InjectionThreatLevel.SAFE:
            return "✓ Input appears safe"

        patterns_str = ", ".join(detection_result["detected_patterns"])
        confidence_pct = detection_result["confidence"] * 100

        if detection_result["is_blocked"]:
            return f"🚫 BLOCKED: {detection_result['reason']} (confidence: {confidence_pct:.0f}%)"
        else:
            return f"⚠️  SUSPICIOUS: {detection_result['reason']} (confidence: {confidence_pct:.0f}%)"
