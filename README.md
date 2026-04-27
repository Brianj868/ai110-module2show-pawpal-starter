# PawPal+ — AI-Powered Pet Care Scheduler

## Original Project

PawPal+ began in Modules 1–3 as a structured Python scheduling system. The original goal was to model the relationship between pet owners, their animals, and daily care tasks — giving owners a way to track what needed to happen, when, and for which pet. The system could sort tasks by time, detect scheduling conflicts, and automatically re-schedule recurring tasks when marked complete.

---

## Title and Summary

**PawPal+** is a Streamlit web app that helps pet owners plan and manage daily care tasks for multiple pets. It combines a hand-built scheduling engine with an AI planner (powered by Groq + LLaMA 3) that can read the current state of your schedule, reason about a goal in plain English, take action by calling tools, and check its own work for conflicts before finishing.

**Why it matters:** Pet care is repetitive, time-sensitive, and easy to forget. PawPal+ removes the cognitive load by handling scheduling logic automatically — and when you're not sure what to add, the AI planner can build a full care plan from a single sentence.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                     app.py (UI)                     │
│              Streamlit frontend layer               │
└────────────────────────┬────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
┌─────────▼──────────┐       ┌──────────▼─────────┐
│  pawpal_system.py  │       │     agent.py        │
│  Owner             │       │  Groq API client    │
│  Pet               │◄──────│  LLaMA 3.3 70B      │
│  Task              │       │  Tool-use loop      │
│  Scheduler         │       │  Plan → Act → Check │
└────────────────────┘       └────────────────────┘
```

**`pawpal_system.py`** — the core domain model. Four classes (`Owner`, `Pet`, `Task`, `Scheduler`) handle all scheduling logic: sorting, filtering, conflict detection, and recurring task generation.

**`agent.py`** — the agentic layer. Wraps the scheduling system in a tool-use loop. The AI receives the current state, calls tools that directly mutate the live objects, then checks its own work before returning a summary.

**`app.py`** — the Streamlit UI. Connects the domain model and agent to a web interface with interactive forms, a live task table, status metrics, and the AI Planner input.

---

## Setup Instructions

### 1. Clone and enter the project

```bash
git clone https://github.com/Brianj868/ai110-module2show-pawpal-starter
cd ai110-module2show-pawpal-starter-main
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate       # Mac/Linux
.venv\Scripts\activate          # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key

Create a `.env` file in the project root (it is already in `.gitignore`):

```
GROQ_API_KEY=your_key_here
```

