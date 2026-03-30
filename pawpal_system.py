from datetime import timedelta


class Task:
    def __init__(self, id, title, description, pet_id, time=None, frequency=None):
        self.id = id
        self.title = title
        self.description = description
        self.pet_id = pet_id
        self.time = time          # datetime of when the task occurs
        self.frequency = frequency  # e.g. "daily", "weekly", None
        self.is_complete = False

    def mark_complete(self):
        """Mark this task as complete."""
        self.is_complete = True

    def mark_incomplete(self):
        """Mark this task as incomplete."""
        self.is_complete = False


class Pet:
    def __init__(self, id, name, species, breed, owner_id):
        self.id = id
        self.name = name
        self.species = species
        self.breed = breed
        self.owner_id = owner_id
        self.tasks = []

    def add_task(self, task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_id):
        """Remove a task from this pet's task list by id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self):
        """Return all tasks assigned to this pet."""
        return self.tasks


class Owner:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.pets = []

    def add_pet(self, pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_id):
        """Remove a pet and clear its tasks to prevent orphaned data."""
        pet = next((p for p in self.pets if p.id == pet_id), None)
        if pet:
            pet.tasks = []
        self.pets = [p for p in self.pets if p.id != pet_id]

    def get_pets(self):
        """Return all pets belonging to this owner."""
        return self.pets

    def get_all_tasks(self):
        """Return a flat list of all tasks across all pets."""
        tasks = []
        for pet in self.pets:
            tasks.extend(pet.get_tasks())
        return tasks


class Scheduler:
    def __init__(self, owner):
        self.owner = owner

    def get_all_tasks(self):
        """Return all tasks across every pet owned by this owner."""
        return self.owner.get_all_tasks()

    def get_tasks_by_pet(self, pet_id):
        """Return all tasks for a specific pet by id."""
        for pet in self.owner.get_pets():
            if pet.id == pet_id:
                return pet.get_tasks()
        return []

    def get_incomplete_tasks(self):
        """Return all tasks that have not yet been marked complete."""
        return [t for t in self.get_all_tasks() if not t.is_complete]

    def get_tasks_at_time(self, time):
        """Return all tasks scheduled at the given time."""
        return [t for t in self.get_all_tasks() if t.time == time]

    def is_time_conflicting(self, time):
        """Return True if any existing task is already scheduled at the given time."""
        return any(t.time == time for t in self.get_all_tasks())

    def sort_by_time(self):
        """Return all tasks sorted by their time attribute, earliest first."""
        return sorted(self.get_all_tasks(), key=lambda t: t.time)

    def filter_tasks(self, is_complete=None, pet_name=None):
        """Return tasks filtered by completion status and/or pet name."""
        tasks = self.get_all_tasks()
        if is_complete is not None:
            tasks = [t for t in tasks if t.is_complete == is_complete]
        if pet_name is not None:
            pets_by_name = {p.name: p.id for p in self.owner.get_pets()}
            pet_id = pets_by_name.get(pet_name)
            tasks = [t for t in tasks if t.pet_id == pet_id]
        return tasks

    def get_conflicts(self):
        """Return a list of warning messages for any tasks scheduled at the same time."""
        tasks = [t for t in self.get_all_tasks() if t.time is not None]
        pet_names = {p.id: p.name for p in self.owner.get_pets()}
        warnings = []

        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].time == tasks[j].time:
                    name_a = pet_names.get(tasks[i].pet_id, tasks[i].pet_id)
                    name_b = pet_names.get(tasks[j].pet_id, tasks[j].pet_id)
                    time_str = tasks[i].time.strftime("%I:%M %p")
                    warnings.append(
                        f"WARNING: '{tasks[i].title}' ({name_a}) and "
                        f"'{tasks[j].title}' ({name_b}) are both scheduled at {time_str}."
                    )

        return warnings

    def complete_task(self, task):
        """Mark a task complete and schedule the next occurrence if it repeats."""
        task.mark_complete()

        if task.frequency not in ("daily", "weekly") or task.time is None:
            return

        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_time = task.time + delta

        next_task = Task(
            id=f"{task.id}_next",
            title=task.title,
            description=task.description,
            pet_id=task.pet_id,
            time=next_time,
            frequency=task.frequency
        )

        pet = next((p for p in self.owner.get_pets() if p.id == task.pet_id), None)
        if pet:
            pet.add_task(next_task)
