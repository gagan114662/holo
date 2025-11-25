"""
SafeGuard AI - Content Safety and Compliance Layer
Our alternative to 2wai's FedBrain™

Features:
- Age-appropriate content filtering
- Curriculum alignment validation
- FERPA/COPPA compliance
- Harmful content detection
- Audit logging for compliance
"""
import asyncio
import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import anthropic

from ..config import settings

logger = logging.getLogger(__name__)


class ContentRating(Enum):
    """Age-appropriate content ratings"""
    ALL_AGES = "all_ages"        # K-12 safe
    TEEN = "teen"               # 13+ (middle/high school)
    MATURE = "mature"           # 18+ (not for K-12)
    BLOCKED = "blocked"         # Harmful content


class ViolationType(Enum):
    """Types of content policy violations"""
    NONE = "none"
    PROFANITY = "profanity"
    VIOLENCE = "violence"
    SEXUAL = "sexual"
    HATE_SPEECH = "hate_speech"
    SELF_HARM = "self_harm"
    PERSONAL_INFO = "personal_info"
    MISINFORMATION = "misinformation"
    OFF_TOPIC = "off_topic"
    CHEATING = "cheating"


@dataclass
class SafetyCheckResult:
    """Result of content safety check"""
    is_safe: bool
    rating: ContentRating
    violations: list[ViolationType]
    confidence: float
    filtered_content: Optional[str] = None
    explanation: str = ""
    suggestions: list[str] = field(default_factory=list)


@dataclass
class CurriculumAlignment:
    """Result of curriculum alignment check"""
    is_aligned: bool
    grade_level: str
    subject: str
    standards: list[str]  # e.g., ["CCSS.MATH.6.NS.1", "NGSS.MS-PS2-1"]
    confidence: float
    suggestions: list[str] = field(default_factory=list)


@dataclass
class AuditLogEntry:
    """Audit log entry for compliance"""
    timestamp: datetime
    user_id: str
    session_id: str
    action: str
    content_hash: str  # Hash of content (not actual content for privacy)
    safety_result: SafetyCheckResult
    metadata: dict = field(default_factory=dict)


