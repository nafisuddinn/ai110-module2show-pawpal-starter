from dataclasses import dataclass, field
from typing import List, Optional


# ---------------------------------------------------------------------------
# Data classes — pure data holders, no scheduling logic
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    special_needs: List[str] = field(default_factory=list)

    def get_info(self) -> str:
        """Return a human-readable summary of the pet."""
        pass


@dataclass
class Task:
    name: str
    category: str          # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    duration: int          # minutes
    priority: int          # 1 (low) – 5 (high)
    frequency: str = "daily"
    notes: str = ""

    def get_summary(self) -> str:
        """Return a one-line description of the task."""
        pass


@dataclass
class ScheduledTask:
    task: Task
    time_slot: str         # e.g. "08:00"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def get_label(self) -> str:
        """Return a display-friendly label for the scheduled task."""
        pass


# ---------------------------------------------------------------------------
# Regular classes — hold behaviour / mutable state
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, time_available: int, preferences: Optional[List[str]] = None):
        self.name: str = name
        self.time_available: int = time_available   # minutes available per day
        self.preferences: List[str] = preferences or []
        self._pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        pass

    def get_pets(self) -> List[Pet]:
        """Return the owner's list of pets."""
        pass


class Schedule:
    def __init__(self, date: str):
        self.date: str = date
        self.scheduled_tasks: List[ScheduledTask] = []

    def add_task(self, task: ScheduledTask) -> None:
        """Append a scheduled task to the plan."""
        pass

    def get_total_duration(self) -> int:
        """Return the sum of all task durations in minutes."""
        pass

    def display_plan(self) -> str:
        """Return a formatted, human-readable version of the daily plan."""
        pass

    def generate_summary(self) -> str:
        """Return a short summary including total time and task count."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.tasks: List[Task] = []
        self.time_limit: int = owner.time_available

    def add_task(self, task: Task) -> None:
        """Add a task to the pool of tasks the scheduler can consider."""
        pass

    def remove_task(self, name: str) -> None:
        """Remove a task from the pool by name."""
        pass

    def filter_by_priority(self, min_priority: int = 1) -> List[Task]:
        """Return tasks at or above the given priority threshold."""
        pass

    def sort_tasks(self) -> List[Task]:
        """Return tasks sorted by priority (highest first), then duration."""
        pass

    def generate_schedule(self, date: str) -> Schedule:
        """
        Build and return a Schedule for the given date.

        Selects tasks by priority, respects the owner's time_available
        constraint, and assigns time slots.
        """
        pass

    def explain_reasoning(self) -> str:
        """Return a plain-English explanation of why the schedule was built as-is."""
        pass
