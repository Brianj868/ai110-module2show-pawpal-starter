import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Helpers ──────────────────────────────────────────────────────────────────

def make_owner():
    return Owner(id="o1", name="Alex", email="alex@email.com")

def make_pet(owner, pet_id="p1", name="Buddy"):
    pet = Pet(id=pet_id, name=name, species="Dog", breed="Lab", owner_id=owner.id)
    owner.add_pet(pet)
    return pet

def make_task(pet_id="p1", task_id="t1", title="Walk",
              time=None, frequency=None):
    return Task(id=task_id, title=title, description="desc",
                pet_id=pet_id, time=time, frequency=frequency)


# ── Task ─────────────────────────────────────────────────────────────────────

class TestTask:
    def test_defaults(self):
        task = make_task()
        assert task.is_complete is False
        assert task.time is None
        assert task.frequency is None

    def test_mark_complete(self):
        task = make_task()
        task.mark_complete()
        assert task.is_complete is True

    def test_mark_incomplete(self):
        task = make_task()
        task.mark_complete()
        task.mark_incomplete()
        assert task.is_complete is False

    def test_mark_complete_idempotent(self):
        task = make_task()
        task.mark_complete()
        task.mark_complete()
        assert task.is_complete is True


# ── Pet ───────────────────────────────────────────────────────────────────────

