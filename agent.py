import os
import json
from datetime import datetime, date
from dotenv import load_dotenv
from groq import Groq
from pawpal_system import Task

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_state",
            "description": "Returns a summary of all pets and their tasks, including time, frequency, and completion status.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Adds a new task to a specific pet.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pet_name": {"type": "string", "description": "Name of the pet to assign the task to."},
                    "title": {"type": "string", "description": "Short title for the task."},
                    "description": {"type": "string", "description": "Details about the task."},
                    "time_str": {"type": "string", "description": "Scheduled time in HH:MM 24-hour format, e.g. '08:00'. Leave empty if no specific time."},
                    "frequency": {"type": "string", "enum": ["none", "daily", "weekly"], "description": "How often the task repeats."}
                },
                "required": ["pet_name", "title", "description", "frequency"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_complete",
            "description": "Marks a task complete for a pet. Recurring tasks automatically schedule the next occurrence.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pet_name": {"type": "string"},
                    "task_title": {"type": "string"}
                },
                "required": ["pet_name", "task_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_task",
            "description": "Removes a task from a pet's task list.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pet_name": {"type": "string"},
                    "task_title": {"type": "string"}
                },
                "required": ["pet_name", "task_title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_conflicts",
            "description": "Checks the schedule for time conflicts across all pets. Always call this after making changes.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_incomplete_tasks",
            "description": "Returns all tasks not yet marked complete.",
            "parameters": {"type": "object", "properties": {}, "required": []}
        }
    }
]


def run_tool(name, inputs, owner, scheduler, task_counter):
    """Execute a tool call against the live pawpal_system objects."""
    pets = owner.get_pets()
    pet_lookup = {p.name: p for p in pets}

    if name == "get_current_state":
        if not pets:
            return "No pets registered yet."
        lines = []
        for pet in pets:
            lines.append(f"Pet: {pet.name} ({pet.species})")
            tasks = pet.get_tasks()
            if not tasks:
                lines.append("  No tasks.")
            for t in tasks:
                time_str = t.time.strftime("%I:%M %p") if t.time else "no time"
                status = "Done" if t.is_complete else "Pending"
                freq = t.frequency or "one-time"
                lines.append(f"  - [{status}] {t.title} | {time_str} | {freq} | {t.description}")
        return "\n".join(lines)

    elif name == "add_task":
        pet = pet_lookup.get(inputs["pet_name"])
        if not pet:
            return f"Pet '{inputs['pet_name']}' not found."
        task_counter[0] += 1
        time_str = inputs.get("time_str", "").strip()
        scheduled_dt = None
        if time_str:
            try:
                t = datetime.strptime(time_str, "%H:%M").time()
                scheduled_dt = datetime.combine(date.today(), t)
            except ValueError:
                return f"Invalid time format '{time_str}'. Use HH:MM."
        freq = inputs["frequency"]
        task = Task(
            id=f"ai_t{task_counter[0]}",
            title=inputs["title"],
            description=inputs["description"],
            pet_id=pet.id,
            time=scheduled_dt,
            frequency=freq if freq != "none" else None
        )
        pet.add_task(task)
        return f"Added task '{inputs['title']}' to {inputs['pet_name']}."

    elif name == "mark_task_complete":
        pet = pet_lookup.get(inputs["pet_name"])
        if not pet:
            return f"Pet '{inputs['pet_name']}' not found."
        task = next((t for t in pet.get_tasks() if t.title == inputs["task_title"]), None)
        if not task:
            return f"Task '{inputs['task_title']}' not found for {inputs['pet_name']}."
        scheduler.complete_task(task)
        return f"Marked '{inputs['task_title']}' complete for {inputs['pet_name']}."

    elif name == "remove_task":
        pet = pet_lookup.get(inputs["pet_name"])
        if not pet:
            return f"Pet '{inputs['pet_name']}' not found."
        task = next((t for t in pet.get_tasks() if t.title == inputs["task_title"]), None)
        if not task:
            return f"Task '{inputs['task_title']}' not found for {inputs['pet_name']}."
        pet.remove_task(task.id)
        return f"Removed '{inputs['task_title']}' from {inputs['pet_name']}."

    elif name == "check_conflicts":
        warnings = scheduler.get_conflicts()
        return "\n".join(warnings) if warnings else "No scheduling conflicts found."

    elif name == "get_incomplete_tasks":
        tasks = scheduler.get_incomplete_tasks()
        if not tasks:
            return "All tasks are complete."
        pet_id_lookup = {p.id: p.name for p in pets}
        lines = [
            f"- {t.title} ({pet_id_lookup.get(t.pet_id, '?')}) | "
            f"{t.time.strftime('%I:%M %p') if t.time else 'no time'}"
            for t in tasks
        ]
        return "\n".join(lines)

    return f"Unknown tool: {name}"


def run_agent(goal, owner, scheduler, task_counter):
    """
    Agentic loop: Plan -> Act -> Check.
    Returns a list of (role, text) tuples for display.
    """
    state_summary = run_tool("get_current_state", {}, owner, scheduler, task_counter)

    messages = [
        {
            "role": "system",
            "content": (
                "You are PawPal AI, a pet care planning assistant. "
                "You help owners schedule and manage care tasks for their pets.\n\n"
                "Operate in three phases:\n"
                "1. PLAN: Reason about the current state and the user's goal.\n"
                "2. ACT: Call tools to create, update, or remove tasks.\n"
                "3. CHECK: Always call check_conflicts after making changes, "
                "then call get_incomplete_tasks to summarize what's left.\n\n"
                "Be concise. Only add tasks that make sense for the pet's species."
            )
        },
        {
            "role": "user",
            "content": f"Current state:\n{state_summary}\n\nGoal: {goal}"
        }
    ]

    action_log = []

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=1024
        )

        message = response.choices[0].message

        if message.content:
            action_log.append(("assistant", message.content))

        # No tool calls — agent is done
        if not message.tool_calls:
            break

        # Execute each tool call
        messages.append({"role": "assistant", "content": message.content, "tool_calls": message.tool_calls})

        for call in message.tool_calls:
            inputs = json.loads(call.function.arguments)
            result = run_tool(call.function.name, inputs, owner, scheduler, task_counter)
            action_log.append(("tool", f"{call.function.name}({call.function.arguments}) → {result}"))
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result
            })

    return action_log
