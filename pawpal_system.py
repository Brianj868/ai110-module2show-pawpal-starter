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
