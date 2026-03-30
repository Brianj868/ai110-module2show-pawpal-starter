# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

A user should be able to add a pet. add tasks and consider time constraints (scheduling).

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

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


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

    Basically, just added back references so that instead of the relationship just being one way, it goes both ways. For example, if a pet is deleted, it will delete the tasks associated with it as well instead of leaving them.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

    ribute (datetime) and the scheduler can sort by it, retrieve tasks at a specific time, and detect exact-time conflicts via get_conflicts().

Frequency/Recurrence — tasks have a frequency attribute ("daily", "weekly", or None). When a recurring task is completed, the scheduler automatically generates the next occurrence using timedelta.

Completion status — filter_tasks(is_complete=) lets you separate pending from done tasks, which is the basis for building an actionable schedule.

I wanted the complexity to be simple for now with the option to alwasys add more later.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler only flags a conflict when two tasks share the exact same datetime. It has no concept of task duration, so a 30-minute walk starting at 8:00 AM and a task starting at 8:15 AM would not be flagged as a conflict — even though they clearly overlap in real life.

This was a deliberate simplification. To detect overlapping durations you'd need each task to have both a start_time and an end_time (or a duration), and the conflict check would need to test whether any two time ranges intersect rather than just comparing timestamps. That's more accurate but adds complexity to both the data model and the scheduling logic.

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
