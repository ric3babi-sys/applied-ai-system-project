import streamlit as st
import pandas as pd
import re
from datetime import datetime

# Import PawPal+ system classes and functions
from pawpal_system import (
    # Core classes
    Owner, Pet, Task, Scheduler,
    # Global data structures
    ownerList, petList, schedulerDictionary, TASK_TYPES,
    # Owner management functions
    newOwner,
    getOwnerByID,
    getOwnerByName,
    getAllOwners,
    removeOwner,
    getOwnerCount,
    getSystemStatistics,
    clearAllData,
    # Pet management functions
    newPet,
    getPetByID,
    getPetByName,
    getPetsByOwner,
    getAllPets,
    removePet,
    getPetCount,
    getPetsByTaskType,
    getPetsWithPendingTasks,
    getPetsWithNoTasks,
    getPetStatistics,
    # Scheduler management functions
    newScheduler,
    getSchedulerByKey,
    getSchedulersByDate,
    getSchedulersByPet,
    getSchedulersByTask,
    getAllSchedulers,
    removeScheduler,
    getSchedulerCount,
    getSchedulesByDateRange,
    getSchedulerStatistics,
    # Planning helpers (weekly improvements)
    timeToMinutes,
    buildDayPlan,
    getFreeSlots,
    findFreeSlot,
    getDailyLoad,
    isDateOverbooked,
    scheduleRecurring,
    DEFAULT_TASK_PRIORITY,
    # Target Features: sorting, filtering, recurring, conflict detection
    sortSchedulesByTime,
    sortTasksByScheduledTime,
    filterSchedules,
    isRecurringTask,
    getRecurringSchedules,
    detectConflicts,
    hasConflicts,
)

# Priority code -> human label, used in the task-creation UI (#3).
PRIORITY_LABELS = {0: "Low", 1: "Normal", 2: "High", 3: "Urgent"}
# Daily care-time budget (minutes) used to flag overbooked days (#7).
DAILY_BUDGET_MINUTES = 480

# Map month words to numeric values for natural language schedule parsing.
MONTH_NAME_TO_NUMBER = {
    'january': 1, 'jan': 1,
    'february': 2, 'feb': 2,
    'march': 3, 'mar': 3,
    'april': 4, 'apr': 4,
    'may': 5,
    'june': 6, 'jun': 6,
    'july': 7, 'jul': 7,
    'august': 8, 'aug': 8,
    'september': 9, 'sep': 9, 'sept': 9,
    'october': 10, 'oct': 10,
    'november': 11, 'nov': 11,
    'december': 12, 'dec': 12,
}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def init_pawpal_session():
    """
    Initialize PawPal+ system objects in session_state.
    Checks if objects already exist in the "vault" before creating new ones.
    This prevents data loss across Streamlit reruns.
    """
    # Initialize global data structures (persist across reruns)
    if "ownerList" not in st.session_state:
        st.session_state.ownerList = []
        st.session_state.has_initial_data = False

    if "petList" not in st.session_state:
        st.session_state.petList = []

    if "schedulerDictionary" not in st.session_state:
        st.session_state.schedulerDictionary = {}

    if "TASK_TYPES" not in st.session_state:
        st.session_state.TASK_TYPES = TASK_TYPES

    # Track current selections
    if "current_owner" not in st.session_state:
        st.session_state.current_owner = None

    if "current_pet" not in st.session_state:
        st.session_state.current_pet = None

    if "current_tasks" not in st.session_state:
        st.session_state.current_tasks = []


# Initialize session state on app load
init_pawpal_session()


def find_owner_by_name(owner_name: str):
    normalized = owner_name.strip().lower()
    return next(
        (owner for owner in st.session_state.ownerList
         if owner.getOwnerName().strip().lower() == normalized),
        None,
    )


def find_pet_by_name(pet_name: str):
    normalized = pet_name.strip().lower()
    return next(
        (pet for pet in st.session_state.petList
         if pet.getPetName().strip().lower() == normalized),
        None,
    )


