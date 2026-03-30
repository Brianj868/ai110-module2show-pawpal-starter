from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(id="o1", name="Alex", email="alex@email.com")

# Create pets
buddy = Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", owner_id="o1")
whiskers = Pet(id="p2", name="Whiskers", species="Cat", breed="Siamese", owner_id="o1")

owner.add_pet(buddy)
owner.add_pet(whiskers)

# Create tasks with different times
morning_walk = Task(
    id="t1",
    title="Morning Walk",
    description="30 minute walk around the block",
    pet_id="p1",
    time=datetime(2026, 3, 29, 8, 0),
    frequency="daily"
)

feeding = Task(
    id="t2",
    title="Feeding",
    description="Fill food and water bowls",
    pet_id="p2",
    time=datetime(2026, 3, 29, 9, 0),
    frequency="daily"
)

vet_checkup = Task(
    id="t3",
    title="Vet Checkup",
    description="Annual checkup at the vet",
    pet_id="p1",
    time=datetime(2026, 3, 29, 14, 0),
    frequency=None
)

buddy.add_task(morning_walk)
whiskers.add_task(feeding)
buddy.add_task(vet_checkup)

# Use Scheduler to print today's schedule
scheduler = Scheduler(owner)

print("===== Today's Schedule =====")
for task in scheduler.get_all_tasks():
    pet_name = next(p.name for p in owner.get_pets() if p.id == task.pet_id)
    status = "Done" if task.is_complete else "Pending"
    time_str = task.time.strftime("%I:%M %p") if task.time else "No time set"
    freq_str = f"({task.frequency})" if task.frequency else ""
    print(f"{time_str} | {pet_name} | {task.title} {freq_str} | {status}")

print("============================")
print(f"Incomplete tasks: {len(scheduler.get_incomplete_tasks())}")
