from pawpal_system import Task, ScheduledTask, Scheduler, Owner, Pet


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
