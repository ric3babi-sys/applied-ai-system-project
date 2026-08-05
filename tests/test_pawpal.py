"""
Unit tests for PawPal+ pet care system.
Tests core functionality of Owner, Pet, Task, and Scheduler classes.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path to import pawpal_system
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from pawpal_system import (
    Owner, Pet, Task, Scheduler,
    newOwner, newPet, newScheduler,
    removeOwner, removePet,
    getOwnerByName, getPetByName,
    getPetsByOwner, getPetsByTaskType,
    getPetsWithPendingTasks, getPetsWithNoTasks,
    getPetStatistics, getSchedulerByKey,
    scheduleRecurring, buildDayPlan, getFreeSlots,
    findFreeSlot, isDateOverbooked, filterSchedules,
    sortSchedulesByTime, sortTasksByScheduledTime,
    checkScheduleConflict, detectConflicts, hasConflicts,
    clearAllData, ownerList, petList, schedulerDictionary
)


class TestTaskDoTask:
    """Test suite for Task.doTask() method and completion status."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        # Clear global data structures
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_task_initial_status_is_incomplete(self):
        """Verify that a newly created Task has incomplete status."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        assert task.isTaskCompleted() is False, "New task should be incomplete"
        assert task.completed is False, "Task.completed should be False"

    def test_doTask_marks_task_as_completed(self):
        """Verify that doTask() changes task status from incomplete to completed."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Verify initial state
        assert task.isTaskCompleted() is False, "Task should initially be incomplete"

        # Call doTask()
        task.doTask()

        # Verify status changed
        assert task.isTaskCompleted() is True, "Task should be completed after doTask()"
        assert task.completed is True, "Task.completed should be True after doTask()"

    def test_doTask_sets_completed_timestamp(self):
        """Verify that doTask() sets the completed_at timestamp."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Verify timestamp is initially None
        assert task.completed_at is None, "completed_at should be None before doTask()"

        # Call doTask()
        before_time = datetime.now()
        task.doTask()
        after_time = datetime.now()

        # Verify timestamp is set
        assert task.completed_at is not None, "completed_at should be set after doTask()"
        assert isinstance(task.completed_at, datetime), "completed_at should be a datetime object"
        assert before_time <= task.completed_at <= after_time, \
            "completed_at should be between before and after call time"

    def test_doTask_multiple_calls(self):
        """Verify that calling doTask() multiple times keeps task completed."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # First call to doTask()
        task.doTask()
        first_completion_time = task.completed_at

        assert task.isTaskCompleted() is True, "Task should be completed after first doTask()"

        # Second call to doTask()
        task.doTask()
        second_completion_time = task.completed_at

        # Task should still be completed
        assert task.isTaskCompleted() is True, "Task should remain completed after second doTask()"
        # Second completion time should be later or equal to first
        assert second_completion_time >= first_completion_time, \
            "Second completion time should be >= first completion time"

    def test_doTask_with_different_task_types(self):
        """Verify that doTask() works for all task types."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        task_codes = [0, 1, 2, 3]  # Walk, Feed, Nap, Vet
        task_names = ["Walk", "Feed", "Nap", "Vet"]

        for task_code, task_name in zip(task_codes, task_names):
            task = Task(pet=pet, taskCode=task_code)

            assert task.isTaskCompleted() is False, \
                f"{task_name} task should initially be incomplete"

            task.doTask()

            assert task.isTaskCompleted() is True, \
                f"{task_name} task should be completed after doTask()"

    def test_task_completion_flow(self):
        """Verify complete workflow: create task -> set duration -> do task -> verify."""
        owner = newOwner("John")
        pet = newPet("Fluffy", owner)
        task = Task(pet=pet, taskCode=0)  # Walk task

        # Setup phase
        task.setTaskDuration(30)
        assert task.getTaskDuration() == 30, "Duration should be set to 30"
        assert task.isTaskCompleted() is False, "Task should be incomplete initially"

        # Create scheduler
        scheduler = newScheduler(
            task,
            year=datetime.now().year,
            month=datetime.now().month,
            date=datetime.now().day,
            time="09:00"
        )
        assert scheduler.getTask() == task, "Scheduler should reference the task"

        # Execute task
        task.doTask()

        # Verify completion
        assert task.isTaskCompleted() is True, "Task should be completed"
        assert task.completed_at is not None, "Completion timestamp should be set"
        assert scheduler.getTask().isTaskCompleted() is True, \
            "Scheduler's referenced task should show as completed"

    def test_completed_attribute_vs_method(self):
        """Verify that completed attribute and isTaskCompleted() method are consistent."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Before doTask()
        assert task.completed is False, "completed attribute should be False"
        assert task.isTaskCompleted() is False, "isTaskCompleted() should return False"

        # After doTask()
        task.doTask()
        assert task.completed is True, "completed attribute should be True"
        assert task.isTaskCompleted() is True, "isTaskCompleted() should return True"