class TestPet:
    def test_starts_with_no_tasks(self):
        owner = make_owner()
        pet = make_pet(owner)
        assert pet.get_tasks() == []

    def test_add_task_increases_count(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task())
        assert len(pet.get_tasks()) == 1

    def test_add_multiple_tasks(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1"))
        pet.add_task(make_task(task_id="t2"))
        assert len(pet.get_tasks()) == 2

    def test_remove_task(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = make_task(task_id="t1")
        pet.add_task(task)
        pet.remove_task("t1")
        assert len(pet.get_tasks()) == 0

    def test_remove_task_nonexistent_id(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1"))
        pet.remove_task("does_not_exist")
        assert len(pet.get_tasks()) == 1

    def test_remove_only_matching_task(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1"))
        pet.add_task(make_task(task_id="t2"))
        pet.remove_task("t1")
        assert pet.get_tasks()[0].id == "t2"

    def test_get_tasks_returns_list(self):
        owner = make_owner()
        pet = make_pet(owner)
        assert isinstance(pet.get_tasks(), list)


# ── Owner ─────────────────────────────────────────────────────────────────────

class TestOwner:
    def test_starts_with_no_pets(self):
        owner = make_owner()
        assert owner.get_pets() == []

    def test_add_pet(self):
        owner = make_owner()
        make_pet(owner)
        assert len(owner.get_pets()) == 1

    def test_add_multiple_pets(self):
        owner = make_owner()
        make_pet(owner, pet_id="p1")
        make_pet(owner, pet_id="p2", name="Whiskers")
        assert len(owner.get_pets()) == 2

    def test_remove_pet(self):
        owner = make_owner()
        make_pet(owner, pet_id="p1")
        owner.remove_pet("p1")
        assert len(owner.get_pets()) == 0

    def test_remove_pet_clears_its_tasks(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task())
        owner.remove_pet("p1")
        assert pet.tasks == []

    def test_remove_pet_nonexistent_id(self):
        owner = make_owner()
        make_pet(owner, pet_id="p1")
        owner.remove_pet("does_not_exist")
        assert len(owner.get_pets()) == 1

    def test_get_all_tasks_empty(self):
        owner = make_owner()
        make_pet(owner)
        assert owner.get_all_tasks() == []

    def test_get_all_tasks_single_pet(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1"))
        pet.add_task(make_task(task_id="t2"))
        assert len(owner.get_all_tasks()) == 2

    def test_get_all_tasks_multiple_pets(self):
        owner = make_owner()
        p1 = make_pet(owner, pet_id="p1")
        p2 = make_pet(owner, pet_id="p2", name="Whiskers")
        p1.add_task(make_task(pet_id="p1", task_id="t1"))
        p2.add_task(make_task(pet_id="p2", task_id="t2"))
        assert len(owner.get_all_tasks()) == 2

    def test_get_all_tasks_no_pets(self):
        owner = make_owner()
        assert owner.get_all_tasks() == []


# ── Scheduler ─────────────────────────────────────────────────────────────────

class TestSchedulerBasics:
    def test_get_all_tasks_delegates_to_owner(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task())
        scheduler = Scheduler(owner)
        assert len(scheduler.get_all_tasks()) == 1

    def test_get_tasks_by_pet_found(self):
        owner = make_owner()
        pet = make_pet(owner, pet_id="p1")
        pet.add_task(make_task(pet_id="p1"))
        scheduler = Scheduler(owner)
        assert len(scheduler.get_tasks_by_pet("p1")) == 1

    def test_get_tasks_by_pet_not_found(self):
        owner = make_owner()
        make_pet(owner)
        scheduler = Scheduler(owner)
        assert scheduler.get_tasks_by_pet("nonexistent") == []

    def test_get_incomplete_tasks(self):
        owner = make_owner()
        pet = make_pet(owner)
        t1 = make_task(task_id="t1")
        t2 = make_task(task_id="t2")
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler = Scheduler(owner)
        incomplete = scheduler.get_incomplete_tasks()
        assert len(incomplete) == 1
        assert incomplete[0].id == "t2"

    def test_get_incomplete_tasks_all_complete(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = make_task()
        t.mark_complete()
        pet.add_task(t)
        scheduler = Scheduler(owner)
        assert scheduler.get_incomplete_tasks() == []

    def test_get_tasks_at_time(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        pet.add_task(make_task(task_id="t1", time=t))
        pet.add_task(make_task(task_id="t2", time=datetime(2026, 3, 29, 9, 0)))
        scheduler = Scheduler(owner)
        assert len(scheduler.get_tasks_at_time(t)) == 1

    def test_get_tasks_at_time_no_match(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(time=datetime(2026, 3, 29, 8, 0)))
        scheduler = Scheduler(owner)
        assert scheduler.get_tasks_at_time(datetime(2026, 3, 29, 10, 0)) == []

    def test_is_time_conflicting_true(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        pet.add_task(make_task(time=t))
        scheduler = Scheduler(owner)
        assert scheduler.is_time_conflicting(t) is True

    def test_is_time_conflicting_false(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(time=datetime(2026, 3, 29, 8, 0)))
        scheduler = Scheduler(owner)
        assert scheduler.is_time_conflicting(datetime(2026, 3, 29, 10, 0)) is False


class TestSchedulerSortAndFilter:
    def test_sort_by_time_orders_correctly(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1", time=datetime(2026, 3, 29, 14, 0)))
        pet.add_task(make_task(task_id="t2", time=datetime(2026, 3, 29, 8, 0)))
        pet.add_task(make_task(task_id="t3", time=datetime(2026, 3, 29, 9, 0)))
        scheduler = Scheduler(owner)
        sorted_tasks = scheduler.sort_by_time()
        times = [t.time for t in sorted_tasks]
        assert times == sorted(times)

    def test_sort_by_time_single_task(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        pet.add_task(make_task(time=t))
        scheduler = Scheduler(owner)
        assert scheduler.sort_by_time()[0].time == t

    def test_filter_by_complete_true(self):
        owner = make_owner()
        pet = make_pet(owner)
        t1 = make_task(task_id="t1")
        t2 = make_task(task_id="t2")
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler = Scheduler(owner)
        result = scheduler.filter_tasks(is_complete=True)
        assert len(result) == 1 and result[0].id == "t1"

    def test_filter_by_complete_false(self):
        owner = make_owner()
        pet = make_pet(owner)
        t1 = make_task(task_id="t1")
        t2 = make_task(task_id="t2")
        t1.mark_complete()
        pet.add_task(t1)
        pet.add_task(t2)
        scheduler = Scheduler(owner)
        result = scheduler.filter_tasks(is_complete=False)
        assert len(result) == 1 and result[0].id == "t2"

    def test_filter_by_pet_name(self):
        owner = make_owner()
        p1 = make_pet(owner, pet_id="p1", name="Buddy")
        p2 = make_pet(owner, pet_id="p2", name="Whiskers")
        p1.add_task(make_task(pet_id="p1", task_id="t1"))
        p2.add_task(make_task(pet_id="p2", task_id="t2"))
        scheduler = Scheduler(owner)
        result = scheduler.filter_tasks(pet_name="Buddy")
        assert len(result) == 1 and result[0].id == "t1"

    def test_filter_by_pet_name_not_found(self):
        owner = make_owner()
        pet = make_pet(owner, name="Buddy")
        pet.add_task(make_task())
        scheduler = Scheduler(owner)
        assert scheduler.filter_tasks(pet_name="Ghost") == []

    def test_filter_both_complete_and_pet_name(self):
        owner = make_owner()
        p1 = make_pet(owner, pet_id="p1", name="Buddy")
        t1 = make_task(pet_id="p1", task_id="t1")
        t2 = make_task(pet_id="p1", task_id="t2")
        t1.mark_complete()
        p1.add_task(t1)
        p1.add_task(t2)
        scheduler = Scheduler(owner)
        result = scheduler.filter_tasks(is_complete=True, pet_name="Buddy")
        assert len(result) == 1 and result[0].id == "t1"

    def test_filter_no_filters_returns_all(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1"))
        pet.add_task(make_task(task_id="t2"))
        scheduler = Scheduler(owner)
        assert len(scheduler.filter_tasks()) == 2


class TestSchedulerConflicts:
    def test_no_conflicts(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1", time=datetime(2026, 3, 29, 8, 0)))
        pet.add_task(make_task(task_id="t2", time=datetime(2026, 3, 29, 9, 0)))
        scheduler = Scheduler(owner)
        assert scheduler.get_conflicts() == []

    def test_conflict_same_pet(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        pet.add_task(make_task(task_id="t1", title="Walk", time=t))
        pet.add_task(make_task(task_id="t2", title="Feed", time=t))
        scheduler = Scheduler(owner)
        assert len(scheduler.get_conflicts()) == 1

    def test_conflict_different_pets(self):
        owner = make_owner()
        p1 = make_pet(owner, pet_id="p1", name="Buddy")
        p2 = make_pet(owner, pet_id="p2", name="Whiskers")
        t = datetime(2026, 3, 29, 9, 0)
        p1.add_task(make_task(pet_id="p1", task_id="t1", title="Bath", time=t))
        p2.add_task(make_task(pet_id="p2", task_id="t2", title="Feed", time=t))
        scheduler = Scheduler(owner)
        conflicts = scheduler.get_conflicts()
        assert len(conflicts) == 1
        assert "Bath" in conflicts[0] and "Feed" in conflicts[0]

    def test_conflict_message_includes_time(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        pet.add_task(make_task(task_id="t1", title="Walk", time=t))
        pet.add_task(make_task(task_id="t2", title="Feed", time=t))
        scheduler = Scheduler(owner)
        assert "08:00 AM" in scheduler.get_conflicts()[0]

    def test_tasks_without_time_ignored_in_conflicts(self):
        owner = make_owner()
        pet = make_pet(owner)
        pet.add_task(make_task(task_id="t1", time=None))
        pet.add_task(make_task(task_id="t2", time=None))
        scheduler = Scheduler(owner)
        assert scheduler.get_conflicts() == []

    def test_three_way_conflict(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        pet.add_task(make_task(task_id="t1", title="A", time=t))
        pet.add_task(make_task(task_id="t2", title="B", time=t))
        pet.add_task(make_task(task_id="t3", title="C", time=t))
        scheduler = Scheduler(owner)
        # 3 tasks at same time = 3 pairs
        assert len(scheduler.get_conflicts()) == 3


class TestSchedulerCompleteTask:
    def test_complete_task_marks_done(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = make_task(time=datetime(2026, 3, 29, 8, 0), frequency="daily")
        pet.add_task(task)
        scheduler = Scheduler(owner)
        scheduler.complete_task(task)
        assert task.is_complete is True

    def test_daily_task_creates_next_occurrence(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        task = make_task(time=t, frequency="daily")
        pet.add_task(task)
        Scheduler(owner).complete_task(task)
        assert len(pet.get_tasks()) == 2
        assert pet.get_tasks()[1].time == t + timedelta(days=1)

    def test_weekly_task_creates_next_occurrence(self):
        owner = make_owner()
        pet = make_pet(owner)
        t = datetime(2026, 3, 29, 8, 0)
        task = make_task(time=t, frequency="weekly")
        pet.add_task(task)
        Scheduler(owner).complete_task(task)
        assert pet.get_tasks()[1].time == t + timedelta(weeks=1)

    def test_one_time_task_no_next_occurrence(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = make_task(time=datetime(2026, 3, 29, 8, 0), frequency=None)
        pet.add_task(task)
        Scheduler(owner).complete_task(task)
        assert len(pet.get_tasks()) == 1

    def test_recurring_task_without_time_no_next_occurrence(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = make_task(time=None, frequency="daily")
        pet.add_task(task)
        Scheduler(owner).complete_task(task)
        assert len(pet.get_tasks()) == 1

    def test_next_task_inherits_frequency(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = make_task(time=datetime(2026, 3, 29, 8, 0), frequency="daily")
        pet.add_task(task)
        Scheduler(owner).complete_task(task)
        assert pet.get_tasks()[1].frequency == "daily"

    def test_next_task_inherits_title_and_description(self):
        owner = make_owner()
        pet = make_pet(owner)
        task = Task(id="t1", title="Morning Walk", description="30 min",
                    pet_id="p1", time=datetime(2026, 3, 29, 8, 0), frequency="daily")
        pet.add_task(task)
        Scheduler(owner).complete_task(task)
        next_task = pet.get_tasks()[1]
        assert next_task.title == "Morning Walk"
        assert next_task.description == "30 min"

    def test_complete_task_pet_not_found(self):
        owner = make_owner()
        # task references a pet_id not in owner's pets
        task = Task(id="t1", title="Walk", description="desc",
                    pet_id="ghost", time=datetime(2026, 3, 29, 8, 0), frequency="daily")
        scheduler = Scheduler(owner)
        scheduler.complete_task(task)  # should not raise
        assert task.is_complete is True