def parse_owner_command(command: str):
    match = re.search(
        r'owner\s+(?:named\s+)?["\']?(?P<name>.+?)["\']?(?:\s+for\b|\s+with\b|\s+to\b|$)',
        command,
        re.IGNORECASE,
    )
    return match.group('name').strip() if match else None


def parse_pet_command(command: str):
    match = re.search(
        r'pet\s+(?:named\s+)?["\']?(?P<pet>.+?)["\']?\s+for\s+["\']?(?P<owner>.+?)["\']?(?:\s|$)',
        command,
        re.IGNORECASE,
    )
    if match:
        return match.group('pet').strip(), match.group('owner').strip()
    return None, None


def find_task_for_pet(pet, task_code: int):
    for task in pet.getPetTaskList():
        if task.getTaskCode() == task_code:
            return task
    return None


def find_task_for_pet_on_date(pet, task_code: int, date_str: str):
    for task in pet.getPetTaskList():
        if task.getTaskCode() != task_code:
            continue
        for scheduler in task.getSchedulerList():
            if scheduler.getDateString() == date_str:
                return task, scheduler
    return None, None


def parse_month_word_date(command: str):
    """Parse month names in natural language dates and return YYYY-MM-DD.

    Supports both full month names and shorthand abbreviations, such as:
      - August 25 2026
      - Aug 25 2026
      - 25 August 2026
      - 25 Aug 2026
    """
    lower = command.lower()
    month_names = r'jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?'
    patterns = [
        rf'\b(?P<month>{month_names})\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?(?:,)?\s+(?P<year>\d{{4}})\b',
        rf'\b(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+(?P<month>{month_names})(?:,)?\s+(?P<year>\d{{4}})\b',
    ]
    for pattern in patterns:
        match = re.search(pattern, lower)
        if match:
            month_word = match.group('month')
            day = int(match.group('day'))
            year = int(match.group('year'))
            month = MONTH_NAME_TO_NUMBER.get(month_word)
            if month and 1 <= day <= 31:
                return f"{year:04d}-{month:02d}-{day:02d}"
    return None


def parse_task_command(command: str):
    lower = command.lower()
    pet = None
    for candidate in st.session_state.petList:
        if candidate.getPetName().strip().lower() in lower:
            pet = candidate
            break

    task_code = None
    task_label = None
    task_keyword_map = {
        0: ["walk", "walk pet"],
        1: ["feed", "feed pet"],
        2: ["nap", "nap time"],
        3: ["vet", "veterinarian", "vet visit", "veterinarian visit"],
    }
    for code, keywords in task_keyword_map.items():
        for keyword in keywords:
            if keyword in lower:
                task_code = code
                task_label = keyword
                break
        if task_code is not None:
            break

    if not pet and task_label:
        # Support shorter commands like "walk Mochi", "feed Mochi", or
        # "feed pet Mochi" even when the full task label is not present.
        pattern = rf'\b{re.escape(task_label)}\s+(?:pet\s+)?(?P<pet>.+?)(?:\s+on\b|\s+at\b|\s+for\b|$)'
        match = re.search(pattern, lower)
        if match:
            candidate_name = match.group('pet').strip()
            for candidate in st.session_state.petList:
                if candidate.getPetName().strip().lower() == candidate_name:
                    pet = candidate
                    break
                if candidate_name in candidate.getPetName().strip().lower():
                    pet = candidate
                    break

    date = None
    numeric_date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', command)
    if numeric_date_match:
        date = numeric_date_match.group(1)
    else:
        date = parse_month_word_date(command)

    time_match = re.search(r'\b(\d{1,2}:\d{2})\b', command)
    duration_match = re.search(r'\b(\d+)\s*(?:min|mins|minutes)\b', command, re.IGNORECASE)
    priority_words = {
        'urgent': 3,
        'high': 2,
        'normal': 1,
        'medium': 1,
        'low': 0,
    }
    priority = 0
    for word, value in priority_words.items():
        if word in lower:
            priority = value
            break

    return {
        'pet': pet,
        'task_code': task_code,
        'date': date,
        'time': time_match.group(1) if time_match else None,
        'duration': int(duration_match.group(1)) if duration_match else 30,
        'priority': priority,
    }


