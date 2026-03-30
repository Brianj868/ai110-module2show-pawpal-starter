import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Initialize session state once ---
if "owner" not in st.session_state:
    owner = Owner(id="o1", name="Jordan", email="")
    pet = Pet(id="p1", name="Mochi", species="dog", breed="", owner_id="o1")
    owner.add_pet(pet)
    st.session_state.owner = owner
    st.session_state.scheduler = Scheduler(owner)
    st.session_state.task_counter = 0

owner = st.session_state.owner
pet = owner.get_pets()[0]
scheduler = st.session_state.scheduler

# --- Owner & Pet inputs ---
owner_name = st.text_input("Owner name", value=owner.name)
owner.name = owner_name

pet_name = st.text_input("Pet name", value=pet.name)
pet.name = pet_name

species_options = ["dog", "cat", "other"]
species = st.selectbox("Species", species_options,
    index=species_options.index(pet.species) if pet.species in species_options else 0)
pet.species = species

# --- Task inputs ---
st.markdown("### Tasks")
col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.task_counter += 1
    task = Task(
        id=f"t{st.session_state.task_counter}",
        title=task_title,
        description=f"{duration} min | {priority} priority",
        pet_id=pet.id
    )
    task.duration_minutes = duration
    task.priority = priority
    pet.add_task(task)

all_tasks = scheduler.get_all_tasks()
if all_tasks:
    st.write("Current tasks:")
    st.table([{
        "Title": t.title,
        "Duration (min)": t.duration_minutes,
        "Priority": t.priority,
        "Status": "Done" if t.is_complete else "Pending"
    } for t in all_tasks])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule ---
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    incomplete = scheduler.get_incomplete_tasks()
    if not incomplete:
        st.info("No pending tasks to schedule.")
    else:
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_tasks = sorted(incomplete, key=lambda t: priority_order.get(t.priority, 1))
        st.success(f"Schedule for {pet.name} — Owner: {owner.name}")
        for i, task in enumerate(sorted_tasks, 1):
            st.markdown(f"**{i}. {task.title}** — {task.duration_minutes} min | Priority: `{task.priority}`")

if st.button("Clear all tasks"):
    pet.tasks = []
    st.session_state.task_counter = 0
    st.rerun()
