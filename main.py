from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import date

# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

owner = Owner(
    name="Alex",
    time_available=90,          # 90 minutes available today
    preferences=["morning walks", "short sessions"]
)

# ---------------------------------------------------------------------------
# Pets
# ---------------------------------------------------------------------------

dog = Pet(name="Biscuit", species="dog", breed="Beagle", age=3)
cat = Pet(name="Luna",    species="cat", breed="Siamese", age=5, special_needs=["daily eye drops"])

owner.add_pet(dog)
owner.add_pet(cat)

# ---------------------------------------------------------------------------
# Tasks — three for the dog, one for the cat
# ---------------------------------------------------------------------------

morning_walk  = Task(name="Morning Walk",   category="walk",     duration=30, priority=5)
breakfast     = Task(name="Breakfast",      category="feeding",  duration=10, priority=5)
fetch         = Task(name="Fetch / Play",   category="enrichment", duration=20, priority=3)
eye_drops     = Task(name="Eye Drops",      category="meds",     duration=5,  priority=5, notes="Luna — one drop each eye")

# ---------------------------------------------------------------------------
# Build a scheduler for each pet and generate today's plan
# ---------------------------------------------------------------------------

today = date.today().strftime("%Y-%m-%d")

# --- Dog schedule ---
dog_scheduler = Scheduler(owner=owner, pet=dog)
dog_scheduler.add_task(morning_walk)
dog_scheduler.add_task(breakfast)
dog_scheduler.add_task(fetch)

dog_schedule = dog_scheduler.generate_schedule(date=today)

# --- Cat schedule ---
cat_scheduler = Scheduler(owner=owner, pet=cat)
cat_scheduler.add_task(eye_drops)

cat_schedule = cat_scheduler.generate_schedule(date=today)

# ---------------------------------------------------------------------------
# Print today's schedule
# ---------------------------------------------------------------------------

print("=" * 55)
print("           TODAY'S SCHEDULE")
print("=" * 55)

print(dog_schedule.display_plan())
print()
print(dog_schedule.generate_summary())
print()
print(dog_scheduler.explain_reasoning())

print()
print("-" * 55)
print()

print(cat_schedule.display_plan())
print()
print(cat_schedule.generate_summary())
print()
print(cat_scheduler.explain_reasoning())

print()
print("=" * 55)
print(f"Owner: {owner.name}  |  Pets: {', '.join(p.name for p in owner.get_pets())}")
print("=" * 55)