def execute_natural_language_input(command: str):
    command = command.strip()
    if not command:
        return {'success': False, 'message': 'Enter a natural language command first.'}

    lower = command.lower()
    if 'owner' in lower and any(word in lower for word in ('remove', 'delete')):
        owner_name = parse_owner_command(command)
        if not owner_name:
            return {
                'success': False,
                'message': 'Could not identify the owner name. Try: remove owner Jordan',
            }
        owner = find_owner_by_name(owner_name)
        if not owner:
            return {
                'success': False,
                'message': f"Owner '{owner_name}' not found.",
            }
        removeOwner(owner)
        st.session_state.ownerList = [o for o in st.session_state.ownerList if o != owner]
        st.session_state.petList = [p for p in st.session_state.petList if p.getOwner() != owner]
        return {
            'success': True,
            'message': f"Removed owner '{owner_name}' and all their pets/tasks.",
        }

    if 'pet' in lower and any(word in lower for word in ('remove', 'delete')):
        pet_name, owner_name = parse_pet_command(command)
        if not pet_name or not owner_name:
            return {
                'success': False,
                'message': 'Could not identify pet name and owner. Try: remove pet Mochi for Jordan',
            }
        owner = find_owner_by_name(owner_name)
        if not owner:
            return {
                'success': False,
                'message': f"Owner '{owner_name}' not found.",
            }
        pet = next((p for p in owner.getPetList() if p.getPetName().strip().lower() == pet_name.strip().lower()), None)
        if not pet:
            return {
                'success': False,
                'message': f"Pet '{pet_name}' for owner '{owner_name}' not found.",
            }
        removePet(pet)
        st.session_state.petList = [p for p in st.session_state.petList if p != pet]
        return {
            'success': True,
            'message': f"Removed pet '{pet_name}' from owner '{owner_name}'.",
        }

    if 'task' in lower and any(word in lower for word in ('remove', 'delete')):
        parsed = parse_task_command(command)
        if not parsed['pet']:
            return {
                'success': False,
                'message': 'Could not identify the pet in the command. Use a pet name like Mochi.',
            }
        if parsed['task_code'] is None:
            return {
                'success': False,
                'message': 'Could not identify the task type. Use one of the known task names.',
            }

        task = None
        scheduler = None
        if parsed['date']:
            task, scheduler = find_task_for_pet_on_date(parsed['pet'], parsed['task_code'], parsed['date'])
        if not task:
            task = find_task_for_pet(parsed['pet'], parsed['task_code'])

        if not task:
            return {
                'success': False,
                'message': f"No task '{st.session_state.TASK_TYPES[parsed['task_code']]}' found for {parsed['pet'].getPetName()}.",
            }

        if scheduler:
            removeScheduler(scheduler)
            if task.getScheduleCount() == 0:
                parsed['pet'].removePetTask(task)
            return {
                'success': True,
                'message': f"Removed scheduled occurrence for '{st.session_state.TASK_TYPES[parsed['task_code']]}' on {parsed['date']} for {parsed['pet'].getPetName()}.",
            }

        removed = parsed['pet'].removePetTask(task)
        if not removed:
            return {
                'success': False,
                'message': 'Failed to remove the task. It may already be deleted.',
            }
        return {
            'success': True,
            'message': f"Removed task '{st.session_state.TASK_TYPES[parsed['task_code']]}' for {parsed['pet'].getPetName()}.",
        }

    if 'owner' in lower and any(word in lower for word in ('add', 'create')):
        owner_name = parse_owner_command(command)
        if not owner_name:
            return {
                'success': False,
                'message': 'Could not identify the owner name. Try: add owner Jordan',
            }
        if find_owner_by_name(owner_name):
            return {
                'success': False,
                'message': f"Owner '{owner_name}' already exists.",
            }
        owner = newOwner(owner_name)
        st.session_state.ownerList.append(owner)
        return {
            'success': True,
            'message': f"Added owner '{owner_name}' successfully.",
        }

    if 'pet' in lower and any(word in lower for word in ('add', 'create')):
        pet_name, owner_name = parse_pet_command(command)
        if not pet_name or not owner_name:
            return {
                'success': False,
                'message': 'Could not identify pet name and owner. Try: add pet Mochi for Jordan',
            }
        owner = find_owner_by_name(owner_name)
        if not owner:
            return {
                'success': False,
                'message': f"Owner '{owner_name}' was not found. Add that owner first.",
            }
        if find_pet_by_name(pet_name):
            return {
                'success': False,
                'message': f"Pet '{pet_name}' already exists.",
            }
        pet = newPet(pet_name, owner)
        st.session_state.petList.append(pet)
        return {
            'success': True,
            'message': f"Added pet '{pet_name}' for owner '{owner_name}'.",
        }

    if any(word in lower for word in ('schedule', 'task', 'feed', 'walk', 'groom', 'vet', 'play')):
        parsed = parse_task_command(command)
        if not parsed['pet']:
            return {
                'success': False,
                'message': 'Could not identify the pet in the command. Use a pet name like Mochi.',
            }
        if parsed['task_code'] is None:
            return {
                'success': False,
                'message': 'Could not identify the task type. Use one of the known task names.',
            }

        # Require numeric HH:MM time format for any command that includes a date.
        if parsed['date'] and not parsed['time']:
            return {
                'success': False,
                'message': 'Scheduled tasks require time in numeric HH:MM format, e.g. 18:00.',
            }

        task = Task(
            pet=parsed['pet'],
            taskCode=parsed['task_code'],
            priority=parsed['priority'],
            isDaily=False,
        )
        task.setTaskDuration(parsed['duration'])
        added = parsed['pet'].addPetTask(task)
        if not added:
            return {
                'success': False,
                'message': f"Task for pet '{parsed['pet'].getPetName()}' already exists or failed to add.",
            }

        details = []
        if parsed['date'] and parsed['time']:
            year, month, day = map(int, parsed['date'].split('-'))
            newScheduler(task, year=year, month=month, date=day, time=parsed['time'])
            details.append(f"Scheduled on {parsed['date']} at {parsed['time']}")

        return {
            'success': True,
            'message': f"Created task '{st.session_state.TASK_TYPES[parsed['task_code']]}' for {parsed['pet'].getPetName()}.",
            'details': '\n'.join(details) if details else None,
        }

    return {
        'success': False,
        'message': 'The command was not recognized. Try adding an owner, adding a pet, or scheduling a task.',
    }


