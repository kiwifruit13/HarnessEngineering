#!/usr/bin/env python3
"""
Rules Validation Script for planning-with-files

Validates compliance with planning-with-files rules and best practices.
Checks for proper file usage, rule adherence, and provides improvement suggestions.

Usage: python3 validate-rules.py [project-directory]
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


def read_markdown_file(filepath: Path) -> str:
    """Read a markdown file and return its content."""
    if not filepath.exists():
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def validate_file_existence(project_dir: Path) -> Dict[str, bool]:
    """Check if all planning files exist."""
    files = ["task_plan.md", "findings.md", "progress.md"]
    return {f: (project_dir / f).exists() for f in files}


def validate_task_plan(content: str) -> List[Dict]:
    """Validate task_plan.md structure and content."""
    issues = []

    if not content:
        issues.append({
            "severity": "critical",
            "category": "missing-file",
            "message": "task_plan.md does not exist or is empty",
            "suggestion": "Create task_plan.md using the template or init-session.sh script"
        })
        return issues

    lines = content.split('\n')

    # Check for Goal section
    has_goal = any('## Goal' in line for line in lines)
    if not has_goal:
        issues.append({
            "severity": "high",
            "category": "missing-section",
            "message": "No Goal section found in task_plan.md",
            "suggestion": "Add ## Goal section with a clear one-sentence description of the end state"
        })

    # Check for Current Phase
    has_current_phase = any('## Current Phase' in line for line in lines)
    if not has_current_phase:
        issues.append({
            "severity": "high",
            "category": "missing-section",
            "message": "No Current Phase section found in task_plan.md",
            "suggestion": "Add ## Current Phase section to track which phase you're working on"
        })

    # Check for Phases section
    has_phases = any('## Phases' in line for line in lines)
    if not has_phases:
        issues.append({
            "severity": "high",
            "category": "missing-section",
            "message": "No Phases section found in task_plan.md",
            "suggestion": "Add ## Phases section with 3-7 logical phases"
        })

    # Check for phase statuses
    has_status_markers = any('**Status:**' in line for line in lines)
    if not has_status_markers:
        issues.append({
            "severity": "medium",
            "category": "missing-status",
            "message": "No phase status markers found",
            "suggestion": "Add **Status:** to each phase (pending/in_progress/complete)"
        })

    # Check for Errors section
    has_errors = any('## Errors Encountered' in line for line in lines)
    if not has_errors:
        issues.append({
            "severity": "low",
            "category": "best-practice",
            "message": "No Errors Encountered section found",
            "suggestion": "Add ## Errors Encountered section to track and learn from errors"
        })

    # Check phase count
    phase_count = sum(1 for line in lines if line.startswith('### Phase'))
    if phase_count < 3:
        issues.append({
            "severity": "medium",
            "category": "planning",
            "message": f"Only {phase_count} phases defined (recommended: 3-7)",
            "suggestion": "Break down the task into 3-7 logical phases"
        })
    elif phase_count > 7:
        issues.append({
            "severity": "low",
            "category": "planning",
            "message": f"Too many phases defined: {phase_count} (recommended: 3-7)",
            "suggestion": "Consider consolidating related phases"
        })

    return issues


def validate_findings(content: str) -> List[Dict]:
    """Validate findings.md structure and content."""
    issues = []

    if not content:
        issues.append({
            "severity": "medium",
            "category": "missing-file",
            "message": "findings.md does not exist or is empty",
            "suggestion": "Create findings.md to document discoveries and decisions"
        })
        return issues

    lines = content.split('\n')

    # Check for key sections
    sections = [
        ("Requirements", "## Requirements"),
        ("Research Findings", "## Research Findings"),
        ("Technical Decisions", "## Technical Decisions")
    ]

    for section_name, section_marker in sections:
        has_section = any(section_marker in line for line in lines)
        if not has_section:
            issues.append({
                "severity": "low",
                "category": "missing-section",
                "message": f"No {section_name} section in findings.md",
                "suggestion": f"Add {section_marker} section to track {section_name.lower()}"
            })

    # Check for empty sections
    current_section = None
    empty_sections = []
    for line in lines:
        if line.startswith('##'):
            current_section = line
        elif current_section and line.strip():
            current_section = None

    return issues


def validate_progress(content: str) -> List[Dict]:
    """Validate progress.md structure and content."""
    issues = []

    if not content:
        issues.append({
            "severity": "low",
            "category": "missing-file",
            "message": "progress.md does not exist or is empty",
            "suggestion": "Create progress.md to track session activities"
        })
        return issues

    lines = content.split('\n')

    # Check for session info
    has_session = any('## Session:' in line for line in lines)
    if not has_session:
        issues.append({
            "severity": "low",
            "category": "missing-info",
            "message": "No Session section found in progress.md",
            "suggestion": "Add ## Session: [DATE] to track when work happened"
        })

    return issues


def validate_2_action_rule(task_plan_content: str, findings_content: str) -> List[Dict]:
    """Check if findings.md is being updated (2-Action Rule compliance)."""
    issues = []

    if not findings_content:
        return issues

    lines = findings_content.split('\n')

    # Check for recent updates (presence of content)
    has_content = any(line.strip() and not line.startswith('#') for line in lines)
    if not has_content:
        issues.append({
            "severity": "medium",
            "category": "2-action-rule",
            "message": "findings.md appears empty or unused",
            "suggestion": "Apply 2-Action Rule: Update findings.md after every 2 view/browser/search operations"
        })

    return issues


def validate_phase_status(task_plan_content: str) -> List[Dict]:
    """Check if phases are being properly tracked."""
    issues = []

    if not task_plan_content:
        return issues

    lines = task_plan_content.split('\n')

    # Count phases by status
    statuses = {"pending": 0, "in_progress": 0, "complete": 0}
    for i, line in enumerate(lines):
        if '**Status:**' in line:
            for status in statuses.keys():
                if status in line.lower():
                    statuses[status] += 1

    # Check for multiple in_progress phases
    if statuses["in_progress"] > 1:
        issues.append({
            "severity": "medium",
            "category": "phase-tracking",
            "message": f"Multiple phases marked as in_progress ({statuses['in_progress']})",
            "suggestion": "Mark completed phases as 'complete' and only keep one as 'in_progress'"
        })

    # Check if no phase is in_progress
    if statuses["in_progress"] == 0 and statuses["complete"] < statuses["pending"]:
        issues.append({
            "severity": "low",
            "category": "phase-tracking",
            "message": "No phase marked as in_progress",
            "suggestion": "Mark the current phase as 'in_progress' to track progress"
        })

    return issues


def generate_validation_report(project_dir: Path):
    """Generate comprehensive validation report."""
    print("\n" + "="*80)
    print("PLANNING-WITH-FILES: RULES VALIDATION REPORT")
    print("="*80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project: {project_dir}")
    print()

    # Read all files
    task_plan = read_markdown_file(project_dir / "task_plan.md")
    findings = read_markdown_file(project_dir / "findings.md")
    progress = read_markdown_file(project_dir / "progress.md")

    # Collect all issues
    all_issues = []

    # File existence
    file_status = validate_file_existence(project_dir)
    print("📁 FILE EXISTENCE CHECK")
    print("-" * 80)
    for filename, exists in file_status.items():
        status = "✓" if exists else "✗"
        print(f"  {status} {filename}")
        if not exists:
            all_issues.append({
                "severity": "critical",
                "category": "missing-file",
                "message": f"{filename} does not exist",
                "suggestion": f"Create {filename} using templates or init-session.sh"
            })

    print()

    # Validate each file
    print("🔍 STRUCTURE VALIDATION")
    print("-" * 80)

    task_plan_issues = validate_task_plan(task_plan)
    if task_plan_issues:
        print(f"\n  task_plan.md: {len(task_plan_issues)} issue(s)")
        for issue in task_plan_issues:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[issue["severity"]]
            print(f"    {severity_icon} [{issue['severity'].upper()}] {issue['message']}")
            print(f"       💡 {issue['suggestion']}")
            all_issues.append(issue)
    else:
        print(f"  ✓ task_plan.md: No issues found")

    findings_issues = validate_findings(findings)
    if findings_issues:
        print(f"\n  findings.md: {len(findings_issues)} issue(s)")
        for issue in findings_issues:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[issue["severity"]]
            print(f"    {severity_icon} [{issue['severity'].upper()}] {issue['message']}")
            print(f"       💡 {issue['suggestion']}")
            all_issues.append(issue)
    else:
        print(f"  ✓ findings.md: No issues found")

    progress_issues = validate_progress(progress)
    if progress_issues:
        print(f"\n  progress.md: {len(progress_issues)} issue(s)")
        for issue in progress_issues:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[issue["severity"]]
            print(f"    {severity_icon} [{issue['severity'].upper()}] {issue['message']}")
            print(f"       💡 {issue['suggestion']}")
            all_issues.append(issue)
    else:
        print(f"  ✓ progress.md: No issues found")

    # Rule compliance
    print("\n📏 RULE COMPLIANCE CHECK")
    print("-" * 80)

    two_action_issues = validate_2_action_rule(task_plan, findings)
    if two_action_issues:
        print(f"\n  2-Action Rule: {len(two_action_issues)} issue(s)")
        for issue in two_action_issues:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[issue["severity"]]
            print(f"    {severity_icon} [{issue['severity'].upper()}] {issue['message']}")
            print(f"       💡 {issue['suggestion']}")
            all_issues.append(issue)
    else:
        print(f"  ✓ 2-Action Rule: Compliant")

    phase_status_issues = validate_phase_status(task_plan)
    if phase_status_issues:
        print(f"\n  Phase Status Tracking: {len(phase_status_issues)} issue(s)")
        for issue in phase_status_issues:
            severity_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[issue["severity"]]
            print(f"    {severity_icon} [{issue['severity'].upper()}] {issue['message']}")
            print(f"       💡 {issue['suggestion']}")
            all_issues.append(issue)
    else:
        print(f"  ✓ Phase Status Tracking: Compliant")

    # Summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)

    severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for issue in all_issues:
        severity_counts[issue["severity"]] += 1

    total_issues = sum(severity_counts.values())

    if total_issues == 0:
        print("✅ All checks passed! Your planning files are in excellent shape.")
    else:
        print(f"⚠️  Found {total_issues} issue(s):")
        if severity_counts["critical"] > 0:
            print(f"    🔴 {severity_counts['critical']} critical")
        if severity_counts["high"] > 0:
            print(f"    🟠 {severity_counts['high']} high")
        if severity_counts["medium"] > 0:
            print(f"    🟡 {severity_counts['medium']} medium")
        if severity_counts["low"] > 0:
            print(f"    🟢 {severity_counts['low']} low")

        print("\n📋 PRIORITY RECOMMENDATIONS")
        print("-" * 80)

        # Show critical and high issues first
        priority_issues = [i for i in all_issues if i["severity"] in ["critical", "high"]]
        for i, issue in enumerate(priority_issues, 1):
            print(f"  {i}. [{issue['severity'].upper()}] {issue['message']}")
            print(f"     → {issue['suggestion']}")

    print("\n" + "="*80)
    print("END OF VALIDATION REPORT")
    print("="*80 + "\n")


def main():
    """Main entry point."""
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

    if not project_dir.exists():
        print(f"Error: Directory {project_dir} does not exist")
        sys.exit(1)

    generate_validation_report(project_dir)


if __name__ == "__main__":
    main()