Get a free key at [console.groq.com](https://console.groq.com) — no credit card required.

### 5. Run the app

```bash
streamlit run app.py
```

### 6. Run the tests

```bash
python -m pytest tests/test_pawpal.py -v
```

---

## Sample Interactions

### 1. AI builds a full day plan from scratch

**Input (AI Planner):**
> Plan a full day of care for my dog Buddy. Include morning, afternoon, and evening tasks.

**AI output:**
```
Planning a full day of care for Buddy...

Added task 'Morning Walk' to Buddy.
Added task 'Breakfast Feeding' to Buddy.
Added task 'Afternoon Playtime' to Buddy.
Added task 'Evening Walk' to Buddy.
Added task 'Dinner Feeding' to Buddy.
Added task 'Bedtime Check' to Buddy.

No scheduling conflicts found.
Buddy has 6 pending tasks scheduled throughout the day.
```

---

### 2. AI detects and resolves a conflict

**Input (AI Planner):**
> Add a vet appointment for Whiskers at 9am and a grooming session also at 9am.

**AI output:**
```
Added task 'Vet Appointment' to Whiskers at 09:00 AM.
Added task 'Grooming Session' to Whiskers at 09:00 AM.

WARNING: 'Vet Appointment' (Whiskers) and 'Grooming Session' (Whiskers)
are both scheduled at 09:00 AM.

I've detected a conflict — both tasks are set for the same time.
You may want to reschedule one of them.
```

---

### 3. AI handles recurring tasks

**Input (AI Planner):**
> Set up daily feeding for both Buddy and Whiskers at 8am and 6pm.

**AI output:**
```
Added task 'Morning Feeding' to Buddy at 08:00 AM (daily).
Added task 'Evening Feeding' to Buddy at 06:00 PM (daily).
Added task 'Morning Feeding' to Whiskers at 08:00 AM (daily).
Added task 'Evening Feeding' to Whiskers at 06:00 PM (daily).

No scheduling conflicts found.
4 recurring tasks created. Each will auto-schedule the next occurrence
when marked complete.
```

---

## Design Decisions

**Why a custom scheduling engine instead of a library?**
The goal was to learn object-oriented design by building it from scratch. Using a library like `apscheduler` would have hidden the logic we were meant to implement.

**Why Groq + LLaMA 3 instead of OpenAI or Anthropic?**
Groq offers a genuinely free tier with no credit card, which makes it accessible for a course project. LLaMA 3.3 70B has strong tool-use support, which is required for the agentic loop.

**Why tool use over a prompt-only approach?**
A prompt-only agent can only describe what should happen — it can't actually change the schedule. Tool use lets the AI directly call `pet.add_task()` and `scheduler.complete_task()` against the live objects, so the schedule is mutated in real time.

**Trade-off — exact time conflict detection:**
`get_conflicts()` only flags tasks with the exact same `datetime`. It does not detect overlapping windows (e.g., a 30-minute task at 8:00 AM and a task at 8:15 AM). This was a deliberate simplification — adding duration-aware overlap detection would require storing both start and end times on every task.

**Trade-off — single owner, single session:**
The app holds state in Streamlit's `session_state`, which resets on refresh. There is no database or persistence layer. This keeps the architecture simple but means data does not survive a page reload.

---

## Testing Summary

**52 tests across all four classes — all passing.**

| Area | Result |
|---|---|
| Task mark complete / incomplete | ✅ Works, including idempotent calls |
| Pet add / remove tasks | ✅ Works, including nonexistent IDs |
| Owner remove pet clears tasks | ✅ Prevents orphaned data |
| Scheduler sort by time | ✅ Handles out-of-order insertion |
| Scheduler filter by status + pet name | ✅ Both filters individually and combined |
| Conflict detection (same pet) | ✅ Correctly flags |
| Conflict detection (different pets) | ✅ Correctly flags |
| Three-way conflicts | ✅ Produces correct number of pairs |
| Tasks without a time | ✅ Safely ignored in conflict checks |
| Daily recurrence creates next task | ✅ Correct date using `timedelta` |
| Weekly recurrence creates next task | ✅ Correct date using `timedelta` |
| One-time task does not spawn follow-up | ✅ |
| Pet not found during complete_task | ✅ Does not crash |

**What didn't work initially:**
- The first version of `app.py` used `duration` and `priority` as dynamic attributes set outside the class, which caused the UI and the backend to drift. Fixing this required rebuilding the task form to map directly to `Task.__init__` parameters.
- The AI agent initially used the Anthropic SDK. Switching to Groq required rewriting the tool schema format (Anthropic uses `input_schema`, OpenAI/Groq uses `parameters`) and the message loop structure.

---

## Reflection

Building PawPal+ made three things concrete that were previously abstract:

**1. Design before code pays off.**
Starting with a UML diagram forced decisions about relationships (does `Task` belong to `Pet` or `Scheduler`?) before any code was written. Every time the diagram was skipped or rushed, the implementation had to be refactored.

**2. Agentic AI is about trust boundaries.**
The most interesting design question was not "what can the AI do?" but "what should it be allowed to do?" Giving the agent direct write access to the schedule (via tools) is powerful but requires the check phase — without `get_conflicts()` as a mandatory final step, the agent could silently create broken schedules.

**3. Tests are a specification, not an afterthought.**
Writing 52 tests after the implementation revealed several edge cases (orphaned tasks on pet removal, recurring tasks with no time set) that the code did not handle correctly. The tests forced the code to be correct, not just functional.
