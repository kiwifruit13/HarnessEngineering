---
name: planning-with-files
description: File-based planning for complex tasks using persistent markdown files. Creates task_plan.md for phase tracking, findings.md for research discoveries, and progress.md for session logging. Ideal for multi-step tasks, research projects, or any task requiring >5 tool calls.
---

# Planning with Files

Work like Manus: Use persistent markdown files as your "working memory on disk."

## Task Goal
- **Purpose**: Provide a systematic approach to complex task management using three persistent markdown files
- **Capabilities**: Phase tracking, discovery logging, session recording, error tracking, and intelligent session recovery
- **Trigger Condition**: When working on complex multi-step tasks, research projects, or any task requiring more than 5 tool calls

## Quick Start

When starting ANY complex task:

1. **Run session recovery** - Execute `python3 <skill-path>/scripts/session-recover.py` to automatically analyze existing planning files
2. **Create planning files if new** - Use [assets/templates/task_plan.md](assets/templates/task_plan.md), [assets/templates/findings.md](assets/templates/findings.md), and [assets/templates/progress.md](assets/templates/progress.md) as references
3. **Or use initialization script (optional)** - Run `bash <skill-path>/scripts/init-session.sh [project-name]` from your project directory
4. **Follow the critical rules** - Adhere to the rules below throughout the task
5. **Update files regularly** - Update planning files after each phase completion and any significant discovery

> **Important**: Planning files should be created in your project directory (current working directory), not in the skill installation directory.

## The Core Pattern

```
Context Window = RAM (volatile, limited)
Filesystem = Disk (persistent, unlimited)

→ Anything important gets written to disk.
```

## File Purposes

| File | Purpose | When to Update |
|------|---------|----------------|
| `task_plan.md` | Track phases, progress, decisions, and errors | After each phase completion or decision |
| `findings.md` | Store research discoveries, technical decisions, and key information | After ANY discovery or research |
| `progress.md` | Log session activities, test results, and chronological progress | Throughout the session, especially after errors |

## Critical Rules

### 1. Create Plan First
Never start a complex task without creating `task_plan.md`. This is non-negotiable.

### 2. The 2-Action Rule
> "After every 2 view/browser/search operations, IMMEDIATELY save key findings to text files."

This prevents visual and multimodal information from being lost when the context window resets or fills up.

### 3. Read Before Decide
Before making major decisions, re-read `task_plan.md`. This keeps your goals and current phase fresh in the attention window.

### 4. Update After Act
After completing any phase:
- Mark phase status: `in_progress` → `complete`
- Log any errors encountered
- Note files created or modified
- Update the current phase indicator

### 5. Log ALL Errors
Every error must be recorded in `task_plan.md`. This builds knowledge and prevents repetition.

Example error log format:
```markdown
## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| FileNotFoundError | 1 | Created default config |
| API timeout | 2 | Added retry logic |
```

### 6. Never Repeat Failures
```
if action_failed:
    next_action != same_action
```
Track what you tried and mutate your approach.

## The 3-Strike Error Protocol

When encountering persistent errors:

```
ATTEMPT 1: Diagnose & Fix
  → Read the error carefully
  → Identify the root cause
  → Apply a targeted fix

ATTEMPT 2: Alternative Approach
  → Same error? Try a different method
  → Use a different tool or library?
  → NEVER repeat the exact same failing action

ATTEMPT 3: Broader Rethink
  → Question your assumptions
  → Search for solutions
  → Consider updating the plan

AFTER 3 FAILURES: Escalate to User
  → Explain what you tried
  → Share the specific error
  → Ask for guidance
```

## Read vs Write Decision Matrix

| Situation | Action | Reason |
|-----------|--------|--------|
| Just wrote a file | DON'T read immediately | Content is still in context |
| Viewed image/PDF | Write findings NOW | Multimodal content must be captured as text before it's lost |
| Browser returned data | Write to file | Screenshots don't persist in context |
| Starting new phase | Read plan/findings | Re-orient if context has become stale |
| Error occurred | Read relevant file | Need current state to diagnose the issue |
| Resuming after gap | Read all planning files | Recover the complete state |

## The 5-Question Reboot Test

If you can answer these questions, your context management is solid:

| Question | Answer Source |
|----------|---------------|
| Where am I? | Current phase in task_plan.md |
| Where am I going? | Remaining phases listed in task_plan.md |
| What's the goal? | Goal statement in task_plan.md |
| What have I learned? | findings.md |
| What have I done? | progress.md |

## Session Recovery

When starting work on an existing project or after a context reset:

1. **Run session recovery script** - Execute `python3 <skill-path>/scripts/session-recover.py` for automatic analysis
2. **Review the recovery report** - The script provides:
   - Goal and current phase
   - Progress percentage with visualization
   - Key decisions and findings
   - Next steps recommendations
