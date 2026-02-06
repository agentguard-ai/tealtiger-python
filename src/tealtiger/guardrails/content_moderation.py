"""Content Moderation Guardrail for detecting harmful content."""

import re
from typing import Any, Dict, List, Optional

import httpx

from tealtiger.guardrails.base import Guardrail, GuardrailResult


class ContentModerationGuardrail(Guardrail):
    """Detects harmful content: hate, violence, sexual, harassment."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize content moderation guardrail.

        Args:
            config: Configuration with use_openai, action, thresholds
        """
        config = config or {}
        super().__init__({
            "name": "ContentModeration",
            "description": "Detects harmful content using AI moderation",
            "version": "1.0.0",
            **config
        })

        # OpenAI API configuration
        self.api_key = config.get("api_key")
        self.use_openai = config.get("use_openai", bool(self.api_key))

        # Configure action: block, transform, allow
        self.action = config.get("action", "block")

        # Thresholds for each category (0-1)
        self.thresholds = config.get("thresholds", {
            "hate": 0.5,
            "hate/threatening": 0.5,
            "self-harm": 0.5,
            "sexual": 0.5,
            "sexual/minors": 0.3,
            "violence": 0.5,
            "violence/graphic": 0.5,
            "harassment": 0.5,
            "harassment/threatening": 0.5,
        })

        # Risk scores per category
        self.risk_scores = config.get("risk_scores", {
            "hate": 70,
            "hate/threatening": 90,
            "self-harm": 85,
            "sexual": 60,
            "sexual/minors": 100,
            "violence": 70,
            "violence/graphic": 85,
            "harassment": 60,
            "harassment/threatening": 80,
        })

        # Local pattern-based detection (fallback)
        self.patterns = {
            "hate": re.compile(r'\b(hate|racist|bigot|nazi|supremacist)\b', re.IGNORECASE),
            "violence": re.compile(r'\b(kill|murder|assault|attack|weapon|bomb)\b', re.IGNORECASE),
            "sexual": re.compile(r'\b(porn|xxx|explicit|nude)\b', re.IGNORECASE),
            "harassment": re.compile(r'\b(harass(ing|ment)?|bully|threaten|intimidate)\b', re.IGNORECASE),
            "self-harm": re.compile(r'\b(suicide|self-harm|cut myself)\b', re.IGNORECASE),
        }

    async def evaluate(
        self,
        input_data: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> GuardrailResult:
        """Evaluate input for harmful content.

        Args:
            input_data: Input to moderate
            context: Execution context

        Returns:
            GuardrailResult with moderation results
        """
        text = self._extract_text(input_data)

        if self.use_openai and self.api_key:
            violations = await self._moderate_with_openai(text)
        else:
            violations = self._moderate_with_patterns(text)

        if not violations:
            return GuardrailResult(
                passed=True,
                action="allow",
                reason="No harmful content detected",
                metadata={"violations": []},
                risk_score=0,
            )

        # Calculate maximum risk score
        max_risk_score = max(self.risk_scores.get(v["category"], 50) for v in violations)

        # Determine action
        action = self.action
        passed = action in ["allow", "transform"]

        metadata = {"violations": violations}
        if action == "transform":
            metadata["transformed_text"] = self._transform_content(text)

        return GuardrailResult(
            passed=passed,
            action=action,
            reason=f"Detected harmful content: {', '.join(v['category'] for v in violations)}",
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

    async def _moderate_with_openai(self, text: str) -> List[Dict[str, Any]]:
        """Moderate content using OpenAI Moderation API."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/moderations",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}",
                    },
                    json={"input": text},
                    timeout=5.0,
                )

                if response.status_code != 200:
                    # Fallback to patterns
                    return self._moderate_with_patterns(text)

                data = response.json()
                result = data["results"][0]

                violations = []
                for category, flagged in result["categories"].items():
                    if flagged:
                        score = result["category_scores"][category]
                        threshold = self.thresholds.get(category, 0.5)

                        if score >= threshold:
                            violations.append({
                                "category": category,
                                "score": score,
                                "threshold": threshold,
                                "flagged": True,
                            })

                return violations

        except Exception:
            # Fallback to patterns
            return self._moderate_with_patterns(text)

    def _moderate_with_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Moderate content using local pattern matching."""
        violations = []

        for category, pattern in self.patterns.items():
            if pattern.search(text):
                violations.append({
                    "category": category,
                    "score": 0.8,
                    "threshold": self.thresholds.get(category, 0.5),
                    "flagged": True,
                    "method": "pattern",
                })

        return violations

    def _transform_content(self, text: str) -> str:
        """Transform harmful content to safer alternative."""
        transformed = text

        for pattern in self.patterns.values():
            transformed = pattern.sub("[FILTERED]", transformed)

        return transformed
