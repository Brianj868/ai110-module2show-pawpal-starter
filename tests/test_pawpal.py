import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    task = Task(id="t1", title="Walk", description="Morning walk", pet_id="p1")
    assert task.is_complete == False
    task.mark_complete()
    assert task.is_complete == True


def test_add_task_increases_pet_task_count():
    pet = Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", owner_id="o1")
    task = Task(id="t1", title="Walk", description="Morning walk", pet_id="p1")
    assert len(pet.get_tasks()) == 0
    pet.add_task(task)
    assert len(pet.get_tasks()) == 1


def test_daily_task_creates_next_occurrence():
    owner = Owner(id="o1", name="Alex", email="")
    pet = Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", owner_id="o1")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    task = Task(id="t1", title="Walk", description="Morning walk", pet_id="p1",
                time=datetime(2026, 3, 29, 8, 0), frequency="daily")
    pet.add_task(task)

    scheduler.complete_task(task)

    tasks = pet.get_tasks()
    assert len(tasks) == 2
    assert tasks[1].time == datetime(2026, 3, 29, 8, 0) + timedelta(days=1)


def test_one_time_task_does_not_create_next_occurrence():
    owner = Owner(id="o1", name="Alex", email="")
    pet = Pet(id="p1", name="Buddy", species="Dog", breed="Labrador", owner_id="o1")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)

    task = Task(id="t1", title="Vet Visit", description="Checkup", pet_id="p1",
                time=datetime(2026, 3, 29, 14, 0), frequency=None)
    pet.add_task(task)

    scheduler.complete_task(task)

    assert len(pet.get_tasks()) == 1
