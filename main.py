from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(id="o1", name="Alex", email="alex@email.com")

# Create pets
buddy = Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", owner_id="o1")
whiskers = Pet(id="p2", name="Whiskers", species="Cat", breed="Siamese", owner_id="o1")

owner.add_pet(buddy)
owner.add_pet(whiskers)

# Add tasks OUT OF ORDER intentionally
vet_checkup = Task(
    id="t1", title="Vet Checkup",
    description="Annual checkup", pet_id="p1",
    time=datetime(2026, 3, 29, 14, 0)
)

morning_walk = Task(
    id="t2", title="Morning Walk",
    description="30 min walk", pet_id="p1",
    time=datetime(2026, 3, 29, 8, 0)
)

feeding = Task(
    id="t3", title="Feeding",
    description="Fill food and water", pet_id="p2",
    time=datetime(2026, 3, 29, 9, 0)
)

evening_grooming = Task(
    id="t4", title="Evening Grooming",
    description="Brush coat", pet_id="p2",
    time=datetime(2026, 3, 29, 18, 0)
)

# Intentional conflict: bath is scheduled at the same time as feeding (9:00 AM)
bath = Task(
    id="t5", title="Bath Time",
    description="Scrub down", pet_id="p1",
    time=datetime(2026, 3, 29, 9, 0)
)

buddy.add_task(vet_checkup)
buddy.add_task(morning_walk)
buddy.add_task(bath)                 # 9:00 AM — conflicts with feeding
whiskers.add_task(evening_grooming)
whiskers.add_task(feeding)           # 9:00 AM — conflicts with bath

# Mark one task complete to test filtering
morning_walk.mark_complete()

scheduler = Scheduler(owner)

# --- Sort by time ---
print("===== Sorted by Time =====")
for task in scheduler.sort_by_time():
    pet_name = next(p.name for p in owner.get_pets() if p.id == task.pet_id)
    status = "Done" if task.is_complete else "Pending"
    print(f"{task.time.strftime('%I:%M %p')} | {pet_name} | {task.title} | {status}")

print()

# --- Filter: incomplete only ---
print("===== Incomplete Tasks =====")
for task in scheduler.filter_tasks(is_complete=False):
    pet_name = next(p.name for p in owner.get_pets() if p.id == task.pet_id)
    print(f"{task.title} | {pet_name}")

print()

# --- Filter: by pet name ---
print("===== Whiskers' Tasks =====")
for task in scheduler.filter_tasks(pet_name="Whiskers"):
    print(f"{task.title} | {'Done' if task.is_complete else 'Pending'}")

print()

# --- Conflict detection ---
print("===== Conflict Check =====")
conflicts = scheduler.get_conflicts()
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("No scheduling conflicts found.")