class TestPetTasks:
    """Test suite for Pet task management and counting."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_pet_initial_task_count_is_zero(self):
        """Verify that a newly created Pet has zero tasks."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        assert pet.getTaskCount() == 0, "New pet should have zero tasks"
        assert len(pet.getPetTaskList()) == 0, "Pet task list should be empty"

    def test_add_single_task_increases_count(self):
        """Verify that adding a single task increases task count to 1."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Add task
        result = pet.addPetTask(task)

        assert result is True, "addPetTask should return True"
        assert pet.getTaskCount() == 1, "Task count should be 1 after adding one task"
        assert len(pet.getPetTaskList()) == 1, "Pet task list should contain one task"
        assert pet.getPetTaskList()[0] == task, "Task list should contain the added task"

    def test_add_multiple_tasks_increases_count(self):
        """Verify that adding multiple tasks increases task count correctly."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Create and add 3 tasks
        task1 = Task(pet=pet, taskCode=0)  # Walk
        task2 = Task(pet=pet, taskCode=1)  # Feed
        task3 = Task(pet=pet, taskCode=2)  # Nap

        # Initial count
        assert pet.getTaskCount() == 0, "Initial task count should be 0"

        # Add first task
        pet.addPetTask(task1)
        assert pet.getTaskCount() == 1, "Task count should be 1 after adding first task"

        # Add second task
        pet.addPetTask(task2)
        assert pet.getTaskCount() == 2, "Task count should be 2 after adding second task"

        # Add third task
        pet.addPetTask(task3)
        assert pet.getTaskCount() == 3, "Task count should be 3 after adding third task"

    def test_add_tasks_maintains_task_list(self):
        """Verify that added tasks are maintained in the pet's task list."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Create tasks with different types
        tasks = [
            Task(pet=pet, taskCode=0),  # Walk
            Task(pet=pet, taskCode=1),  # Feed
            Task(pet=pet, taskCode=2),  # Nap
        ]

        # Add all tasks
        for task in tasks:
            pet.addPetTask(task)

        # Verify all tasks are in the list
        task_list = pet.getPetTaskList()
        assert len(task_list) == 3, "Task list should contain 3 tasks"
        for i, task in enumerate(tasks):
            assert task_list[i] == task, f"Task {i} should match added task"

    def test_add_multiple_different_task_types(self):
        """Verify task count increases for all task types."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        task_types = [0, 1, 2, 3]  # Walk, Feed, Nap, Vet
        task_names = ["Walk", "Feed", "Nap", "Vet"]

        for task_code, task_name in zip(task_types, task_names):
            task = Task(pet=pet, taskCode=task_code)
            result = pet.addPetTask(task)

            assert result is True, f"Adding {task_name} task should return True"
            assert pet.getTaskCount() == task_code + 1, \
                f"Task count should be {task_code + 1} after adding {task_name} task"

    def test_task_count_matches_task_list_length(self):
        """Verify that getTaskCount() matches the actual task list length."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        for i in range(5):
            task = Task(pet=pet, taskCode=i % 4)
            pet.addPetTask(task)

            count = pet.getTaskCount()
            list_length = len(pet.getPetTaskList())
            assert count == list_length, \
                f"Task count ({count}) should match task list length ({list_length})"

    def test_prevent_duplicate_task_addition(self):
        """Verify that adding the same task twice is prevented."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        # Add task first time
        result1 = pet.addPetTask(task)
        assert result1 is True, "First add should return True"
        assert pet.getTaskCount() == 1, "Task count should be 1"

        # Try to add same task again
        result2 = pet.addPetTask(task)
        assert result2 is False, "Duplicate add should return False"
        assert pet.getTaskCount() == 1, "Task count should still be 1 (no duplicate added)"

    def test_add_task_with_pending_and_completed(self):
        """Verify task count includes both pending and completed tasks."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Create multiple tasks
        tasks = [Task(pet=pet, taskCode=i % 4) for i in range(4)]

        # Add all tasks
        for task in tasks:
            pet.addPetTask(task)

        assert pet.getTaskCount() == 4, "Task count should be 4"
        assert pet.getPendingTaskCount() == 4, "All tasks should be pending"

        # Complete some tasks
        tasks[0].doTask()
        tasks[2].doTask()

        assert pet.getTaskCount() == 4, "Total task count should still be 4"
        assert pet.getCompletedTaskCount() == 2, "Completed task count should be 2"
        assert pet.getPendingTaskCount() == 2, "Pending task count should be 2"


class TestTaskInitialization:
    """Test suite for Task initialization and validation."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_task_requires_pet_and_taskcode(self):
        """Verify that Task requires pet and taskCode parameters."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        # Valid task creation
        task = Task(pet=pet, taskCode=0)
        assert task.pet == pet, "Task should store pet reference"
        assert task.taskCode == 0, "Task should store taskCode"

    def test_task_default_values(self):
        """Verify Task default attribute values."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=1)

        assert task.duration == 0, "Duration should default to 0"
        assert task.completed is False, "Completed should default to False"
        assert task.completed_at is None, "completed_at should default to None"
        assert isinstance(task.schedulerList, list), "schedulerList should be a list"
        assert len(task.schedulerList) == 0, "schedulerList should be empty initially"

    def test_invalid_taskcode_raises_error(self):
        """Verify that invalid taskCode raises ValueError."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)

        with pytest.raises(ValueError):
            Task(pet=pet, taskCode=999)  # Invalid taskCode

    def test_negative_duration_raises_error(self):
        """Verify that negative duration raises ValueError."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0)

        with pytest.raises(ValueError):
            task.setTaskDuration(-30)  # Negative duration


