"""Template profile registry and compatibility metadata."""

from __future__ import annotations

from dataclasses import dataclass

from .templates import TEMPLATE_VERSION


@dataclass(frozen=True, slots=True)
class TemplateProfile:
    """Compatibility metadata for a generated-project profile."""

    name: str
    version: str
    ai_enabled: bool
    description: str


TEMPLATE_PROFILES: tuple[TemplateProfile, ...] = (
    TemplateProfile(
        name="default",
        version=TEMPLATE_VERSION,
        ai_enabled=False,
        description="Production FastAPI foundation without AI dependencies.",
    ),
    TemplateProfile(
        name="ai",
        version=TEMPLATE_VERSION,
        ai_enabled=True,
        description="Production FastAPI foundation with the optional provider-neutral AI boundary.",
    ),
)


def get_template_profile(name: str) -> TemplateProfile:
    """Return a registered template profile."""
    for profile in TEMPLATE_PROFILES:
        if profile.name == name:
            return profile
    raise ValueError(f"unknown template profile: {name!r}")
