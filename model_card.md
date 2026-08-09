# Reflection and Ethics: Thinking Critically About Your AI

## What are the limitations or biases in your system?

### Natural language parsing is narrow
- The command parser only recognizes a limited set of task verbs (feed, walk, nap, vet, etc.).
- It supports only specific date/time patterns and month-word forms, so more casual phrasing like tomorrow, next Monday, or 6pm is rejected.

### Month-word support is limited
- It handles English month names and abbreviations only.
- It does not support misspellings like Feber, and it only accepts a small set of date layouts.

### Time validation is strict

- Scheduled commands require numeric HH:MM format if a date is included.
- That means user-friendly times like 6pm or 18 are treated as invalid.

### Command ambiguity

- The parser uses keyword matching and simple pet-name lookup, so ambiguous phrases or overlapping names may behave unpredictably.
- It also assumes pet and owner names appear clearly in the command.

### Bias toward the tested command forms

- The system is most reliable for the variants covered by tests.
- Unseen command forms or workflows outside the current test patterns are less reliable.

### No broader NLP understanding

- This is not a full conversational assistant; it is a pattern-based parser.
- It cannot infer intent beyond the defined command templates.

## Could your AI be misused, and how would you prevent that?

The current command parser is not a general AI agent — it is a pattern-based parser for a small set of pet-care commands. That means:

- It is unlikely to be misused for security exploits in its current form, because it does not execute arbitrary code.
- The main risk is misuse as bad input: users can submit unsupported or ambiguous commands and cause confusion, failed responses, or incorrect task creation.

### How to prevent misuse
- Restrict accepted commands to explicit patterns only.
- Validate every parsed field:
    - require supported task verbs,
    - require HH:MM time for scheduled dates,
    - require valid owner/pet names,
    - reject unknown month words.
- Avoid evaluating user text or using eval/dynamic code paths.
- Provide clear error feedback when a command is not recognized.
- Log or reject ambiguous commands rather than guessing.
- If this ever becomes exposed beyond a controlled Streamlit UI, add input sanitization and command whitelisting as a hard guard.

So the safest design is: treat the parser as a command validator, not a free-form conversational assistant.

## What surprised you while testing your AI's reliability?

- The AI produced useful parser code and test cases very quickly, which sped up iteration far more than I expected.
- Small regex tweaks had outsized effects — a single pattern change fixed many failing cases, showing the parser is surprisingly sensitive.
- The parser initially missed obvious human forms (day-suffixes like “25th”, day-first order, and misspellings like “Feber”); tests quickly exposed those blind spots.
- I was surprised that time handling required explicit design choices: “time only” should create a task (no schedule), while a date without numeric HH:MM must be rejected.

## Describe your collaboration with AI during this project. Identify one instance when the AI gave a helpful suggestion and one instance where its suggestion was flawed or incorrect.

**Workflow:** I iterated with the AI to design parser changes, write regexes, and generate unit tests. The AI suggested test-driven ideas and code snippets; I ran the tests, inspected failures, and guided refinements until the parser and tests matched the desired behavior.

**Helpful suggestion:** The AI recommended using parameterized/property-style tests and a unified month-word parsing approach (a single regex family handling full and abbreviated month names in both month-first and day-first orders). Implementing that pattern made it easy to cover many edge cases (day suffixes, both date orders) with concise tests and revealed brittle spots quickly.

**Flawed suggestion:** Early on the AI suggested accepting permissive time formats like `6pm` and auto-creating schedules when a date was present but time was missing. That led to ambiguous behavior and failing tests; we resolved this by enforcing numeric `HH:MM` for scheduled dates and treating "time-only" commands as unscheduled tasks.

These examples show how the AI accelerated iteration (fast code + tests) while still requiring human judgment to set safe, unambiguous policies for parsing and scheduling.

