import streamlit as st
from datetime import datetime, date
from pawpal_system import Owner, Pet, Task, Scheduler
from agent import run_agent

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Initialize session state once ---
if "owner" not in st.session_state:
    owner = Owner(id="o1", name="Jordan", email="")
    st.session_state.owner = owner
    st.session_state.scheduler = Scheduler(owner)
    st.session_state.task_counter = 0
    st.session_state.pet_counter = 0

owner = st.session_state.owner
scheduler = st.session_state.scheduler

# --- Owner input ---
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Pet Management ---
st.subheader("Pets")

col1, col2, col3 = st.columns(3)
with col1:
    new_pet_name = st.text_input("Pet name")
with col2:
    species_options = ["dog", "cat", "other"]
    new_species = st.selectbox("Species", species_options)
with col3:
    new_breed = st.text_input("Breed (optional)")

if st.button("Add pet", use_container_width=True):
    if new_pet_name.strip():
        st.session_state.pet_counter += 1
        pet = Pet(
            id=f"p{st.session_state.pet_counter}",
            name=new_pet_name.strip(),
            species=new_species,
            breed=new_breed.strip(),
            owner_id=owner.id
        )
        owner.add_pet(pet)
        st.rerun()

pets = owner.get_pets()
if pets:
    for p in pets:
        st.markdown(f"- **{p.name}** ({p.species}{'— ' + p.breed if p.breed else ''})")
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Add Task ---
st.subheader("Add a Task")

if not pets:
    st.warning("Add a pet first before creating tasks.")
else:
    pet_names = [p.name for p in pets]
    col1, col2 = st.columns(2)
    with col1:
        task_title = st.text_input("Task title", value="Morning walk")
    with col2:
        task_description = st.text_input("Description", value="")

    col1, col2, col3 = st.columns(3)
    with col1:
        selected_pet_name = st.selectbox("Assign to pet", pet_names)
    with col2:
        task_time = st.time_input("Scheduled time", value=None)
    with col3:
        frequency_choice = st.selectbox("Frequency", ["none", "daily", "weekly"])

    if st.button("Add task", use_container_width=True):
        st.session_state.task_counter += 1
        selected_pet = next(p for p in pets if p.name == selected_pet_name)
        scheduled_dt = datetime.combine(date.today(), task_time) if task_time else None
        task = Task(
            id=f"t{st.session_state.task_counter}",
            title=task_title,
            description=task_description,
            pet_id=selected_pet.id,
            time=scheduled_dt,
            frequency=frequency_choice if frequency_choice != "none" else None
        )
        selected_pet.add_task(task)
        st.rerun()

st.divider()

# --- Current Tasks ---
st.subheader("Current Tasks")
all_tasks = scheduler.get_all_tasks()
pet_lookup = {p.id: p.name for p in pets}

if not all_tasks:
    st.info("No tasks yet.")
else:
    for warning in scheduler.get_conflicts():
        st.warning(warning)

    sorted_tasks = sorted(all_tasks, key=lambda t: (t.time is None, t.time))
    st.table([{
        "Pet": pet_lookup.get(t.pet_id, "Unknown"),
        "Title": t.title,
        "Description": t.description,
        "Time": t.time.strftime("%I:%M %p") if t.time else "—",
        "Frequency": t.frequency or "one-time",
        "Status": "Done" if t.is_complete else "Pending"
    } for t in sorted_tasks])

    col1, col2 = st.columns(2)
    col1.metric("Pending", len(scheduler.get_incomplete_tasks()))
    col2.metric("Completed", len(scheduler.filter_tasks(is_complete=True)))

    st.divider()

    # --- Mark task complete / incomplete ---
    st.subheader("Update Task Status")
    task_labels = [f"{pet_lookup.get(t.pet_id, '?')} — {t.title}" for t in all_tasks]
    selected_label = st.selectbox("Select task", task_labels)
    selected_task = all_tasks[task_labels.index(selected_label)]

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Mark complete", use_container_width=True):
            scheduler.complete_task(selected_task)
            st.rerun()
    with col2:
        if st.button("Mark incomplete", use_container_width=True):
            selected_task.mark_incomplete()
            st.rerun()

    st.divider()

    # --- Remove Task ---
    st.subheader("Remove a Task")
    remove_label = st.selectbox("Select task to remove", task_labels, key="remove_select")
    remove_task = all_tasks[task_labels.index(remove_label)]
    if st.button("Remove task", use_container_width=True):
        pet_obj = next((p for p in pets if p.id == remove_task.pet_id), None)
        if pet_obj:
            pet_obj.remove_task(remove_task.id)
        st.rerun()

st.divider()

# --- Generate Schedule ---
st.subheader("Today's Schedule")

if st.button("Generate schedule", use_container_width=True):
    incomplete = scheduler.get_incomplete_tasks()
    if not incomplete:
        st.info("All tasks are complete — nothing left to schedule.")
    else:
        st.success(f"Full schedule for {owner.name}")
        for i, task in enumerate(scheduler.sort_by_time(), 1):
            if not task.is_complete:
                time_str = task.time.strftime("%I:%M %p") if task.time else "No time set"
                freq_str = f"({task.frequency})" if task.frequency else ""
                pet_name = pet_lookup.get(task.pet_id, "Unknown")
                st.markdown(f"**{i}. {task.title}** — {pet_name} | {time_str} {freq_str}")

        for warning in scheduler.get_conflicts():
            st.warning(warning)

if st.button("Clear all tasks", use_container_width=True):
    for p in pets:
        p.tasks = []
    st.session_state.task_counter = 0
    st.rerun()

st.divider()

# --- AI Planner ---
st.subheader("AI Planner")
st.caption("Describe a goal and the AI will plan, act, and check its own work.")

if not pets:
    st.warning("Add at least one pet before using the AI Planner.")
else:
    goal = st.text_area(
        "What should the AI do?",
        placeholder="e.g. Plan a full day of care for Buddy. Add morning, afternoon, and evening tasks.",
        height=80
    )

    if st.button("Run AI Planner", use_container_width=True):
        if not goal.strip():
            st.warning("Enter a goal first.")
        else:
            with st.spinner("AI is planning, acting, and checking..."):
                if "task_counter" not in st.session_state:
                    st.session_state.task_counter = 0
                counter = [st.session_state.task_counter]
                log = run_agent(goal, owner, scheduler, counter)
                st.session_state.task_counter = counter[0]

            # Show agent reasoning and actions
            for role, text in log:
                if role == "assistant":
                    st.markdown(text)
                elif role == "tool":
                    with st.expander("Tool call", expanded=False):
                        st.code(text, language="text")

            st.success("AI finished. Schedule updated above.")
            st.rerun()