st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

left_col, right_col = st.columns([3, 7])
with left_col:
    st.subheader("Natural language command pane")
    st.markdown(
        "Use natural language commands to add owners, add pets, or schedule tasks."
    )
    nlp_command = st.text_area(
        "Enter a command", key="nl_command", height=260,
        placeholder="e.g. add owner Jordan\nadd pet Mochi for Jordan\nschedule walk for Mochi on 2026-08-25 at 09:00 for 30 minutes, high priority"
    )
    if st.button("Execute command", key="nl_execute"):
        result = execute_natural_language_input(nlp_command)
        if result['success']:
            st.success(result['message'])
            if result.get('details'):
                st.info(result['details'])
        else:
            st.error(result['message'])

with right_col:
    st.subheader("Command helper")
    st.markdown(
        """
This command parser is case-insensitive for owner and pet names.

- `add owner Jordan`
- `add pet Mochi for Jordan`
- `schedule walk for Mochi on 2026-08-25 at 09:00 for 30 minutes, high priority`
- `feed Mochi on 2026-08-25 at 18:00`
- `walk Mochi`
- `feed Mochi`
- `remove owner Jordan`
- `remove pet Mochi for Jordan`
- `delete task walk for Mochi`
- `remove task walk for Mochi on 2026-08-25`
"""
    )