class TestChronologicalOrder:
    """Test suite verifying schedules and tasks come back in chronological order."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def _make_task(self, task_code=0, duration=30):
        """Create a pet + task with a positive duration, ready to be scheduled."""
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=task_code)
        task.setTaskDuration(duration)
        return task

    def test_schedules_sorted_by_time_within_same_day(self):
        """Schedules on one day should come back earliest-time-first."""
        task = self._make_task()
        # Add out of order: noon, morning, evening.
        s_noon = newScheduler(task, 2026, 7, 6, "12:00")
        s_morning = newScheduler(task, 2026, 7, 6, "09:00")
        s_evening = newScheduler(task, 2026, 7, 6, "17:30")

        ordered = sortSchedulesByTime([s_noon, s_morning, s_evening])

        assert [s.getTime() for s in ordered] == ["09:00", "12:00", "17:30"], \
            "Same-day schedules should be ordered by ascending time"

    def test_schedules_sorted_across_multiple_days(self):
        """Chronological order should span year, month, and day, not just time."""
        task = self._make_task()
        # Add newest first so a stable/no-op sort would fail the assertion.
        s_july = newScheduler(task, 2026, 7, 6, "08:00")
        s_dec = newScheduler(task, 2025, 12, 31, "23:00")
        s_jan = newScheduler(task, 2026, 1, 1, "06:00")

        ordered = sortSchedulesByTime([s_july, s_dec, s_jan])

        assert [s.getDateString() for s in ordered] == [
            "2025-12-31", "2026-01-01", "2026-07-06"
        ], "Schedules should be ordered chronologically across days/months/years"

    def test_schedules_sorted_numerically_not_lexically(self):
        """Times must sort as minutes, so 09:00 precedes 10:00 (not a string compare)."""
        task = self._make_task()
        s_ten = newScheduler(task, 2026, 7, 6, "10:00")
        s_nine = newScheduler(task, 2026, 7, 6, "09:00")

        ordered = sortSchedulesByTime([s_ten, s_nine])

        assert [s.getTime() for s in ordered] == ["09:00", "10:00"], \
            "09:00 should sort before 10:00"

    def test_schedules_descending_order(self):
        """descending=True should return most-recent-first (history view)."""
        task = self._make_task()
        s_morning = newScheduler(task, 2026, 7, 6, "09:00")
        s_evening = newScheduler(task, 2026, 7, 6, "17:30")

        ordered = sortSchedulesByTime([s_morning, s_evening], descending=True)

        assert [s.getTime() for s in ordered] == ["17:30", "09:00"], \
            "Descending sort should return latest schedule first"

    def test_sort_empty_schedule_list(self):
        """Sorting an empty list should return an empty list, not raise."""
        assert sortSchedulesByTime([]) == []

    def test_tasks_sorted_by_earliest_scheduled_time(self):
        """Tasks should be ordered by their earliest scheduled occurrence."""
        owner = newOwner("Owner")
        pet = newPet("Pet", owner)

        early_task = Task(pet=pet, taskCode=0)
        early_task.setTaskDuration(30)
        late_task = Task(pet=pet, taskCode=1)
        late_task.setTaskDuration(30)

        # late_task is scheduled later in the day than early_task.
        newScheduler(late_task, 2026, 7, 6, "15:00")
        newScheduler(early_task, 2026, 7, 6, "08:00")

        ordered = sortTasksByScheduledTime([late_task, early_task])

        assert ordered == [early_task, late_task], \
            "Tasks should be ordered by earliest scheduled time"

    def test_tasks_keyed_on_earliest_of_multiple_schedules(self):
        """A task with several schedules is ordered by its EARLIEST occurrence."""
        owner = newOwner("Owner")
        pet = newPet("Pet", owner)

        task_a = Task(pet=pet, taskCode=0)
        task_a.setTaskDuration(30)
        task_b = Task(pet=pet, taskCode=1)
        task_b.setTaskDuration(30)

        # task_a's earliest is 07:00 even though it also has a late slot.
        newScheduler(task_a, 2026, 7, 6, "20:00")
        newScheduler(task_a, 2026, 7, 6, "07:00")
        newScheduler(task_b, 2026, 7, 6, "09:00")

        ordered = sortTasksByScheduledTime([task_b, task_a])

        assert ordered == [task_a, task_b], \
            "Task should be ranked by its earliest schedule (07:00 < 09:00)"

    def test_unscheduled_tasks_sorted_last(self):
        """Tasks with no schedule are appended after scheduled ones, both directions."""
        owner = newOwner("Owner")
        pet = newPet("Pet", owner)

        scheduled = Task(pet=pet, taskCode=0)
        scheduled.setTaskDuration(30)
        newScheduler(scheduled, 2026, 7, 6, "09:00")

        unscheduled = Task(pet=pet, taskCode=1)  # never scheduled

        ascending = sortTasksByScheduledTime([unscheduled, scheduled])
        assert ascending == [scheduled, unscheduled], \
            "Unscheduled task should come last in ascending order"

        descending = sortTasksByScheduledTime([unscheduled, scheduled], descending=True)
        assert descending[-1] == unscheduled, \
            "Unscheduled task should still come last in descending order"


class TestDailyRecurrence:
    """Test suite for daily recurring tasks: completing one spawns the next day's."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def _make_daily_task(self, year=2026, month=7, date=6, time="09:00", duration=30):
        """Create a pet with a scheduled daily task ready to complete."""
        owner = newOwner("Owner")
        pet = newPet("Pet", owner)
        task = Task(pet=pet, taskCode=0, duration=duration, isDaily=True)
        pet.addPetTask(task)
        newScheduler(task, year, month, date, time)
        return pet, task

    def test_completing_daily_task_returns_new_task(self):
        """doTask() on a daily task returns the freshly spawned next occurrence."""
        pet, task = self._make_daily_task()

        next_task = task.doTask()

        assert next_task is not None, "Completing a daily task should return a new Task"
        assert isinstance(next_task, Task), "Spawned occurrence should be a Task"
        assert next_task is not task, "Spawned occurrence should be a distinct object"

    def test_new_task_scheduled_for_following_day(self):
        """The spawned task is scheduled one calendar day later at the same time."""
        pet, task = self._make_daily_task(2026, 7, 6, "09:00")

        next_task = task.doTask()
        schedules = next_task.getSchedulerList()

        assert len(schedules) == 1, "Spawned task should have exactly one schedule"
        sched = schedules[0]
        assert (sched.year, sched.month, sched.date) == (2026, 7, 7), \
            "Spawned schedule should be the following day"
        assert sched.getTime() == "09:00", "Spawned schedule should keep the same time"

    def test_new_task_added_to_pet_and_pending(self):
        """The next occurrence is attached to the pet and starts incomplete."""
        pet, task = self._make_daily_task()

        next_task = task.doTask()

        assert next_task in pet.getPetTaskList(), \
            "Spawned task should be added to the pet's task list"
        assert next_task.isTaskCompleted() is False, \
            "Spawned task should start as pending"
        assert pet.getTaskCount() == 2, "Pet should now have original + spawned task"

    def test_new_task_inherits_attributes(self):
        """The spawned task copies type, duration, priority, and daily flag."""
        pet, task = self._make_daily_task(duration=45)

        next_task = task.doTask()

        assert next_task.getTaskCode() == task.getTaskCode(), "Task type should carry over"
        assert next_task.getTaskDuration() == task.getTaskDuration(), \
            "Duration should carry over"
        assert next_task.getPriority() == task.getPriority(), "Priority should carry over"
        assert next_task.isDailyTask() is True, "Spawned task should remain daily"

    def test_non_daily_task_does_not_spawn(self):
        """Completing a one-off task returns None and adds no new task."""
        owner = newOwner("Owner")
        pet = newPet("Pet", owner)
        task = Task(pet=pet, taskCode=0, duration=30, isDaily=False)
        pet.addPetTask(task)
        newScheduler(task, 2026, 7, 6, "09:00")

        result = task.doTask()

        assert result is None, "A non-daily task should not spawn a new occurrence"
        assert pet.getTaskCount() == 1, "No extra task should be created"

    def test_completing_twice_does_not_spawn_duplicate(self):
        """The 'first completion' guard stops a second doTask() from spawning again."""
        pet, task = self._make_daily_task()

        first = task.doTask()
        second = task.doTask()

        assert first is not None, "First completion should spawn a task"
        assert second is None, "Second completion should not spawn a duplicate"
        assert pet.getTaskCount() == 2, \
            "Only one occurrence should be spawned despite two doTask() calls"

    def test_recurrence_rolls_over_month_boundary(self):
        """Completing a daily task on the last of the month rolls to the 1st of the next."""
        pet, task = self._make_daily_task(2026, 7, 31, "08:00")

        next_task = task.doTask()
        sched = next_task.getSchedulerList()[0]

        assert (sched.year, sched.month, sched.date) == (2026, 8, 1), \
            "July 31 daily task should roll over to August 1"

    def test_recurrence_chains_forward(self):
        """Completing each spawned occurrence keeps rolling the routine forward."""
        pet, task = self._make_daily_task(2026, 7, 6, "09:00")

        day2 = task.doTask()
        day3 = day2.doTask()
        sched = day3.getSchedulerList()[0]

        assert (sched.year, sched.month, sched.date) == (2026, 7, 8), \
            "Chained completions should advance the schedule one day at a time"
        assert pet.getTaskCount() == 3, "Each completion should add one occurrence"


