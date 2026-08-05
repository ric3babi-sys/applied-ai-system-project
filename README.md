# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
   - See `diagrams/maincomponents.mmd` for the implemented class architecture.
   - See `diagrams/dataflows.mmd` for the input → process → output dataflow.
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```
Sample Output from TERMINAL
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ clear && python3 main.py
======================================================================
PawPal+ Pet Care System - Example Usage
======================================================================

[1] Creating Owner...
    ✓ Owner created: John Smith (ID: 1)

[2] Creating first Pet...
    ✓ Pet created: Fluffy (ID: 1)
      Owner: John Smith

[3] Creating second Pet...
    ✓ Pet created: Buddy (ID: 2)
      Owner: John Smith

[4] John Smith's Pets Summary:
    Total pets owned: 2
      • Fluffy (ID: 1)
      • Buddy (ID: 2)

[5] Creating Tasks for Fluffy...
    ✓ Task 1: Walk (30 min) - Today at 09:00
    ✓ Task 2: Feed (15 min) - Today at 12:30
    ✓ Task 3: Nap Time (60 min) - Tomorrow at 14:00

[6] Creating Tasks for Buddy...
    ✓ Task 1: Feed (15 min) - Today at 08:00
    ✓ Task 2: Walk (45 min) - Today at 16:00
    ✓ Task 3: Vet Visit (30 min) - Day after tomorrow at 10:00

[7] System Statistics:
    Total Owners: 1
    Total Pets: 2
    Total Tasks: 0
    Average pets per owner: 2

[8] Pet Statistics:
    Total Pets in system: 2
    Total Tasks: 0
    Pets with pending tasks: 0
    Pets with no tasks: 2

======================================================================
TODAY'S SCHEDULE
======================================================================

Date: 2026-07-07
Total activities scheduled: 4

  1. [08:00] Buddy - Feed Pet (15 min)
  2. [09:00] Fluffy - Walk Pet (30 min)
  3. [12:30] Fluffy - Feed Pet (15 min)
  4. [16:00] Buddy - Walk Pet (45 min)

[9] Scheduler Statistics:
    Total Schedulers: 6
    Total Dates Scheduled: 3
    Today's Activities: 4
    Pending Activities: 6
    Total Duration: 195 minutes

======================================================================
Example completed successfully!
======================================================================

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ pytest
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py ...................                                                                                     [100%]

======================================================== 19 passed in 0.56s ========================================================

# Run with coverage:
pytest --cov
```
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ pytest --cov
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py ...................                                                                                     [100%]

========================================================== tests coverage ==========================================================
_________________________________________ coverage: platform linux, python 3.13.7-final-0 __________________________________________

Name                   Stmts   Miss  Cover
------------------------------------------
pawpal_system.py         692    408    41%
tests/__init__.py          0      0   100%
tests/test_pawpal.py     199      1    99%
------------------------------------------
TOTAL                    891    409    54%
======================================================== 19 passed in 0.80s ========================================================

