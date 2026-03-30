import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet


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