class TestDuplicateTimeDetection:
    """Test suite for the Scheduler's duplicate/conflicting time flagging."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def _make_task(self, task_code=0, duration=30, pet_name="Pet"):
        """Create a pet + scheduled-ready task."""
        owner = newOwner("Owner")
        pet = newPet(pet_name, owner)
        task = Task(pet=pet, taskCode=task_code, duration=duration)
        pet.addPetTask(task)
        return task

    def test_free_slot_returns_no_warning(self):
        """An empty slot should not be flagged as a conflict."""
        assert checkScheduleConflict(2026, 7, 6, "09:00") is None, \
            "A date/time with no bookings should return None"

    def test_duplicate_time_is_flagged(self):
        """A second booking at the same date and time should be flagged."""
        task = self._make_task()
        newScheduler(task, 2026, 7, 6, "09:00")

        warning = checkScheduleConflict(2026, 7, 6, "09:00")

        assert warning is not None, "Duplicate date+time should produce a warning"
        assert "conflict" in warning.lower(), "Warning should mention a conflict"

    def test_duplicate_time_flags_across_different_pets(self):
        """A clash between two different pets at the same slot is still flagged."""
        task_a = self._make_task(pet_name="Rex")
        newScheduler(task_a, 2026, 7, 6, "09:00")

        task_b = self._make_task(pet_name="Milo")
        warning = checkScheduleConflict(2026, 7, 6, "09:00")

        assert warning is not None, "Overlapping slot for another pet should be flagged"
        assert "Rex" in warning, "Warning should name the already-booked pet"

    def test_different_time_same_day_not_flagged(self):
        """Different times on the same day should not conflict."""
        task = self._make_task()
        newScheduler(task, 2026, 7, 6, "09:00")

        assert checkScheduleConflict(2026, 7, 6, "10:30") is None, \
            "A different time on the same day should not be flagged"

    def test_same_time_different_day_not_flagged(self):
        """The same time on a different day should not conflict."""
        task = self._make_task()
        newScheduler(task, 2026, 7, 6, "09:00")

        assert checkScheduleConflict(2026, 7, 7, "09:00") is None, \
            "The same time on a different day should not be flagged"

    def test_ignore_excludes_self_from_conflict(self):
        """A scheduler should not report a conflict with itself via ignore."""
        task = self._make_task()
        sched = newScheduler(task, 2026, 7, 6, "09:00")

        # Only this one scheduler exists, so ignoring it clears the slot.
        assert checkScheduleConflict(2026, 7, 6, "09:00", ignore=sched) is None, \
            "Ignoring the only booking should report no conflict"

    def test_newScheduler_prints_warning_on_duplicate(self, capsys):
        """Creating a second schedule at a taken slot prints a non-fatal warning."""
        task = self._make_task()
        newScheduler(task, 2026, 7, 6, "09:00")
        capsys.readouterr()  # clear any output from the first (conflict-free) create

        second = newScheduler(task, 2026, 7, 6, "09:00")
        captured = capsys.readouterr()

        assert "conflict" in captured.out.lower(), \
            "newScheduler should print a conflict warning for a duplicate slot"
        # Non-fatal: the schedule is still created despite the clash.
        assert second in schedulerDictionary["20260706"], \
            "The duplicate schedule should still be created (warning is non-fatal)"


class TestOverlapDetection:
    """Test suite for duration-aware overlap detection (detectConflicts/hasConflicts)."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def _schedule(self, year, month, date, time, duration=30,
                  task_code=0, pet_name="Pet"):
        """Create a scheduled task and return its Scheduler."""
        owner = newOwner("Owner")
        pet = newPet(pet_name, owner)
        task = Task(pet=pet, taskCode=task_code, duration=duration)
        pet.addPetTask(task)
        return newScheduler(task, year, month, date, time)

    def test_overlapping_intervals_are_detected(self):
        """A 60-min task at 09:00 overlaps a task starting at 09:30."""
        s1 = self._schedule(2026, 7, 6, "09:00", duration=60, pet_name="Rex")
        s2 = self._schedule(2026, 7, 6, "09:30", duration=30, pet_name="Milo")

        conflicts = detectConflicts([s1, s2])

        assert len(conflicts) == 1, "Overlapping intervals should produce one conflict"
        pair = conflicts[0]
        assert s1 in pair and s2 in pair, "Conflict should reference both schedules"
        assert hasConflicts([s1, s2]) is True, "hasConflicts should report True"

    def test_non_overlapping_intervals_have_no_conflict(self):
        """Back-to-back tasks with a gap should not conflict."""
        s1 = self._schedule(2026, 7, 6, "09:00", duration=30, pet_name="Rex")
        s2 = self._schedule(2026, 7, 6, "10:00", duration=30, pet_name="Milo")

        assert detectConflicts([s1, s2]) == [], "Separated intervals should not conflict"
        assert hasConflicts([s1, s2]) is False, "hasConflicts should report False"

    def test_adjacent_intervals_do_not_conflict(self):
        """When one task ends exactly as the next begins, there is no overlap."""
        s1 = self._schedule(2026, 7, 6, "09:00", duration=60, pet_name="Rex")  # ends 10:00
        s2 = self._schedule(2026, 7, 6, "10:00", duration=30, pet_name="Milo")  # starts 10:00

        assert detectConflicts([s1, s2]) == [], \
            "Touching-but-not-overlapping intervals should not conflict"

    def test_conflicts_only_within_same_day(self):
        """Identical times on different days must not be treated as overlapping."""
        s1 = self._schedule(2026, 7, 6, "09:00", duration=60, pet_name="Rex")
        s2 = self._schedule(2026, 7, 7, "09:00", duration=60, pet_name="Milo")

        assert detectConflicts([s1, s2]) == [], \
            "Overlap check must be scoped to a single calendar day"

    def test_multiple_overlaps_all_reported(self):
        """Three mutually overlapping tasks should yield all three pair conflicts."""
        s1 = self._schedule(2026, 7, 6, "09:00", duration=90, pet_name="A")  # 09:00-10:30
        s2 = self._schedule(2026, 7, 6, "09:30", duration=60, pet_name="B")  # 09:30-10:30
        s3 = self._schedule(2026, 7, 6, "10:00", duration=30, pet_name="C")  # 10:00-10:30

        conflicts = detectConflicts([s1, s2, s3])

        # Pairs: (s1,s2), (s1,s3), (s2,s3)
        assert len(conflicts) == 3, "All three overlapping pairs should be reported"

    def test_zero_duration_task_never_overlaps(self):
        """A zero-length task shares no interval, so it cannot overlap another."""
        # Build the zero-duration schedule directly (setTaskDuration rejects 0).
        owner = newOwner("Owner")
        pet = newPet("Rex", owner)
        zero_task = Task(pet=pet, taskCode=0)  # duration defaults to 0
        pet.addPetTask(zero_task)
        s_zero = newScheduler(zero_task, 2026, 7, 6, "09:00")

        s_other = self._schedule(2026, 7, 6, "09:00", duration=60, pet_name="Milo")

        assert (s_zero, s_other) not in detectConflicts([s_zero, s_other]) and \
               (s_other, s_zero) not in detectConflicts([s_zero, s_other]), \
            "A zero-duration task should not register as an overlap"

    def test_empty_and_single_schedule_have_no_conflicts(self):
        """Degenerate inputs should return no conflicts, not raise."""
        assert detectConflicts([]) == [], "Empty input should yield no conflicts"
        s1 = self._schedule(2026, 7, 6, "09:00")
        assert detectConflicts([s1]) == [], "A single schedule cannot conflict"