st.subheader("Owner & Pet Management")

# Owner input section
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    if st.button("Add Owner"):
        # Check if owner already exists (prevent duplicates)
        existing = next((o for o in st.session_state.ownerList if o.getOwnerName().lower() == owner_name.lower()), None)
        if existing:
            st.warning(f"Owner '{owner_name}' already exists!")
        else:
            owner = newOwner(owner_name)
            st.session_state.ownerList.append(owner)
            st.success(f"Added owner: {owner_name}")

with col2:
    st.write(f"**Total Owners:** {len(st.session_state.ownerList)}")
    if st.session_state.ownerList:
        st.write("Current owners:")
        for owner in st.session_state.ownerList:
            st.write(f"  • {owner.getOwnerName()}")

st.divider()

# Pet input section
if st.session_state.ownerList:
    selected_owner_name = st.selectbox(
        "Select owner for pet",
        [o.getOwnerName() for o in st.session_state.ownerList]
    )
    selected_owner = next(o for o in st.session_state.ownerList if o.getOwnerName() == selected_owner_name)

    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Pet name", value="Mochi")
        if st.button("Add Pet"):
            # Check if pet already exists for this owner
            existing = next((p for p in selected_owner.getPetList() if p.getPetName().lower() == pet_name.lower()), None)
            if existing:
                st.warning(f"Pet '{pet_name}' already exists for {selected_owner_name}!")
            else:
                pet = newPet(pet_name, selected_owner)
                st.session_state.petList.append(pet)
                st.success(f"Added pet: {pet_name} to {selected_owner_name}")

    with col2:
        st.write(f"**Total Pets:** {len(st.session_state.petList)}")
        if selected_owner.getPetList():
            st.write(f"**{selected_owner_name}'s pets:**")
            for pet in selected_owner.getPetList():
                st.write(f"  • {pet.getPetName()}")
else:
    st.info("Add an owner first to manage pets.")

st.markdown("### Scheduling Tasks")
st.caption("Create tasks for the selected pet and schedule them.")