class SafeGuardService:
    """
    Content safety and compliance service.

    Provides multi-layer protection:
    1. Pattern-based filtering (fast, catches obvious violations)
    2. AI-based analysis (thorough, catches nuanced issues)
    3. Curriculum alignment (ensures educational value)
    4. Audit logging (compliance/accountability)
    """

    def __init__(self):
        self.anthropic_client = None
        if settings.anthropic_api_key:
            self.anthropic_client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key
            )

        # Pattern-based filters (fast first pass)
        self._profanity_patterns = self._load_profanity_patterns()
        self._pii_patterns = self._compile_pii_patterns()

        # Audit log (in production, use database)
        self.audit_log: list[AuditLogEntry] = []
        self._audit_lock = asyncio.Lock()

        # Cache for repeated checks
        self._cache: dict[str, SafetyCheckResult] = {}
        self._cache_lock = asyncio.Lock()

    def _load_profanity_patterns(self) -> set[str]:
        """Load profanity word list"""
        # Basic list - in production, use comprehensive word list
        return {
            "fuck", "shit", "ass", "bitch", "damn", "crap",
            "hell", "bastard", "dick", "cock", "pussy",
            # Add more as needed
        }

    def _compile_pii_patterns(self) -> dict[str, re.Pattern]:
        """Compile regex patterns for PII detection"""
        return {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b'),
            "ssn": re.compile(r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b'),
            "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            "address": re.compile(r'\b\d+\s+[\w\s]+(?:street|st|avenue|ave|road|rd|drive|dr|lane|ln|court|ct|way|boulevard|blvd)\b', re.I),
        }

    async def check_content(
        self,
        content: str,
        user_age: Optional[int] = None,
        context: str = "tutoring",
        check_curriculum: bool = False,
        grade_level: Optional[str] = None,
        subject: Optional[str] = None
    ) -> SafetyCheckResult:
        """
        Check content for safety and appropriateness.

        Args:
            content: Text content to check
            user_age: User's age for age-appropriate filtering
            context: Context (tutoring, chat, etc.)
            check_curriculum: Whether to verify curriculum alignment
            grade_level: Expected grade level (K, 1-12)
            subject: Expected subject area

        Returns:
            SafetyCheckResult with safety assessment
        """
        # Check cache first
        cache_key = hashlib.md5(f"{content}:{user_age}:{context}".encode()).hexdigest()
        async with self._cache_lock:
            if cache_key in self._cache:
                return self._cache[cache_key]

        violations = []
        confidence = 1.0
        filtered_content = content
        suggestions = []

        # Layer 1: Pattern-based checks (fast)
        pattern_result = self._pattern_check(content)
        violations.extend(pattern_result["violations"])
        if pattern_result["filtered"]:
            filtered_content = pattern_result["filtered"]

        # Layer 2: PII detection
        pii_result = self._check_pii(content)
        if pii_result["has_pii"]:
            violations.append(ViolationType.PERSONAL_INFO)
            filtered_content = pii_result["redacted"]
            suggestions.append("Personal information was detected and redacted for privacy.")

        # Layer 3: AI-based analysis (if available and needed)
        if self.anthropic_client and (not violations or context == "tutoring"):
            ai_result = await self._ai_safety_check(content, user_age, context)
            if ai_result:
                violations.extend(ai_result.get("violations", []))
                confidence = ai_result.get("confidence", 0.8)
                suggestions.extend(ai_result.get("suggestions", []))

        # Determine rating based on violations and age
        rating = self._determine_rating(violations, user_age)

        # Check curriculum alignment if requested
        if check_curriculum and grade_level and subject:
            alignment = await self.check_curriculum_alignment(
                content, grade_level, subject
            )
            if not alignment.is_aligned:
                violations.append(ViolationType.OFF_TOPIC)
                suggestions.extend(alignment.suggestions)

        result = SafetyCheckResult(
            is_safe=rating != ContentRating.BLOCKED and len(violations) == 0,
            rating=rating,
            violations=list(set(violations)),  # Deduplicate
            confidence=confidence,
            filtered_content=filtered_content if filtered_content != content else None,
            explanation=self._generate_explanation(violations),
            suggestions=suggestions
        )

        # Cache result
        async with self._cache_lock:
            self._cache[cache_key] = result
            # Limit cache size
            if len(self._cache) > 10000:
                # Remove oldest entries
                keys = list(self._cache.keys())[:5000]
                for k in keys:
                    del self._cache[k]

        return result

    def _pattern_check(self, content: str) -> dict:
        """Fast pattern-based content check"""
        violations = []
        filtered = content
        words = content.lower().split()

        # Check for profanity
        for word in words:
            clean_word = re.sub(r'[^a-z]', '', word)
            if clean_word in self._profanity_patterns:
                violations.append(ViolationType.PROFANITY)
                # Replace with asterisks
                filtered = re.sub(
                    rf'\b{re.escape(word)}\b',
                    '*' * len(word),
                    filtered,
                    flags=re.IGNORECASE
                )

        return {
            "violations": violations,
            "filtered": filtered if filtered != content else None
        }

    def _check_pii(self, content: str) -> dict:
        """Check for personally identifiable information"""
        has_pii = False
        redacted = content

        for pii_type, pattern in self._pii_patterns.items():
            matches = pattern.findall(content)
            if matches:
                has_pii = True
                for match in matches:
                    redacted = redacted.replace(match, f"[{pii_type.upper()}_REDACTED]")

        return {
            "has_pii": has_pii,
            "redacted": redacted
        }

    async def _ai_safety_check(
        self,
        content: str,
        user_age: Optional[int],
        context: str
    ) -> Optional[dict]:
        """AI-powered content safety analysis"""
        if not self.anthropic_client:
            return None

        age_context = f"The user is {user_age} years old." if user_age else "The user's age is unknown."

        prompt = f"""Analyze this content for safety in an educational {context} context.
{age_context}

Content to analyze:
"{content}"

Check for:
1. Inappropriate language or themes for students
2. Potential misinformation or factual errors
3. Content that could encourage cheating or academic dishonesty
4. Harmful suggestions (violence, self-harm, etc.)
5. Content that deviates from educational purposes

Respond in JSON format:
{{
    "is_safe": true/false,
    "violations": ["list of violation types if any"],
    "confidence": 0.0-1.0,
    "suggestions": ["constructive suggestions if issues found"],
    "educational_value": "low/medium/high"
}}

Violation types: none, profanity, violence, sexual, hate_speech, self_harm, misinformation, off_topic, cheating"""

        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse JSON response
            text = response.content[0].text
            # Extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                result = json.loads(json_match.group())
                # Convert violation strings to enum
                violations = []
                for v in result.get("violations", []):
                    try:
                        violations.append(ViolationType(v.lower()))
                    except ValueError:
                        pass
                result["violations"] = violations
                return result

        except Exception as e:
            logger.error(f"AI safety check failed: {e}")

        return None

    def _determine_rating(
        self,
        violations: list[ViolationType],
        user_age: Optional[int]
    ) -> ContentRating:
        """Determine content rating based on violations and user age"""
        if ViolationType.SEXUAL in violations or ViolationType.SELF_HARM in violations:
            return ContentRating.BLOCKED

        if ViolationType.VIOLENCE in violations or ViolationType.HATE_SPEECH in violations:
            return ContentRating.BLOCKED

        if ViolationType.PROFANITY in violations:
            return ContentRating.TEEN if user_age and user_age >= 13 else ContentRating.BLOCKED

        if violations:
            return ContentRating.TEEN

        return ContentRating.ALL_AGES

    def _generate_explanation(self, violations: list[ViolationType]) -> str:
        """Generate human-readable explanation of violations"""
        if not violations:
            return "Content passed all safety checks."

        explanations = {
            ViolationType.PROFANITY: "Contains inappropriate language",
            ViolationType.VIOLENCE: "Contains violent content",
            ViolationType.SEXUAL: "Contains sexual content",
            ViolationType.HATE_SPEECH: "Contains hate speech or discrimination",
            ViolationType.SELF_HARM: "Contains self-harm related content",
            ViolationType.PERSONAL_INFO: "Contains personal information",
            ViolationType.MISINFORMATION: "May contain inaccurate information",
            ViolationType.OFF_TOPIC: "Content is off-topic for educational context",
            ViolationType.CHEATING: "May encourage academic dishonesty"
        }

        parts = [explanations.get(v, str(v)) for v in violations]
        return "Issues found: " + "; ".join(parts)

    async def check_curriculum_alignment(
        self,
        content: str,
        grade_level: str,
        subject: str
    ) -> CurriculumAlignment:
        """
        Check if content aligns with curriculum standards.

        Args:
            content: Educational content to check
            grade_level: Grade level (K, 1-12)
            subject: Subject area (math, science, etc.)

        Returns:
            CurriculumAlignment result
        """
        if not self.anthropic_client:
            # Without AI, assume aligned (fail open)
            return CurriculumAlignment(
                is_aligned=True,
                grade_level=grade_level,
                subject=subject,
                standards=[],
                confidence=0.5,
                suggestions=["AI validation not available"]
            )

        prompt = f"""Analyze this educational content for curriculum alignment.

Grade Level: {grade_level}
Subject: {subject}

Content:
"{content[:1000]}"

Determine:
1. Is this content appropriate for the grade level?
2. Does it align with the subject area?
3. What curriculum standards might it address? (Common Core, NGSS, etc.)

Respond in JSON:
{{
    "is_aligned": true/false,
    "appropriate_grade_range": "e.g., 6-8",
    "standards": ["standard codes if identifiable"],
    "confidence": 0.0-1.0,
    "suggestions": ["suggestions for improvement"]
}}"""

        try:
            response = await self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            text = response.content[0].text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                result = json.loads(json_match.group())
                return CurriculumAlignment(
                    is_aligned=result.get("is_aligned", True),
                    grade_level=grade_level,
                    subject=subject,
                    standards=result.get("standards", []),
                    confidence=result.get("confidence", 0.7),
                    suggestions=result.get("suggestions", [])
                )

        except Exception as e:
            logger.error(f"Curriculum alignment check failed: {e}")

        return CurriculumAlignment(
            is_aligned=True,
            grade_level=grade_level,
            subject=subject,
            standards=[],
            confidence=0.5,
            suggestions=[]
        )

    async def log_audit(
        self,
        user_id: str,
        session_id: str,
        action: str,
        content: str,
        safety_result: SafetyCheckResult,
        metadata: Optional[dict] = None
    ):
        """
        Log an audit entry for compliance tracking.

        In production, this would write to a secure, immutable audit database.
        """
        # Hash content for privacy (don't store actual content)
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        entry = AuditLogEntry(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            action=action,
            content_hash=content_hash,
            safety_result=safety_result,
            metadata=metadata or {}
        )

        async with self._audit_lock:
            self.audit_log.append(entry)
            # In production, write to database
            # Keep in-memory log bounded
            if len(self.audit_log) > 100000:
                self.audit_log = self.audit_log[-50000:]

        logger.info(
            f"Audit: user={user_id} session={session_id} action={action} "
            f"safe={safety_result.is_safe} violations={len(safety_result.violations)}"
        )

    async def get_compliance_report(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        user_id: Optional[str] = None
    ) -> dict:
        """
        Generate compliance report for audit purposes.

        Required for FERPA/COPPA compliance documentation.
        """
        async with self._audit_lock:
            entries = self.audit_log

        if start_date:
            entries = [e for e in entries if e.timestamp >= start_date]
        if end_date:
            entries = [e for e in entries if e.timestamp <= end_date]
        if user_id:
            entries = [e for e in entries if e.user_id == user_id]

        # Aggregate statistics
        total = len(entries)
        safe_count = sum(1 for e in entries if e.safety_result.is_safe)
        violations_by_type = {}
        for e in entries:
            for v in e.safety_result.violations:
                violations_by_type[v.value] = violations_by_type.get(v.value, 0) + 1

        return {
            "report_generated": datetime.utcnow().isoformat(),
            "period": {
                "start": start_date.isoformat() if start_date else "all",
                "end": end_date.isoformat() if end_date else "all"
            },
            "total_checks": total,
            "safe_content": safe_count,
            "flagged_content": total - safe_count,
            "safety_rate": safe_count / total if total > 0 else 1.0,
            "violations_by_type": violations_by_type,
            "unique_users": len(set(e.user_id for e in entries)),
            "unique_sessions": len(set(e.session_id for e in entries))
        }


# Global service instance
safeguard_service = SafeGuardService()