class TestGlobalLookupAndCleanup:
    """Test global registry lookups, cleanup, and convenience helpers."""

    def setup_method(self):
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_remove_pet_cascades_tasks_and_scheduler_cleanup(self):
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0, duration=30)
        pet.addPetTask(task)
        sched = newScheduler(task, 2026, 7, 6, "09:00")

        assert sched in schedulerDictionary["20260706"]
        assert task in pet.getPetTaskList()

        assert removePet(pet) is True

        assert pet not in owner.getPetList(), "Removed pet should no longer belong to owner"
        assert pet not in petList, "Removed pet should no longer be in global pet list"
        assert "20260706" not in schedulerDictionary, "Scheduler for removed pet should be cleaned up"
        assert task.getSchedulerList() == [], "Task schedulers should be removed when pet is removed"

    def test_remove_owner_cascades_pet_and_schedule_cleanup(self):
        owner = newOwner("Test Owner")
        pet = newPet("Test Pet", owner)
        task = Task(pet=pet, taskCode=0, duration=30)
        pet.addPetTask(task)
        newScheduler(task, 2026, 7, 6, "09:00")

        assert removeOwner(owner) is True
        assert owner not in ownerList, "Removed owner should not remain in global owner list"
        assert pet not in petList, "Pets for removed owner should also be removed"
        assert schedulerDictionary == {}, "Schedulers for removed owner should be removed"

    def test_clear_all_data_returns_owner_count_and_clears_state(self):
        owner = newOwner("Test Owner")
        newPet("Pet A", owner)
        newPet("Pet B", owner)

        assert clearAllData() == 1
        assert ownerList == []
        assert petList == []
        assert schedulerDictionary == {}

    def test_clear_all_data_clears_indexes_and_scheduler_state(self):
        owner = newOwner("Index Owner")
        pet = newPet("Index Pet", owner)
        task = Task(pet=pet, taskCode=0, duration=30)
        pet.addPetTask(task)
        newScheduler(task, 2026, 7, 6, "09:00")

        assert getOwnerByName("Index Owner") == owner
        assert getPetByName("Index Pet") == pet
        assert getSchedulerByKey("20260706") != []

        assert clearAllData() == 1

        assert getOwnerByName("Index Owner") is None
        assert getPetByName("Index Pet") is None
        assert getSchedulerByKey("20260706") == []
        assert schedulerDictionary == {}

    def test_get_scheduler_by_key_returns_empty_after_clear_all_data(self):
        owner = newOwner("Cleaner")
        pet = newPet("Paws", owner)
        task = Task(pet=pet, taskCode=1, duration=20)
        pet.addPetTask(task)
        newScheduler(task, 2026, 7, 7, "10:00")

        assert getSchedulerByKey("20260707") != []
        assert clearAllData() == 1
        assert getSchedulerByKey("20260707") == []

    def test_get_owner_and_pet_lookup_is_case_insensitive(self):
        owner = newOwner("Jane Doe")
        pet = newPet("Mochi", owner)

        assert getOwnerByName("jane doe") == owner
        assert getPetByName("mochi") == pet

    def test_get_pets_by_owner_and_task_type_convenience(self):
        owner = newOwner("Jane Doe")
        pet1 = newPet("Mochi", owner)
        pet2 = newPet("Buddy", owner)
        task1 = Task(pet=pet1, taskCode=0, duration=30)
        task2 = Task(pet=pet2, taskCode=1, duration=15)
        pet1.addPetTask(task1)
        pet2.addPetTask(task2)

        assert getPetsByOwner(owner) == [pet1, pet2]
        assert getPetsByTaskType(0) == [pet1]
        assert getPetsByTaskType(1) == [pet2]

    def test_pending_and_no_task_filters(self):
        owner = newOwner("Jane Doe")
        pet1 = newPet("Mochi", owner)
        pet2 = newPet("Buddy", owner)
        task = Task(pet=pet1, taskCode=0, duration=30)
        pet1.addPetTask(task)

        assert getPetsWithPendingTasks() == [pet1]
        assert getPetsWithNoTasks() == [pet2]

    def test_get_pet_statistics_returns_expected_counts(self):
        owner = newOwner("Jane Doe")
        pet = newPet("Mochi", owner)
        task = Task(pet=pet, taskCode=0, duration=30)
        pet.addPetTask(task)
        newScheduler(task, 2026, 7, 6, "09:00")

        stats = getPetStatistics()
        assert stats['total_pets'] == 1
        assert stats['total_tasks'] == 1
        assert stats['total_schedules'] == 1