3. **Update if needed** - Sync planning files with recent progress
4. **Continue from where you left off** - Resume work from the current phase

**Benefits of automatic recovery:**
- Instant context restoration without manual file reading
- Progress visualization with percentage tracking
- Intelligent next steps recommendations
- Compliance checklist validation

## When to Use This Pattern

**Use for:**
- Multi-step tasks (3+ steps)
- Research projects
- Building or creating complex projects
- Tasks spanning many tool calls
- Anything requiring organization and tracking
- Tasks that might be interrupted or resumed later

**Skip for:**
- Simple questions
- Single-file edits
- Quick lookups or fact retrieval
- Tasks that can be completed in one response

## Resource Index

- **Templates**: See [assets/templates/](assets/templates/) for all three planning file templates
  - [task_plan.md](assets/templates/task_plan.md) - Master plan with phases and progress tracking
  - [findings.md](assets/templates/findings.md) - Research discoveries and technical decisions
  - [progress.md](assets/templates/progress.md) - Session log and test results
- **Examples**: See [references/examples.md](references/examples.md) for real-world usage scenarios
- **Principles**: See [references/manus-principles.md](references/manus-principles.md) for the underlying context engineering principles from Manus

## Operation Steps

### Standard Workflow

1. **Initial Setup**
   - Run `session-recover.py` to check for existing planning files
   - If files exist, review the recovery report
   - If no files, create them using templates or init script

2. **Execution Loop**
   - Before major decisions: Read `task_plan.md` to refresh goals
   - During work: Update `progress.md` with actions taken
   - After discoveries: Update `findings.md` with key findings
   - After every 2 view/browser operations: Apply 2-Action Rule
   - After phase completion: Update `task_plan.md` status

3. **Error Handling**
   - Log all errors in `task_plan.md`
   - Follow 3-Strike Error Protocol
   - Never repeat the same failing action

4. **Completion**
   - Verify all phases are marked complete
   - Review deliverables
   - Update final status in planning files

### Optional Branches

- **When starting new project**: Use `init-session.sh` for quick setup
- **When resuming work**: Run `session-recover.py` for intelligent context recovery
- **When validating compliance**: Run `validate-rules.py` to check rule adherence
- **When generating report**: Run `generate-report.py` for comprehensive progress summary

## Automated Scripts

### Session Recovery (Recommended)
```bash
python3 <skill-path>/scripts/session-recover.py [project-directory]
```

Automatically analyzes planning files and generates:
- Context summary with goal and current phase
- Progress percentage with visualization
- Key decisions and findings
- Next steps recommendations
- Compliance checklist

**When to use:**
- At the start of any session
- After context reset or interruption
- When resuming work after a break

### Rules Validation
```bash
python3 <skill-path>/scripts/validate-rules.py [project-directory]
```

Validates compliance with planning-with-files rules:
- File existence and structure
- Rule adherence (2-Action Rule, phase tracking)
- Error logging completeness
- Provides improvement suggestions

**When to use:**
- Periodically during long tasks
- Before major milestones
- When encountering issues
- For quality assurance

### Progress Report Generation
```bash
python3 <skill-path>/scripts/generate-report.py [project-directory] [output-file.md]
```

Generates comprehensive progress report:
- Visual progress bar and statistics
- Phase breakdown with status
- Key findings and decisions summary
- Error log and resolution status
- Recommendations

**When to use:**
- At project milestones
- Before delivering to user
- For progress review meetings
- For documentation purposes

### Initialization Script (Optional)
```bash
bash <skill-path>/scripts/init-session.sh [project-name]
```

Quickly creates all three planning files in your current directory if they don't already exist.

## Best Practices

### Regular Use
1. **Start every session** with `session-recover.py`
2. **Validate rules** periodically with `validate-rules.py`
3. **Generate reports** at milestones with `generate-report.py`
4. **Update files** consistently throughout the task

### Error Prevention
1. Always apply the 2-Action Rule
2. Never repeat the same failing action
3. Log all errors immediately
4. Read plan before major decisions

### Efficiency Tips
1. Use `session-recover.py` instead of manually reading all files
2. Run `validate-rules.py` to catch compliance issues early
3. Generate reports for quick status overviews
4. Keep planning files concise and focused

## Notes

- Planning files go in your project directory (current working directory), not in the skill installation directory
- The 2-Action Rule prevents visual and multimodal information from being lost when context resets
- Re-read `task_plan.md` before major decisions to keep goals in attention
- Log ALL errors - they help avoid repetition and build knowledge
- Never repeat a failed action - mutate your approach instead
- Use automated scripts to enhance efficiency and accuracy
- This pattern works across all AI agents that support file-based workflows
- The key is agent discipline: actively following the rules, not relying on automatic triggers
