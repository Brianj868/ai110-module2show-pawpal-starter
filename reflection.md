# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

A user should be able to add a pet. add tasks and consider time constraints (scheduling).

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

<<<<<<< HEAD
<<<<<<< HEAD
=======
    A user should be able to add a pet. add tasks and consider time constraints (scheduling).
=======
    Owner
Represents the person who uses the app. Owns one or more pets and serves as the top of the hierarchy — everything in the system traces back to an owner.

Pet
Represents an individual animal belonging to an owner. Holds the pet's identifying details and acts as the container for all tasks associated with that pet.

Task
Represents a single thing that needs to be done for a pet — feeding, grooming, a vet visit, etc. Tracks whether it's been completed and can optionally be linked to a schedule if it needs to happen at a specific time.

Schedule
Represents the time constraints for a task. Stores when a task starts, when it ends, and whether it repeats. Can check if it conflicts with another scheduled task to prevent double-booking.
>>>>>>> 2db1f27 (Add PawPal system: Owner, Pet, Task, Scheduler classes with tests)

>>>>>>> 89cfc7f (chore: add class skeletons from UML)
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

    Basically, just added back references so that instead of the relationship just being one way, it goes both ways. For example, if a pet is deleted, it will delete the tasks associated with it as well instead of leaving them.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