Sample test output:
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ python3 tests/test_pawpal.py 
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0 -- /home/mait/Documents/codepath/AI/.venv-1/bin/python3
cachedir: .pytest_cache
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py::TestTaskDoTask::test_task_initial_status_is_incomplete PASSED                                          [  5%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_marks_task_as_completed PASSED                                             [ 10%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_sets_completed_timestamp PASSED                                            [ 15%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_multiple_calls PASSED                                                      [ 21%]
tests/test_pawpal.py::TestTaskDoTask::test_doTask_with_different_task_types PASSED                                           [ 26%]
tests/test_pawpal.py::TestTaskDoTask::test_task_completion_flow PASSED                                                       [ 31%]
tests/test_pawpal.py::TestTaskDoTask::test_completed_attribute_vs_method PASSED                                              [ 36%]
tests/test_pawpal.py::TestPetTasks::test_pet_initial_task_count_is_zero PASSED                                               [ 42%]
tests/test_pawpal.py::TestPetTasks::test_add_single_task_increases_count PASSED                                              [ 47%]
tests/test_pawpal.py::TestPetTasks::test_add_multiple_tasks_increases_count PASSED                                           [ 52%]
tests/test_pawpal.py::TestPetTasks::test_add_tasks_maintains_task_list PASSED                                                [ 57%]
tests/test_pawpal.py::TestPetTasks::test_add_multiple_different_task_types PASSED                                            [ 63%]
tests/test_pawpal.py::TestPetTasks::test_task_count_matches_task_list_length PASSED                                          [ 68%]
tests/test_pawpal.py::TestPetTasks::test_prevent_duplicate_task_addition PASSED                                              [ 73%]
tests/test_pawpal.py::TestPetTasks::test_add_task_with_pending_and_completed PASSED                                          [ 78%]
tests/test_pawpal.py::TestTaskInitialization::test_task_requires_pet_and_taskcode PASSED                                     [ 84%]
tests/test_pawpal.py::TestTaskInitialization::test_task_default_values PASSED                                                [ 89%]
tests/test_pawpal.py::TestTaskInitialization::test_invalid_taskcode_raises_error PASSED                                      [ 94%]
tests/test_pawpal.py::TestTaskInitialization::test_negative_duration_raises_error PASSED                                     [100%]

======================================================== 19 passed in 0.13s ========================================================
```
# Paste your pytest output here
```
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ python -m pytest
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.13.0
collected 19 items                                                                                                                 

tests/test_pawpal.py ...................                                                                                     [100%]

======================================================== 19 passed in 0.18s ========================================================

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature           | Method(s)              | Notes                                              |
|-------------------|------------------------|----------------------------------------------------|
| Task sorting      |sortTasksByScheduledTime| default chronological, uses year, month, date, time|
| Filter by status  |filterTasks             | filter by pet, completed task status, task code    |
| Conflict handling |checkScheduleConflict   | is checked when running newScheduler               |
| Recurring tasks   |scheduleRecurring       | creates number of schedule slots for one task      |

## Testing PawPal+
Test for Task.doTask() method and completion status.
Test for Pet task management and counting.
Test for Task initialization and validation.
Test for verifying schedules and tasks come back in chronological order.
Test for daily recurring tasks: completing one spawns the next day's.
Test for the Scheduler's duplicate/conflicting time flagging.
Test for duration-aware overlap detection (detectConflicts/hasConflicts).

## output from python -m pytest
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter$ python -m pytest
======================================================= test session starts ========================================================
platform linux -- Python 3.13.7, pytest-9.0.3, pluggy-1.6.0
rootdir: /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter
plugins: cov-7.1.0, anyio-4.13.0
collected 49 items                                                                                                                 

tests/test_pawpal.py .................................................                                                       [100%]

======================================================== 49 passed in 0.26s ========================================================

## Confidence Level
⭐⭐⭐⭐⭐

## ✨ Features

### Sorting & Filtering
- **Chronological sorting** — `sortSchedulesByTime`, `sortTasksByScheduledTime`
  Orders schedules by full (year, month, date, start-time). Times are compared as
  minutes-since-midnight (not string compare), so `09:00` correctly precedes `10:00`.
  Tasks are keyed on their *earliest* occurrence; unscheduled tasks always sort last.
- **Multi-criteria filtering** — `filterTasks`, `filterSchedules`
  Filter by pet, completion status, and/or task type in any combination; a criterion
  left as `None` is ignored.

### Conflict Detection
- **Duplicate-time warnings** — `checkScheduleConflict`
  Non-fatal, exact date+time match. Runs automatically inside `newScheduler`; the
  schedule is still created, the owner is just advised of the clash.
- **Duration-aware overlap detection** — `detectConflicts`, `hasConflicts`, `Scheduler.overlaps`
  Interval-based overlap on the same day (a 60-min 09:00 walk conflicts with a 09:30
  feed). Buckets by day, sorts, and scans once with early-exit. Adjacent tasks
  (one ends as the next begins) do **not** conflict.
- **Per-pet conflict check** — `Pet.findConflictingSchedules`
  Runs the shared overlap algorithm across all of a pet's schedules.

### Recurrence
- **Daily recurrence** — `Task.doTask` → `Task._spawnNextOccurrence`
  Completing a task flagged `isDaily` auto-spawns a fresh instance one day later
  (same type, duration, priority), re-scheduling each of its times +1 day. A guard
  prevents a second completion from spawning a duplicate.
- **Fixed-interval recurrence** — `scheduleRecurring`
  Creates N occurrences of a task stepping forward every K days (e.g. a daily 09:00
  walk for a week), correctly rolling over month/year boundaries via date arithmetic.
- **Recurrence detection & expansion** — `isRecurringTask`, `getRecurringSchedules`
  Flags tasks with >1 occurrence and returns their occurrences in chronological order.

### Planning
- **Greedy day planner** — `buildDayPlan`, `Owner.planDay`
  Orders pending tasks by priority (high→low), then duration (short→long), and packs
  them back-to-back from the day's start; tasks that don't fit the window are returned
  as `unplaced`.
- **Free-slot finder** — `getFreeSlots`, `findFreeSlot`
  Merges busy intervals and returns the open gaps, or the earliest start time that
  fits a given duration.
- **Daily load / overbooking** — `getDailyLoad`, `isDateOverbooked`
  Totals scheduled minutes for a date and flags it against a care-time budget
  (default 480 min).

### Data Model & Integrity
- **Priority model** — `DEFAULT_TASK_PRIORITY`
  Sensible defaults per task type (Vet > Feed > Walk > Nap), overridable 0–3.
- **O(1) lookups** — id/name indexes behind `getOwnerByID`, `getPetByName`, etc.,
  with a linear-scan fallback so a stale index can never return a wrong answer.
- **Cascading cleanup** — `removeOwner`, `removePet`
  Removing an owner/pet cascades to its pets, tasks, and schedulers (no orphans).

## 📸 Demo Walkthrough

- The main UI features and what actions a user can perform
  Owner Management allows you to add owner and view all known owners
  Pet Management allows you to add a pet, set it's owner, and view all known pets
  Scheduling Tasks lets you configure a task for a particular pet.

- An example workflow
  Create a new owner
  Create a new pet and assign owner
  Schedule a task and link to pet
  View pet's tasks and today's schedule

- Sorting Scheduler behavior
  Create a new owner
  Create a new pet and assign owner
  Schedule a task and link to pet
  Schedule another task before 1st task
  View pet's tasks should sort by date and time

- Scheduler conflict warnings behavior
  Create a new owner
  Create a new pet and assign owner
  Schedule a task and link to pet
  Schedule another task before 1st task
  Schedule 3rd task with same time as 2nd task
  View pet's tasks should show a conflict alert with emoji for the columns involved

- CLI terminal output from running main.py
(.venv-1) mait@Ubuntu-dev:~/Documents/codepath/AI$ /home/mait/Documents/codepath/AI/.venv-1/bin/python /home/mait/Documents/codepath/AI/Week4/ai110-module2show-pawpal-starter/main.py
======================================================================
PawPal+ Pet Care System - Example Usage
======================================================================

[1] Creating Owner...
    ✓ Owner created: John Smith (ID: 1)

[2] Creating first Pet...
    ✓ Pet created: Fluffy (ID: 1)
      Owner: John Smith

[3] Creating second Pet...
    ✓ Pet created: Buddy (ID: 2)
      Owner: John Smith

[4] John Smith's Pets Summary:
    Total pets owned: 2
      • Fluffy (ID: 1)
      • Buddy (ID: 2)

[5] Creating Tasks for Fluffy...
    ✓ Task 1: Walk (30 min) - Today at 09:00
    ✓ Task 2: Feed (15 min) - Today at 12:30
    ✓ Task 3: Nap Time (60 min) - Tomorrow at 14:00

[6] Creating Tasks for Buddy...
    ✓ Task 1: Feed (15 min) - Today at 08:00
    ✓ Task 2: Walk (45 min) - Today at 16:00
    ✓ Task 3: Vet Visit (30 min) - Day after tomorrow at 10:00

[7] System Statistics:
    Total Owners: 1
    Total Pets: 2
    Total Tasks: 0
    Average pets per owner: 2

[8] Pet Statistics:
    Total Pets in system: 2
    Total Tasks: 0
    Pets with pending tasks: 0
    Pets with no tasks: 2

======================================================================
TODAY'S SCHEDULE
======================================================================

Date: 2026-07-08
Total activities scheduled: 4

  1. [08:00] Buddy - Feed Pet (15 min)
  2. [09:00] Fluffy - Walk Pet (30 min)
  3. [12:30] Fluffy - Feed Pet (15 min)
  4. [16:00] Buddy - Walk Pet (45 min)

======================================================================
SORT SCHEDULER BY TIME
======================================================================

Created 5 tasks for Ziggy on 2026-07-08 (out of order):
  • [15:45] Walk Pet (30 min)
  • [07:15] Feed Pet (15 min)
  • [20:00] Nap Time (60 min)
  • [06:30] Veterinarian Visit (45 min)
  • [11:00] Feed Pet (15 min)

After sortSchedulesByTime() (chronological):
  1. [06:30] Veterinarian Visit (45 min)
  2. [07:15] Feed Pet (15 min)
  3. [11:00] Feed Pet (15 min)
  4. [15:45] Walk Pet (30 min)
  5. [20:00] Nap Time (60 min)

======================================================================
SORTING AND FILTERING
======================================================================

[A] All scheduled tasks for 'Fluffy':
    Found 3 scheduled task(s).
      • 2026-07-08 [09:00] Walk Pet (30 min)
      • 2026-07-08 [12:30] Feed Pet (15 min)
      • 2026-07-09 [14:00] Nap Time (60 min)

[B] 'Fluffy' schedule sorted by time (sortSchedulesByTime):
    1. 2026-07-08 [09:00] Walk Pet (30 min)
    2. 2026-07-08 [12:30] Feed Pet (15 min)
    3. 2026-07-09 [14:00] Nap Time (60 min)

======================================================================
CONFLICT DETECTION
======================================================================

Scheduling two tasks at 2026-07-08 18:30 ...
  → Booking Fluffy's Feed:
  → Booking Buddy's Walk (same slot):
⚠️ Schedule conflict at 2026-07-08 18:30: slot already booked for Fluffy (Feed Pet).

Direct checkScheduleConflict() call for that slot:
  ⚠️ Schedule conflict at 2026-07-08 18:30: slot already booked for Fluffy (Feed Pet), Buddy (Walk Pet).
  Free slot (23:15) -> no conflict (as expected)

[9] Scheduler Statistics:
    Total Schedulers: 13
    Total Dates Scheduled: 3
    Today's Activities: 11
    Pending Activities: 13
    Total Duration: 405 minutes

======================================================================
Example completed successfully!
======================================================================
(.venv-1) mait@Ubuntu-de

Describe your app in numbered steps so a reader can follow along without watching a video:

1. Create a new owner
2. Create a new pet and assign owner
3. Schedule a task and link to pet
4. View pet's tasks and today's schedule


**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
