"""Prompt Injection Detection Guardrail for detecting jailbreak attempts."""

import re
from typing import Any, Dict, List, Optional

from agentguard.guardrails.base import Guardrail, GuardrailResult


class PromptInjectionGuardrail(Guardrail):
    """Detects prompt injection and jailbreak attempts."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize prompt injection guardrail.

        Args:
            config: Configuration with action, sensitivity
        """
        config = config or {}
        super().__init__({
            "name": "PromptInjection",
            "description": "Detects prompt injection and jailbreak attempts",
            "version": "1.0.0",
            **config
        })

        # Configure action: block, transform, allow
        self.action = config.get("action", "block")

        # Configure sensitivity: low, medium, high
        self.sensitivity = config.get("sensitivity", "medium")

        # Detection patterns organized by attack type
        self.patterns = {
            "instruction_injection": [
                re.compile(r'ignore (all )?(previous|above|prior) (instructions|prompts|rules)', re.IGNORECASE),
                re.compile(r'disregard (all )?(previous|above|prior) (instructions|prompts|rules)', re.IGNORECASE),
                re.compile(r'forget (all )?(previous|above|prior) (instructions|prompts|rules)', re.IGNORECASE),
                re.compile(r'new (instructions|task|prompt):', re.IGNORECASE),
                re.compile(r'system (prompt|message|instruction):', re.IGNORECASE),
            ],
            "role_playing": [
                re.compile(r'you are now (a|an) ', re.IGNORECASE),
                re.compile(r'pretend (you are|to be) ', re.IGNORECASE),
                re.compile(r'act as (a|an) ', re.IGNORECASE),
                re.compile(r'roleplay as ', re.IGNORECASE),
                re.compile(r'simulate (a|an) ', re.IGNORECASE),
                re.compile(r'from now on,? you (are|will be)', re.IGNORECASE),
            ],
            "system_leakage": [
                re.compile(r'show (me )?(your|the) (system|original) (prompt|instructions)', re.IGNORECASE),
                re.compile(r'what (are|were) your (original|initial) (instructions|prompt)', re.IGNORECASE),
                re.compile(r'repeat (your|the) (system|original) (prompt|instructions)', re.IGNORECASE),
                re.compile(r'print (your|the) (system|original) (prompt|instructions)', re.IGNORECASE),
            ],
            "jailbreak": [
                re.compile(r'DAN (mode|prompt)', re.IGNORECASE),
                re.compile(r'do anything now', re.IGNORECASE),
                re.compile(r'evil confidant', re.IGNORECASE),
                re.compile(r'DUDE (mode|prompt)', re.IGNORECASE),
                re.compile(r'jailbreak (mode|prompt)', re.IGNORECASE),
                re.compile(r'developer mode', re.IGNORECASE),
                re.compile(r'opposite mode', re.IGNORECASE),
            ],
            "encoding": [
                re.compile(r'base64|rot13|hex|unicode|ascii', re.IGNORECASE),
                re.compile(r'decode (this|the following)', re.IGNORECASE),
                re.compile(r'\\x[0-9a-f]{2}', re.IGNORECASE),
                re.compile(r'&#\d+;'),
            ],
            "delimiter": [
                re.compile(r'"""|\'\'\'|```'),
                re.compile(r'\[SYSTEM\]|\[USER\]|\[ASSISTANT\]', re.IGNORECASE),
                re.compile(r'<\|system\|>|<\|user\|>|<\|assistant\|>', re.IGNORECASE),
            ],
        }

        # Risk scores per attack type
        self.risk_scores = {
            "instruction_injection": 90,
            "role_playing": 70,
            "system_leakage": 95,
            "jailbreak": 100,
            "encoding": 80,
            "delimiter": 85,
        }

        # Sensitivity thresholds
        self.thresholds = {
            "low": 2,    # Require 2+ pattern matches
            "medium": 1,  # Require 1+ pattern match
            "high": 1,    # Require 1+ pattern match
        }

    async def evaluate(
        self,
        input_data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> GuardrailResult:
        """Evaluate input for prompt injection attempts.

        Args:
            input_data: Input to scan
            context: Execution context

        Returns:
            GuardrailResult with detection results
        """
        text = self._extract_text(input_data)
        detections = self._detect_injection(text)

        threshold = self.thresholds[self.sensitivity]

        if len(detections) < threshold:
            return GuardrailResult(
                passed=True,
                action="allow",
                reason="No prompt injection detected",
                metadata={"detections": []},
                risk_score=0,
            )

        # Calculate maximum risk score
        max_risk_score = max(self.risk_scores.get(d["type"], 50) for d in detections)

        # Determine action
        action = self.action
        passed = action in ["allow", "transform"]

        metadata = {"detections": detections}
        if action == "transform":
            metadata["transformed_text"] = self._transform_injection(text, detections)

        return GuardrailResult(
            passed=passed,
            action=action,
            reason=f"Detected {len(detections)} prompt injection pattern(s): {', '.join(d['type'] for d in detections)}",
            metadata=metadata,
            risk_score=max_risk_score,
        )

    def _extract_text(self, input_data: Any) -> str:
        """Extract text from various input formats."""
        if isinstance(input_data, str):
            return input_data

        if isinstance(input_data, dict):
            if "prompt" in input_data:
                return input_data["prompt"]
            if "messages" in input_data and isinstance(input_data["messages"], list):
                return " ".join(m.get("content", "") for m in input_data["messages"])
            if "text" in input_data:
                return input_data["text"]

        return str(input_data)

    def _detect_injection(self, text: str) -> List[Dict[str, Any]]:
        """Detect prompt injection patterns."""
        detections = []

        for attack_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    detections.append({
                        "type": attack_type,
                        "pattern": pattern.pattern,
                        "match": match.group(0),
                        "confidence": self._calculate_confidence(attack_type, match.group(0)),
                    })

        return detections

    def _calculate_confidence(self, attack_type: str, match: str) -> float:
        """Calculate confidence score for detection."""
        base_confidence = {
            "instruction_injection": 0.85,
            "role_playing": 0.70,
            "system_leakage": 0.95,
            "jailbreak": 0.98,
            "encoding": 0.75,
            "delimiter": 0.80,
        }

        return base_confidence.get(attack_type, 0.70)

    def _transform_injection(self, text: str, detections: List[Dict[str, Any]]) -> str:
        """Transform injection attempt to safer alternative."""
        # Sort by match length (longest first)
        sorted_detections = sorted(detections, key=lambda d: len(d["match"]), reverse=True)

        transformed = text
        for detection in sorted_detections:
            transformed = transformed.replace(detection["match"], "[FILTERED_INJECTION]")

        return transformed
