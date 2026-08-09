# Show What You Know: Applied AI System Project

I am expanding on Week 4 project **PawPal+**. This Streamlit app helps a pet owner plan care tasks for their pet.

## Title and Summary

The upgraded **PawPal+** includes multiple enhancements to make the system easier to use. A new input interface is implemented so user can write "add owner Jordan" instead of entering form data. The following is a list of the new enhancements:

- Added a text input widget and button to process inputed text.
- Add support for removing/deleting owner, pet, and tasks.
- Allow for case insensitive matching of commands, owner names, and pet names.
- Allow walk command in text input to do same task as walk pet.
- Allow feed command in text input to do same task as feed pet.
- Allow scheduler month to include month words in full and shorthand mode (April, Apr).
- Update tests to include new functionality covering natural language commands.
- Add test edge cases for scheduler date and time inputs.


## Architecture Overview

**System Diagram Summary**
The diagram shows a simple object model for **PawPal+**:

- Owner owns one or more Pet objects.
- Each Pet contains multiple Task items.
- Each Task can have one or more Scheduler entries for planned dates/times.
- Scheduler points back to its Task, and through the task to the pet.

**A module-level SchedulingModule manages the collections and operations:**
- creates owners, pets, and schedules
- looks up pets and owners
- builds day plans
- detects conflicts
- sorts and filters schedules/tasks

The core flow is:
`Owner -> Pet -> Task -> Scheduler`, with the scheduling module coordinating creation and validation.

## Setup Instructions
Steps to setup and run enhanced **PawPal+**:
1. Clone github project: `https://github.com/ric3babi-sys/applied-ai-system-project.git`
2. Change directory to where you cloned the project.
3. Create and activate the virtual environment:
    - ```bash
      python -m venv .venv
      ```
    - ```bash source .venv/bin/activate```
4. Install the requirements:
    - ```bash pip install -r requirements.txt```
5. Launch the Streamlit app:
    - ```bash python -m streamlit run app.py```
6. Open the browser when Streamlit gives you the local URL, usually:
    - `http://localhost:8501`


## Sample Interactions
Enter each command separately then click the `Execute command` button:
```bash
add owner Jordan
```
```bash
add pet Mochi for Jordan
```
```bash
feed Mochi on 2026-08-25 at 18:00   # adjust date accordingly
```
This will create owner named Jordan. A pet named Mochi is created with Jordan assigned as it's owner. A task is then scheduled to `feed Mochi` at entered date and time.

## Design Decisions
I designed a natural language interface to make it easier for user to describe what available tasks to schedule for their pet. I was constrained on how many tasks to provide due to time limits. Adding more tasks require planning because there could by specific parameters exclusive to new tasks.

## Testing Summary
All tests for new functionality passed. Coverage included test cases for parsing natural language into commands that created owner, pet, and task scheduling. Initially tests missed cases for full word months and abbreviations. This was corrected.

## Reflection
I was pleasantly surprised with how capable AI is in generating code and comments. With detailed prompts and examples, AI was able to infer and understand the task assigned. The code produced can be bloated and room for optimization is there. On another note, it scares me how fast AI learned to code. The future is both exciting and a little scary.

## Reliability and Evaluation: How You Test and Improve Your AI
For reliability details and confidence analysis, see `Reliability.txt`.

