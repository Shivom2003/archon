"""All enumerations used throughout Archon."""

from enum import StrEnum


class ProjectType(StrEnum):
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app"
    CLI_TOOL = "cli_tool"
    API_SERVICE = "api_service"
    DATA_PIPELINE = "data_pipeline"
    ML_AI_SYSTEM = "ml_ai_system"
    LIBRARY_SDK = "library_sdk"
    DESKTOP_APP = "desktop_app"
    IOT_EMBEDDED = "iot_embedded"
    OTHER = "other"

    @property
    def label(self) -> str:
        return {
            "web_app": "Web Application",
            "mobile_app": "Mobile Application",
            "cli_tool": "CLI Tool",
            "api_service": "API / Backend Service",
            "data_pipeline": "Data Pipeline",
            "ml_ai_system": "ML / AI System",
            "library_sdk": "Library / SDK",
            "desktop_app": "Desktop Application",
            "iot_embedded": "IoT / Embedded",
            "other": "Other",
        }[self.value]


class ConsumerScale(StrEnum):
    """Scale from the end-user / consumer perspective."""

    PERSONAL = "personal"  # 1 user (yourself)
    SMALL_TEAM = "small_team"  # 2–20 users (internal tool, small team)
    SMALL_BUSINESS = "small_business"  # 20–500 users
    MID_MARKET = "mid_market"  # 500–50k users
    ENTERPRISE = "enterprise"  # 50k+ users / enterprise contracts

    @property
    def label(self) -> str:
        return {
            "personal": "Personal (just me)",
            "small_team": "Small Team (2–20 users)",
            "small_business": "Small Business (20–500 users)",
            "mid_market": "Mid-Market (500–50k users)",
            "enterprise": "Enterprise (50k+ users)",
        }[self.value]


class DevScale(StrEnum):
    """Scale from the development team perspective."""

    SOLO = "solo"  # 1 developer
    SMALL_TEAM = "small_team"  # 2–5 developers
    STARTUP = "startup"  # 5–20 developers
    SME = "sme"  # 20–100 developers
    ENTERPRISE = "enterprise"  # 100+ developers

    @property
    def label(self) -> str:
        return {
            "solo": "Solo Developer",
            "small_team": "Small Team (2–5 devs)",
            "startup": "Startup (5–20 devs)",
            "sme": "SME / Agency (20–100 devs)",
            "enterprise": "Enterprise (100+ devs)",
        }[self.value]


class AgenticTool(StrEnum):
    """Supported agentic coding tools."""

    CLAUDE_CODE = "claude_code"
    CODEX = "codex"
    CURSOR = "cursor"
    KIRO = "kiro"
    ANTIGRAVITY = "antigravity"
    WINDSURF = "windsurf"
    COPILOT = "copilot"
    DEVIN = "devin"
    OTHER = "other"

    @property
    def label(self) -> str:
        return {
            "claude_code": "Claude Code (Anthropic)",
            "codex": "Codex / ChatGPT (OpenAI)",
            "cursor": "Cursor",
            "kiro": "Kiro (Amazon)",
            "antigravity": "Antigravity",
            "windsurf": "Windsurf (Codeium)",
            "copilot": "GitHub Copilot",
            "devin": "Devin (Cognition)",
            "other": "Other",
        }[self.value]

    @property
    def strengths(self) -> list[str]:
        """Known strengths — used for agent assignment recommendations."""
        return {
            "claude_code": [
                "complex reasoning",
                "refactoring",
                "backend logic",
                "multi-file edits",
                "test writing",
            ],
            "codex": [
                "frontend autocomplete",
                "boilerplate generation",
                "familiar patterns",
            ],
            "cursor": [
                "context-aware edits",
                "inline suggestions",
                "large codebase navigation",
            ],
            "kiro": [
                "spec-driven development",
                "structured task execution",
                "requirements tracing",
            ],
            "antigravity": ["autonomous execution", "long-running tasks"],
            "windsurf": ["fast inline edits", "autocomplete"],
            "copilot": ["IDE integration", "autocomplete", "chat"],
            "devin": ["autonomous debugging", "repo-wide changes"],
            "other": [],
        }[self.value]


class SubscriptionTier(StrEnum):
    """Subscription tiers for agentic tools."""

    FREE = "free"
    PRO = "pro"
    MAX = "max"
    TEAM = "team"
    ENTERPRISE = "enterprise"
    API = "api"  # Direct API access (no GUI limits)

    @property
    def label(self) -> str:
        return {
            "free": "Free",
            "pro": "Pro",
            "max": "Max",
            "team": "Team",
            "enterprise": "Enterprise",
            "api": "API (direct)",
        }[self.value]


class ExpertiseLevel(StrEnum):
    """Developer's self-assessed expertise level."""

    NOVICE = "novice"  # Learning, needs guidance on tech stack
    INTERMEDIATE = "intermediate"  # Comfortable, knows the basics
    EXPERT = "expert"  # Opinionated, knows exactly what they want

    @property
    def label(self) -> str:
        return {
            "novice": "Novice (I'm still learning — help me choose a stack)",
            "intermediate": "Intermediate (I know the basics, some guidance welcome)",
            "expert": "Expert (I'm opinionated — keep the recommendations minimal)",
        }[self.value]


class ComplianceRequirement(StrEnum):
    """Regulatory / compliance requirements."""

    NONE = "none"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    CCPA = "ccpa"
    OTHER = "other"


class Priority(StrEnum):
    """Feature / task priority."""

    MUST_HAVE = "must_have"
    SHOULD_HAVE = "should_have"
    NICE_TO_HAVE = "nice_to_have"
    FUTURE = "future"


class RoadmapPhaseStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
