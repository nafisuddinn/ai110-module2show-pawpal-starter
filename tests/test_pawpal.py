from pawpal_system import Task, ScheduledTask, Scheduler, Schedule, Owner, Pet


# ---------------------------------------------------------------------------
# Test 1: Task Completion
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    """
    Verify that calling mark_complete() flips is_completed from False to True.

    We start with a fresh ScheduledTask (is_completed defaults to False),
    call mark_complete(), and assert the flag changed. This confirms the method
    actually mutates the object rather than being a no-op.
    """
    task = Task(name="Morning Walk", category="walk", duration=30, priority=5)
    scheduled = ScheduledTask(task=task, time_slot="08:00")

    # Sanity-check the default state before acting
    assert scheduled.is_completed is False

    scheduled.mark_complete()

    assert scheduled.is_completed is True


# ---------------------------------------------------------------------------
# Test 2: Task Addition
# ---------------------------------------------------------------------------

def test_adding_task_increases_scheduler_task_count():
    """
    Verify that add_task() increases the number of tasks the Scheduler holds.

    The Scheduler is the object responsible for managing the task pool, so
    this is the right place to test task addition. We start with zero tasks,
    add one, and confirm the count goes from 0 to 1.
    """
    owner = Owner(name="Alex", time_available=90)
    pet = Pet(name="Biscuit", species="dog", breed="Beagle", age=3)
    scheduler = Scheduler(owner=owner, pet=pet)

    assert len(scheduler.tasks) == 0

    task = Task(name="Breakfast", category="feeding", duration=10, priority=5)
    scheduler.add_task(task)

    assert len(scheduler.tasks) == 1


# ---------------------------------------------------------------------------
# Test 3: Sorting Correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """
    Verify that sort_by_time() returns tasks in ascending time order.

    We add three tasks with deliberately out-of-order preferred start times
    and confirm the sorted result matches the expected chronological sequence.
    Tasks with no time set use "99:99" as a fallback, so they should appear last.
    """
    owner = Owner(name="Sam", time_available=120)
    pet = Pet(name="Mochi", species="cat", breed="Tabby", age=2)
    scheduler = Scheduler(owner=owner, pet=pet)

    task_afternoon = Task(name="Afternoon Nap", category="enrichment", duration=20, priority=3, time="14:00")
    task_morning   = Task(name="Morning Meds",  category="meds",        duration=5,  priority=5, time="08:00")
    task_midday    = Task(name="Midday Feeding", category="feeding",    duration=10, priority=4, time="12:30")
    task_no_time   = Task(name="Free Play",      category="enrichment", duration=15, priority=2, time="")

    # Add in random order to confirm sort is not relying on insertion order
    for t in [task_afternoon, task_no_time, task_morning, task_midday]:
        scheduler.add_task(t)

    sorted_tasks = scheduler.sort_by_time()

    assert sorted_tasks[0].name == "Morning Meds"
    assert sorted_tasks[1].name == "Midday Feeding"
    assert sorted_tasks[2].name == "Afternoon Nap"
    assert sorted_tasks[3].name == "Free Play"   # no time → sorted last


# ---------------------------------------------------------------------------
# Test 4: Recurrence Logic
# ---------------------------------------------------------------------------

def test_mark_complete_daily_task_creates_next_day_task():
    """
    Confirm that marking a daily task complete returns a new Task due the
    following day.

    mark_complete() delegates to Task.next_occurrence(), which adds one day
    to the current due_date. We pin the due_date to a known value so the
    expected output is deterministic regardless of when the test runs.
    """
    task = Task(
        name="Evening Walk",
        category="walk",
        duration=30,
        priority=4,
        frequency="daily",
        due_date="2024-06-10",
    )
    scheduled = ScheduledTask(task=task, time_slot="18:00")

    next_task = scheduled.mark_complete()

    # The original task should now be marked done
    assert scheduled.is_completed is True

    # A new Task should have been returned (not None)
    assert next_task is not None

    # Its due_date must be exactly one day after the original
    assert next_task.due_date == "2024-06-11"

    # Core fields must be preserved on the new Task
    assert next_task.name      == task.name
    assert next_task.frequency == "daily"


# ---------------------------------------------------------------------------
# Test 5: Conflict Detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_time_slots():
    """
    Verify that detect_conflicts() returns a warning when two tasks in a
    schedule have overlapping time intervals.

    We build a Schedule manually and add two tasks whose durations overlap:
      - Task A: 08:00 for 60 min → occupies 08:00–09:00
      - Task B: 08:30 for 30 min → occupies 08:30–09:00
    These share the window 08:30–09:00, so detect_conflicts() must flag them.

    We also verify that two non-overlapping tasks produce no warnings.
    """
    owner = Owner(name="Jordan", time_available=180)
    pet   = Pet(name="Pepper", species="dog", breed="Poodle", age=5)

    # --- Overlapping scenario ---
    schedule_conflict = Schedule(date="2024-06-10", owner=owner, pet=pet)

    task_a = Task(name="Long Walk",     category="walk",    duration=60, priority=5)
    task_b = Task(name="Vet Check-in",  category="meds",    duration=30, priority=5)

    # Different time_slot strings so Schedule.add_task() does not raise;
    # the interval overlap is what detect_conflicts() must catch.
    schedule_conflict.scheduled_tasks.append(ScheduledTask(task=task_a, time_slot="08:00"))
    schedule_conflict.scheduled_tasks.append(ScheduledTask(task=task_b, time_slot="08:30"))

    scheduler = Scheduler(owner=owner, pet=pet)
    conflicts = scheduler.detect_conflicts(schedule_conflict)

    assert len(conflicts) >= 1
    assert any("Long Walk" in w and "Vet Check-in" in w for w in conflicts)

    # --- Non-overlapping scenario ---
    schedule_clean = Schedule(date="2024-06-10", owner=owner, pet=pet)

    task_c = Task(name="Breakfast",  category="feeding", duration=15, priority=5)
    task_d = Task(name="Playtime",   category="enrichment", duration=20, priority=3)

    # Task C: 08:00–08:15 | Task D: 08:15–08:35 → clean handoff, no overlap
    schedule_clean.scheduled_tasks.append(ScheduledTask(task=task_c, time_slot="08:00"))
    schedule_clean.scheduled_tasks.append(ScheduledTask(task=task_d, time_slot="08:15"))

    no_conflicts = scheduler.detect_conflicts(schedule_clean)

    assert no_conflicts == []