# Task creation section - requires a pet to be selected
if st.session_state.petList:
    # Pet selection for task assignment
    selected_pet_name = st.selectbox(
        "Select pet for task",
        [p.getPetName() for p in st.session_state.petList],
        key="task_pet_select"
    )
    selected_pet = next(p for p in st.session_state.petList if p.getPetName() == selected_pet_name)

    # Task creation inputs
    col1, col2, col3 = st.columns(3)
    with col1:
        task_type = st.selectbox(
            "Task type",
            list(st.session_state.TASK_TYPES.values()),
            key="task_type_select"
        )
        # Get the task code from the selected task type
        task_code = [k for k, v in st.session_state.TASK_TYPES.items() if v == task_type][0]

    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30, key="task_duration")

    with col3:
        # Priority defaults to the task type's default, but the owner can override (#3).
        default_priority = DEFAULT_TASK_PRIORITY.get(task_code, 0)
        priority = st.selectbox(
            "Priority",
            options=[0, 1, 2, 3],
            index=default_priority,
            format_func=lambda p: PRIORITY_LABELS[p],
            key="task_priority",
        )

    # Task scheduling inputs
    col1, col2 = st.columns(2)
    with col1:
        task_date = st.date_input("Date", value=datetime.now().date(), key="task_date")
    with col2:
        task_time = st.time_input("Time", value=datetime.min.time(), key="task_time")

    # Free-slot suggestion for the chosen date + duration (#4)
    existing_for_date = getSchedulersByDate(task_date.year, task_date.month, task_date.day)
    suggested_slot = findFreeSlot(existing_for_date, duration)
    if suggested_slot:
        st.caption(f"💡 Earliest free {duration}-min slot on {task_date.strftime('%b %d')}: **{suggested_slot}**")
    else:
        st.caption(f"⚠️ No free {duration}-min slot found on {task_date.strftime('%b %d')} within 08:00–20:00.")

    # Daily task flag: auto-recreates itself for the next day when completed.
    daily = st.checkbox("Daily task (re-creates itself for the next day when completed)",
                        key="task_daily")

    # Recurring schedule options (#8)
    repeat = st.checkbox("Repeat this task", key="task_repeat")
    if repeat:
        rcol1, rcol2 = st.columns(2)
        with rcol1:
            occurrences = st.number_input("Occurrences", min_value=2, max_value=60, value=7, key="task_occurrences")
        with rcol2:
            interval_days = st.number_input("Every N days", min_value=1, max_value=30, value=1, key="task_interval")
    else:
        occurrences = 1
        interval_days = 1

    if st.button("Create & Schedule Task"):
        try:
            time_str = f"{task_time.hour:02d}:{task_time.minute:02d}"

            # Create the Task object with the chosen priority and daily flag
            task = Task(pet=selected_pet, taskCode=task_code, priority=priority, isDaily=daily)
            task.setTaskDuration(duration)

            # Add task to pet's task list
            result = selected_pet.addPetTask(task)
            if result:
                if repeat:
                    # Create one Scheduler per occurrence (#8)
                    created = scheduleRecurring(
                        task,
                        task_date.year, task_date.month, task_date.day,
                        time_str,
                        occurrences=int(occurrences),
                        interval_days=int(interval_days),
                    )
                    st.success(f"✓ Created recurring {task_type} task for {selected_pet_name}")
                    st.info(f"Scheduled {len(created)} times, every {int(interval_days)} day(s) at {time_str}, "
                            f"starting {task_date.strftime('%Y-%m-%d')}")
                else:
                    # Create a single Scheduler for the task
                    newScheduler(
                        task,
                        year=task_date.year,
                        month=task_date.month,
                        date=task_date.day,
                        time=time_str,
                    )
                    daily_note = " · 🔁 daily" if daily else ""
                    st.success(f"✓ Created {task_type} task for {selected_pet_name}{daily_note}")
                    st.info(f"Scheduled for {task_date.strftime('%Y-%m-%d')} at {time_str} "
                            f"(priority: {PRIORITY_LABELS[priority]})")

                # Warn if the start date is now overbooked (#7)
                if isDateOverbooked(task_date.year, task_date.month, task_date.day, DAILY_BUDGET_MINUTES):
                    load = getDailyLoad(task_date.year, task_date.month, task_date.day)
                    st.warning(f"⚠️ {task_date.strftime('%b %d')} is overbooked: "
                               f"{load} min scheduled (budget {DAILY_BUDGET_MINUTES} min).")

                # Surface any time conflicts this created for the pet (#1)
                conflicts = selected_pet.findConflictingSchedules()
                if conflicts:
                    st.warning(f"⚠️ {selected_pet_name} has {len(conflicts)} overlapping schedule(s). "
                               "Check the times below.")
            else:
                st.error("Failed to add task to pet (duplicate detected)")

        except Exception as e:
            st.error(f"Error creating task: {str(e)}")

    # Display tasks for selected pet
    if selected_pet.getPetTaskList():
        st.markdown(f"#### 🐾 {selected_pet_name}'s Tasks")

        # Order tasks by their earliest scheduled time (Target Feature);
        # unscheduled tasks fall to the end.
        ordered_tasks = sortTasksByScheduledTime(selected_pet.getPetTaskList())

        # Collect schedule IDs involved in a time overlap so we can flag those rows (#1).
        # (Scheduler is a mutable dataclass and therefore unhashable, so key on its ID.)
        conflicting_schedules = set()
        for s1, s2 in selected_pet.findConflictingSchedules():
            conflicting_schedules.add(s1.getSchedulerID())
            conflicting_schedules.add(s2.getSchedulerID())

        # Build one row per task for a clean, professional table view.
        task_rows = []
        for task in ordered_tasks:
            # Badge daily tasks and recurring tasks (more than one occurrence).
            if task.isDailyTask():
                repeat = "🔁 daily"
            elif isRecurringTask(task):
                repeat = f"🔁 ×{task.getScheduleCount()}"
            else:
                repeat = "—"

            # Derive the scheduled window from the earliest occurrence.
            task_schedules = task.getSchedulerList()
            if task_schedules:
                earliest = sortSchedulesByTime(task_schedules)[0]
                when = f"{earliest.getDateString()} {earliest.getTime()}"
                if isRecurringTask(task):
                    when += f" → {getRecurringSchedules(task)[-1].getDateString()}"
            else:
                when = "Not scheduled"

            # Flag the task if any of its schedules overlaps another (#1).
            in_conflict = any(s.getSchedulerID() in conflicting_schedules
                              for s in task.getSchedulerList())

            task_rows.append({
                "Task": task.getTaskDescription(),
                "When": when,
                "Duration": f"{task.getTaskDuration()} min",
                "Priority": PRIORITY_LABELS[task.getPriority()],
                "Repeat": repeat,
                "Status": "✅ Completed" if task.isTaskCompleted() else "⏳ Pending",
                "Alert": "⚠️ overlap" if in_conflict else "",
            })

        st.table(pd.DataFrame(task_rows))

        # Summarize completion status with an at-a-glance banner.
        pending = selected_pet.getPendingTaskCount()
        total = selected_pet.getTaskCount()
        if pending == 0:
            st.success(f"🎉 All {total} of {selected_pet_name}'s tasks are complete!")
        else:
            st.info(f"⏳ {pending} of {total} task(s) still pending for {selected_pet_name}.")
    else:
        st.info(f"No tasks yet for {selected_pet_name}.")

    # --- Plan My Day (#2): greedily order the owner's pending tasks ---
    plan_owner = selected_pet.getOwner()
    with st.expander(f"🗓️ Plan {plan_owner.getOwnerName()}'s day", expanded=False):
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            day_start = st.time_input("Day starts", value=datetime.strptime("08:00", "%H:%M").time(), key="plan_start")
        with pcol2:
            day_end = st.time_input("Day ends", value=datetime.strptime("20:00", "%H:%M").time(), key="plan_end")

        if st.button("Build plan"):
            plan = plan_owner.planDay(
                day_start=f"{day_start.hour:02d}:{day_start.minute:02d}",
                day_end=f"{day_end.hour:02d}:{day_end.minute:02d}",
            )
            if plan["planned"]:
                st.success(f"✅ Planned {len(plan['planned'])} task(s) — "
                           f"{plan['total_minutes']} min of care.")
                plan_rows = [
                    {
                        "Time": f"{item['start']}–{item['end']}",
                        "Pet": item["task"].getPet().getPetName(),
                        "Task": item["task"].getTaskDescription(),
                        "Priority": PRIORITY_LABELS[item["task"].getPriority()],
                        "Duration": f"{item['duration']} min",
                    }
                    for item in plan["planned"]
                ]
                st.table(pd.DataFrame(plan_rows))
            else:
                st.info("No pending tasks with a duration to plan.")

            if plan["unplaced"]:
                st.warning(f"⚠️ {len(plan['unplaced'])} task(s) didn't fit in the window:")
                unplaced_rows = [
                    {
                        "Pet": task.getPet().getPetName(),
                        "Task": task.getTaskDescription(),
                        "Duration": f"{task.getTaskDuration()} min",
                        "Priority": PRIORITY_LABELS[task.getPriority()],
                    }
                    for task in plan["unplaced"]
                ]
                st.table(pd.DataFrame(unplaced_rows))

