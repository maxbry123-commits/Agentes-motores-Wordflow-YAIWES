"""agent-resume: checkpoint + resume for long-running agent jobs.

The public API is intentionally tiny:

- `resume_or_start(...)` for the common case.
- `Resumable` for the advanced case.
- `JsonlStore`, `InMemoryStore`, `Sink` for the storage layer.
- `Checkpoint` if you want to introspect the records yourself.
- `CheckpointCorrupt`, `NoCheckpoint` for error handling.
"""

from .checkpoint import Checkpoint
from .exceptions import AgentResumeError, CheckpointCorrupt, NoCheckpoint
from .resumable import Resumable
from .runner import resume_or_start
from .store import InMemoryStore, JsonlStore, Sink

__all__ = [
    "AgentResumeError",
    "Checkpoint",
    "CheckpointCorrupt",
    "InMemoryStore",
    "JsonlStore",
    "NoCheckpoint",
    "Resumable",
    "Sink",
    "resume_or_start",
]

__version__ = "0.1.0"
