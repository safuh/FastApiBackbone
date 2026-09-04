"""Optional database-backed identity persistence."""

from .models import User
from .repository import UserCredentialRepository

__all__ = ["User", "UserCredentialRepository"]