class TestValidationAndPlanning:
    """Test validation paths, recurring scheduling, and day-planning helpers."""

    def setup_method(self):
        clearAllData()
        ownerList.clear()
        petList.clear()
        schedulerDictionary.clear()

    def test_schedule_recurring_rejects_bad_arguments(self):
        owner = newOwner("Jane Doe")
        pet = newPet("Mochi", owner)
        task = Task(pet=pet, taskCode=0, duration=30)
        pet.addPetTask(task)

        with pytest.raises(ValueError):
            scheduleRecurring(task, 2026, 7, 6, "09:00", occurrences=0)

        with pytest.raises(ValueError):
            scheduleRecurring(task, 2026, 7, 6, "09:00", occurrences=3, interval_days=0)

    def test_build_day_plan_returns_unplaced_when_tasks_exceed_day(self):
        owner = newOwner("Jane Doe")
        pet = newPet("Mochi", owner)
        tasks = [Task(pet=pet, taskCode=0, duration=300), Task(pet=pet, taskCode=1, duration=300), Task(pet=pet, taskCode=2, duration=300)]
        for task in tasks:
            pet.addPetTask(task)

        plan = buildDayPlan(tasks, day_start="08:00", day_end="12:00")

        assert plan['total_minutes'] == 0
        assert len(plan['planned']) == 0
        assert len(plan['unplaced']) == 3

    def test_build_day_plan_ignores_zero_duration_tasks(self):
        owner = newOwner("Jane Doe")
        pet = newPet("Mochi", owner)
        zero_task = Task(pet=pet, taskCode=0)  # duration 0
        pet.addPetTask(zero_task)

        plan = buildDayPlan([zero_task])

        assert plan['planned'] == []
        assert plan['unplaced'] == [zero_task]

    def test_get_free_slots_and_find_free_slot_account_for_booked_times(self):
        owner = newOwner("Jane Doe")
        pet = newPet("Mochi", owner)
        task1 = Task(pet=pet, taskCode=0, duration=60)
        task2 = Task(pet=pet, taskCode=1, duration=30)
        pet.addPetTask(task1)
        pet.addPetTask(task2)
        s1 = newScheduler(task1, 2026, 7, 6, "09:00")
        s2 = newScheduler(task2, 2026, 7, 6, "10:00")

        slots = getFreeSlots([s1, s2], day_start="08:00", day_end="12:00")
        assert slots[0] == ("08:00", "09:00")
        assert slots[1] == ("10:30", "12:00")
        assert findFreeSlot([s1, s2], 45, day_start="08:00", day_end="12:00") == "08:00"
        assert findFreeSlot([s1, s2], 120, day_start="08:00", day_end="12:00") is None

    def test_is_date_overbooked_returns_true_when_above_budget(self):
        owner = newOwner("Jane Doe")
        pet = newPet("Mochi", owner)
        task = Task(pet=pet, taskCode=0, duration=500)
        pet.addPetTask(task)
        newScheduler(task, 2026, 7, 6, "09:00")

        assert isDateOverbooked(2026, 7, 6, budget_minutes=480) is True
        assert isDateOverbooked(2026, 7, 6, budget_minutes=600) is False

    def test_get_scheduler_by_key_returns_empty_for_missing_key(self):
        assert getSchedulerByKey("19990101") == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
