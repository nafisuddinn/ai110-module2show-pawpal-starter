from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime, timedelta


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
        # Join special needs into a comma-separated string, or show "none"
        needs = ", ".join(self.special_needs) if self.special_needs else "none"
        return f"{self.name} ({self.breed} {self.species}, age {self.age}) — special needs: {needs}"


@dataclass
class Task:
    name: str
    category: str       # e.g. "walk", "feeding", "meds", "grooming", "enrichment"
    duration: int       # minutes
    priority: int       # 1 (low) – 5 (high)
    frequency: str = "daily"
    notes: str = ""

    def get_summary(self) -> str:
        """Return a one-line description of the task."""
        return f"[P{self.priority}] {self.name} ({self.category}, {self.duration} min, {self.frequency})"


@dataclass
class ScheduledTask:
    task: Task
    time_slot: str      # "HH:MM" string, e.g. "08:00"
    is_completed: bool = False

    def mark_complete(self) -> None:
        """Flip the completion flag to True."""
        self.is_completed = True

    def get_label(self) -> str:
        """Return a display-friendly label showing slot, status, name, and duration."""
        status = "✓" if self.is_completed else "○"
        return f"{self.time_slot}  {status}  {self.task.name} ({self.task.duration} min)"


# ---------------------------------------------------------------------------
# Regular classes — hold behaviour / mutable state
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, time_available: int, preferences: Optional[List[str]] = None):
        self.name: str = name
        self.time_available: int = time_available   # total minutes available per day
        self.preferences: List[str] = preferences or []
        self._pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Append a Pet to the owner's internal list."""
        self._pets.append(pet)

    def get_pets(self) -> List[Pet]:
        """Return a copy of the pet list so callers can't mutate the internal state."""
        return list(self._pets)


class Schedule:
    def __init__(self, date: str, owner: Owner, pet: Pet):
        self.date: str = date
        # Storing owner and pet on the schedule makes it self-contained —
        # we can display whose plan it is without passing context externally.
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.scheduled_tasks: List[ScheduledTask] = []

    def add_task(self, scheduled_task: ScheduledTask) -> None:
        """
        Append a ScheduledTask to the plan.

        Raises ValueError if the time slot is already occupied, preventing
        overlapping tasks from being silently added.
        """
        occupied_slots = {st.time_slot for st in self.scheduled_tasks}
        if scheduled_task.time_slot in occupied_slots:
            raise ValueError(
                f"Time slot {scheduled_task.time_slot} is already occupied."
            )
        self.scheduled_tasks.append(scheduled_task)

    def get_total_duration(self) -> int:
        """Sum the duration of every task currently in the schedule."""
        return sum(st.task.duration for st in self.scheduled_tasks)

    def display_plan(self) -> str:
        """
        Return a formatted, human-readable version of the daily plan.

        Tasks are sorted by time slot so the output is always chronological,
        regardless of the order they were added.
        """
        if not self.scheduled_tasks:
            return f"No tasks scheduled for {self.date}."

        lines = [
            f"Daily Plan for {self.pet.name}  —  {self.date}  (Owner: {self.owner.name})",
            "-" * 55,
        ]

        # Sort by time_slot string; "HH:MM" format sorts correctly lexicographically
        for st in sorted(self.scheduled_tasks, key=lambda x: x.time_slot):
            lines.append(st.get_label())

        lines.append("-" * 55)
        total = self.get_total_duration()
        lines.append(f"Total: {total} min / {self.owner.time_available} min available")
        return "\n".join(lines)

    def generate_summary(self) -> str:
        """Return a short one-line summary of the plan."""
        count = len(self.scheduled_tasks)
        total = self.get_total_duration()
        remaining = self.owner.time_available - total
        return (
            f"{count} task(s) scheduled for {self.date}, "
            f"totaling {total} min — {remaining} min remaining."
        )


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner: Owner = owner
        self.pet: Pet = pet
        self.tasks: List[Task] = []
        # Reasoning notes are populated during generate_schedule() and read by
        # explain_reasoning(), so both methods stay in sync automatically.
        self._last_reasoning: List[str] = []

    def add_task(self, task: Task) -> None:
        """Add a Task to the pool the scheduler can draw from."""
        self.tasks.append(task)

    def remove_task(self, name: str) -> None:
        """
        Remove every task whose name matches (case-insensitive).

        Using a list comprehension keeps only tasks that do NOT match,
        which is simpler and safer than mutating the list while iterating.
        """
        self.tasks = [t for t in self.tasks if t.name.lower() != name.lower()]

    def filter_by_priority(self, min_priority: int = 1) -> List[Task]:
        """Return tasks whose priority is at or above the threshold."""
        return [t for t in self.tasks if t.priority >= min_priority]

    def sort_tasks(self) -> List[Task]:
        """
        Sort tasks by priority descending (5 = most urgent first), then by
        duration ascending as a tiebreaker (shorter tasks first so more tasks
        can fit within the time limit).
        """
        return sorted(self.tasks, key=lambda t: (-t.priority, t.duration))

    def generate_schedule(self, date: str) -> Schedule:
        """
        Build and return a Schedule for the given date.

        Algorithm:
          1. Read time_available fresh from owner (avoids stale snapshot).
          2. Separate daily tasks (eligible today) from non-daily tasks (skipped).
          3. Sort eligible tasks by priority then duration.
          4. Walk through the sorted list, assigning consecutive time slots
             starting at 08:00 and advancing by each task's duration.
          5. Skip any task that would push the total past the time limit.
          6. Record a reasoning note for every decision made.
        """
        self._last_reasoning = []
        schedule = Schedule(date=date, owner=self.owner, pet=self.pet)

        # Read directly from owner so changes to time_available are always respected
        time_limit = self.owner.time_available
        time_used = 0

        # Separate eligible (daily) from non-daily tasks up front
        eligible = [t for t in self.sort_tasks() if t.frequency == "daily"]
        non_daily = [t for t in self.tasks if t.frequency != "daily"]

        if non_daily:
            names = ", ".join(t.name for t in non_daily)
            self._last_reasoning.append(
                f"Skipped non-daily tasks (need manual scheduling): {names}."
            )

        # Time slots are computed as datetime objects so arithmetic is exact,
        # then formatted back to "HH:MM" strings for storage.
        current_time = datetime.strptime("08:00", "%H:%M")

        for task in eligible:
            if time_used + task.duration > time_limit:
                # Task doesn't fit — log why and move on to the next one
                self._last_reasoning.append(
                    f"Skipped '{task.name}' ({task.duration} min) — would exceed "
                    f"the {time_limit}-min daily limit."
                )
                continue

            time_slot = current_time.strftime("%H:%M")
            schedule.add_task(ScheduledTask(task=task, time_slot=time_slot))

            self._last_reasoning.append(
                f"Scheduled '{task.name}' at {time_slot} "
                f"(priority {task.priority}, {task.duration} min)."
            )

            # Advance the clock by this task's duration for the next slot
            time_used += task.duration
            current_time += timedelta(minutes=task.duration)

        return schedule

    def explain_reasoning(self) -> str:
        """
        Return a plain-English explanation of the last schedule generated.

        explain_reasoning() reads _last_reasoning, which is populated by
        generate_schedule(), so they're always in sync without needing arguments.
        """
        if not self._last_reasoning:
            return "No schedule has been generated yet. Call generate_schedule() first."
        return "Scheduling reasoning:\n" + "\n".join(
            f"  • {note}" for note in self._last_reasoning
        )