else:
    st.info("Add a pet first to create and schedule tasks.")

st.divider()

st.subheader("📅 Today's Schedule")
st.caption("View all tasks scheduled for today.")

# Get today's date
today = datetime.now()
today_year = today.year
today_month = today.month
today_day = today.day

# Retrieve today's schedule using getSchedulersByDate
today_schedule = getSchedulersByDate(today_year, today_month, today_day)

if today_schedule:
    st.write(f"**Date:** {today.strftime('%A, %B %d, %Y')}")
    st.write(f"**Total activities scheduled:** {len(today_schedule)}")

    # Daily-load / overbooking banner (#7)
    todays_load = getDailyLoad(today_year, today_month, today_day)
    if isDateOverbooked(today_year, today_month, today_day, DAILY_BUDGET_MINUTES):
        st.warning(f"⚠️ Today is overbooked: {todays_load} min scheduled "
                   f"(budget {DAILY_BUDGET_MINUTES} min).")
    else:
        st.caption(f"Total care time today: {todays_load} / {DAILY_BUDGET_MINUTES} min budget.")

    # Conflict banner: flag overlapping schedules anywhere in today's plan.
    todays_conflicts = detectConflicts(today_schedule)
    # Flatten the conflicting pairs into a set of IDs so we can mark individual rows
    # below (Scheduler is a mutable dataclass and therefore unhashable).
    conflicting_today = set()
    for s1, s2 in todays_conflicts:
        conflicting_today.add(s1.getSchedulerID())
        conflicting_today.add(s2.getSchedulerID())
    if todays_conflicts:
        st.warning(f"⚠️ {len(todays_conflicts)} overlapping schedule(s) today. "
                   "Overlapping tasks share a time window.")

    # Filter controls (by pet / by status) -- Target Feature.
    fcol1, fcol2 = st.columns(2)
    with fcol1:
        pet_names = ["All pets"] + [p.getPetName() for p in st.session_state.petList]
        pet_filter = st.selectbox("Filter by pet", pet_names, key="today_pet_filter")
    with fcol2:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Completed"],
                                     key="today_status_filter")

    # Resolve the selected pet object (None = all pets).
    selected_filter_pet = None
    if pet_filter != "All pets":
        selected_filter_pet = next(
            (p for p in st.session_state.petList if p.getPetName() == pet_filter), None)
    # Map the status label to the completed flag filterSchedules expects.
    completed_filter = {"All": None, "Pending": False, "Completed": True}[status_filter]

    # Filter first, then sort chronologically (Target Features).
    filtered_schedule = filterSchedules(
        today_schedule, pet=selected_filter_pet, completed=completed_filter)
    sorted_schedule = sortSchedulesByTime(filtered_schedule)

    if not sorted_schedule:
        st.info("No scheduled tasks match the current filter.")
    else:
        # Render the sorted + filtered schedule as a professional table.
        schedule_rows = []
        for scheduler in sorted_schedule:
            task = scheduler.getTask()
            schedule_rows.append({
                "Time": f"{scheduler.getTime()}–{scheduler.getEndTime()}",
                "Pet": scheduler.getPetName(),
                "Task": scheduler.getTaskType(),
                "Duration": f"{scheduler.getTaskDuration()} min",
                "Status": "✅ Completed" if task and task.isTaskCompleted() else "⏳ Pending",
                # Flag rows that overlap another schedule (#1).
                "Alert": "⚠️ overlap" if scheduler.getSchedulerID() in conflicting_today else "",
            })
        st.table(pd.DataFrame(schedule_rows))
        st.caption(f"Showing {len(sorted_schedule)} of {len(today_schedule)} scheduled task(s).")

    # Show system statistics
    st.divider()
    st.subheader("📊 System Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        stats = getSystemStatistics()
        st.metric("Total Owners", stats['total_owners'])

    with col2:
        st.metric("Total Pets", stats['total_pets'])

    with col3:
        st.metric("Today's Tasks", len(today_schedule))

    # Show task completion rates
    if st.session_state.petList:
        st.write("**Pet Task Status:**")
        for pet in st.session_state.petList:
            progress = pet.getTaskCompletionRate()
            st.progress(progress / 100, text=f"{pet.getPetName()}: {pet.getCompletedTaskCount()}/{pet.getTaskCount()} completed")

else:
    st.info(f"No tasks scheduled for {today.strftime('%B %d, %Y')}. Create and schedule some tasks above!")
