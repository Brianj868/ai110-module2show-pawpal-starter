class Owner:
    def __init__(self, id, name, email):
        self.id = id
        self.name = name
        self.email = email
        self.pets = []

    def add_pet(self, pet):
        pass

    def remove_pet(self, pet_id):
        pass

    def get_pets(self):
        pass


class Pet:
    def __init__(self, id, name, species, breed):
        self.id = id
        self.name = name
        self.species = species
        self.breed = breed
        self.tasks = []

    def add_task(self, task):
        pass

    def remove_task(self, task_id):
        pass

    def get_tasks(self):
        pass


class Task:
    def __init__(self, id, title, description):
        self.id = id
        self.title = title
        self.description = description
        self.is_complete = False
        self.schedule = None

    def mark_complete(self):
        pass

    def mark_incomplete(self):
        pass

    def assign_schedule(self, schedule):
        pass


class Schedule:
    def __init__(self, id, start_time, end_time, recurrence=None):
        self.id = id
        self.start_time = start_time
        self.end_time = end_time
        self.recurrence = recurrence

    def is_conflicting(self, other):
        pass
