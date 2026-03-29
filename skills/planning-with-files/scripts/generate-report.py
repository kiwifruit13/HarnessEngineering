#!/usr/bin/env python3
"""
Progress Report Generator for planning-with-files

Generates comprehensive progress reports with visualizations,
statistics, and trend analysis.

Usage: python3 generate-report.py [project-directory] [output-file]
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


def read_markdown_file(filepath: Path) -> str:
    """Read a markdown file and return its content."""
    if not filepath.exists():
        return ""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_all_files(project_dir: Path) -> Dict:
    """Parse all three planning files."""
    task_plan = read_markdown_file(project_dir / "task_plan.md")
    findings = read_markdown_file(project_dir / "findings.md")
    progress = read_markdown_file(project_dir / "progress.md")

    return {
        "task_plan": task_plan,
        "findings": findings,
        "progress": progress
    }


def extract_phases(content: str) -> List[Dict]:
    """Extract phase information from task_plan.md."""
    phases = []
    if not content:
        return phases

    lines = content.split('\n')
    current_phase = None

    for i, line in enumerate(lines):
        if line.startswith('### Phase'):
            current_phase = line.replace('### Phase', '').strip()
            # Look for status in next 10 lines
            for j in range(i, min(i+10, len(lines))):
                if '**Status:**' in lines[j]:
                    status = lines[j].split('**Status:**')[1].strip()
                    phases.append({
                        "name": current_phase,
                        "status": status
                    })
                    break
    return phases


def extract_errors(content: str) -> List[Dict]:
    """Extract error information from task_plan.md."""
    errors = []
    if not content:
        return errors

    lines = content.split('\n')
    in_errors = False

    for line in lines:
        if '## Errors Encountered' in line:
            in_errors = True
            continue
        if in_errors and line.startswith('##'):
            break
        if in_errors and '|' in line and not line.startswith('|---'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3 and parts[0]:
                errors.append({
                    "error": parts[0],
                    "attempt": parts[1],
                    "resolution": parts[2]
                })
    return errors


def extract_goal(content: str) -> str:
    """Extract goal from task_plan.md."""
    if not content:
        return "Not specified"

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('## Goal'):
            for j in range(i+1, len(lines)):
                if lines[j].strip() and not lines[j].startswith('#'):
                    return lines[j].strip()
    return "Not specified"


def extract_findings(content: str) -> Dict:
    """Extract findings statistics."""
    stats = {
        "requirements": 0,
        "research": 0,
        "decisions": 0,
        "issues": 0
    }

    if not content:
        return stats

    lines = content.split('\n')
    current_section = None

    for line in lines:
        if line.startswith('## Requirements'):
            current_section = "requirements"
        elif line.startswith('## Research Findings'):
            current_section = "research"
        elif line.startswith('## Technical Decisions'):
            current_section = "decisions"
        elif line.startswith('## Issues Encountered'):
            current_section = "issues"
        elif line.startswith('##'):
            current_section = None
        elif current_section and line.strip() and not line.startswith('#') and line.startswith('-'):
            stats[current_section] += 1

    return stats


def calculate_metrics(phases: List[Dict], errors: List[Dict]) -> Dict:
    """Calculate progress metrics."""
    if not phases:
        return {
            "total_phases": 0,
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "progress_percent": 0,
            "total_errors": len(errors),
            "resolved_errors": 0
        }

    completed = sum(1 for p in phases if "complete" in p["status"].lower())
    in_progress = sum(1 for p in phases if "in_progress" in p["status"].lower())
    pending = sum(1 for p in phases if "pending" in p["status"].lower())

    progress_percent = int((completed / len(phases)) * 100) if phases else 0

    # Count resolved errors (have resolution text)
    resolved = sum(1 for e in errors if e.get("resolution"))

    return {
        "total_phases": len(phases),
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "progress_percent": progress_percent,
        "total_errors": len(errors),
        "resolved_errors": resolved
    }


def generate_markdown_report(project_dir: Path, files: Dict, output_file: Path = None):
    """Generate comprehensive markdown report."""
    phases = extract_phases(files["task_plan"])
    errors = extract_errors(files["task_plan"])
    goal = extract_goal(files["task_plan"])
    findings_stats = extract_findings(files["findings"])
    metrics = calculate_metrics(phases, errors)

    report_lines = []

    # Header
    report_lines.append("# Progress Report")
    report_lines.append("")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Project:** {project_dir.name}")
    report_lines.append("")

    # Executive Summary
    report_lines.append("## 📊 Executive Summary")
    report_lines.append("")
    report_lines.append(f"**Goal:** {goal}")
    report_lines.append("")
    report_lines.append(f"- **Overall Progress:** {metrics['progress_percent']}%")
    report_lines.append(f"- **Phases Completed:** {metrics['completed']}/{metrics['total_phases']}")
    report_lines.append(f"- **Errors Encountered:** {metrics['total_errors']}")
    report_lines.append(f"- **Errors Resolved:** {metrics['resolved_errors']}")
    report_lines.append("")

    # Progress Bar
    report_lines.append("### Progress Visualization")
    report_lines.append("")
    bar_length = 30
    filled = int(bar_length * metrics['progress_percent'] / 100)
    bar = "█" * filled + "░" * (bar_length - filled)
    report_lines.append(f"``")
    report_lines.append(f"[{bar}] {metrics['progress_percent']}%")
    report_lines.append(f"```")
    report_lines.append("")

    # Phase Breakdown
    report_lines.append("## 📋 Phase Breakdown")
    report_lines.append("")

    for phase in phases:
        status_icon = "✅" if "complete" in phase["status"].lower() else "🔄" if "in_progress" in phase["status"].lower() else "⏸️"
        report_lines.append(f"### {status_icon} {phase['name']}")
        report_lines.append(f"**Status:** {phase['status']}")
        report_lines.append("")

    # Key Statistics
    report_lines.append("## 📈 Key Statistics")
    report_lines.append("")

    report_lines.append("### Planning Files")
    report_lines.append("")
    report_lines.append("| File | Status | Content |")
    report_lines.append("|------|--------|---------|")
    report_lines.append(f"| task_plan.md | {'✅' if files['task_plan'] else '❌'} | {len(files['task_plan'])} characters |")
    report_lines.append(f"| findings.md | {'✅' if files['findings'] else '❌'} | {len(files['findings'])} characters |")
    report_lines.append(f"| progress.md | {'✅' if files['progress'] else '❌'} | {len(files['progress'])} characters |")
    report_lines.append("")

    report_lines.append("### Findings Breakdown")
    report_lines.append("")
    report_lines.append("| Category | Count |")
    report_lines.append("|----------|-------|")
    report_lines.append(f"| Requirements | {findings_stats['requirements']} |")
    report_lines.append(f"| Research Findings | {findings_stats['research']} |")
    report_lines.append(f"| Technical Decisions | {findings_stats['decisions']} |")
    report_lines.append(f"| Issues | {findings_stats['issues']} |")
    report_lines.append("")

    # Error Summary
    if errors:
        report_lines.append("## ❌ Error Summary")
        report_lines.append("")
        report_lines.append(f"Total errors: **{metrics['total_errors']}**")
        report_lines.append(f"Resolved: **{metrics['resolved_errors']}** ({int((metrics['resolved_errors']/metrics['total_errors'])*100) if metrics['total_errors'] else 0}%)")
        report_lines.append("")

        report_lines.append("### Error Details")
        report_lines.append("")
        report_lines.append("| Error | Attempt | Resolution |")
        report_lines.append("|-------|---------|------------|")
        for error in errors:
            resolution = error.get("resolution", "Pending")
            report_lines.append(f"| {error['error']} | {error['attempt']} | {resolution} |")
        report_lines.append("")

    # Recommendations
    report_lines.append("## 🎯 Recommendations")
    report_lines.append("")

    # Find next incomplete phase
    next_phase = None
    for phase in phases:
        if "pending" in phase["status"].lower():
            next_phase = phase
            break

    if next_phase:
        report_lines.append(f"1. **Start Next Phase:** {next_phase['name']}")
        report_lines.append(f"   - Current status: {next_phase['status']}")
        report_lines.append(f"   - Action: Review requirements and begin execution")
        report_lines.append("")
    elif metrics['completed'] == metrics['total_phases']:
        report_lines.append("1. **Review Deliverables:** All phases complete")
        report_lines.append("   - Verify all requirements are met")
        report_lines.append("   - Prepare for final handoff")
        report_lines.append("")
    else:
        report_lines.append("1. **Complete Current Phase:** Mark in-progress phase as complete")
        report_lines.append("   - Review checklist items")
        report_lines.append("   - Update status in task_plan.md")
        report_lines.append("")

    report_lines.append("2. **Maintain 2-Action Rule:** Update findings.md after every 2 operations")
    report_lines.append("   - Prevents information loss")
    report_lines.append("   - Maintains knowledge base")
    report_lines.append("")

    if metrics['total_errors'] > metrics['resolved_errors']:
        unresolved = metrics['total_errors'] - metrics['resolved_errors']
        report_lines.append(f"3. **Address Unresolved Errors:** {unresolved} error(s) remaining")
        report_lines.append("   - Review error log in task_plan.md")
        report_lines.append("   - Apply 3-Strike Error Protocol")
        report_lines.append("")

    # Footer
    report_lines.append("---")
    report_lines.append("")
    report_lines.append("*Report generated by planning-with-files progress report generator*")
    report_lines.append(f"*Generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    # Write report
    report_content = '\n'.join(report_lines)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        print(f"✓ Report saved to: {output_file}")
    else:
        print("\n" + report_content)

    return report_content


def main():
    """Main entry point."""
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    if not project_dir.exists():
        print(f"Error: Directory {project_dir} does not exist")
        sys.exit(1)

    files = parse_all_files(project_dir)

    if not files["task_plan"]:
        print("⚠️  Warning: task_plan.md not found. Cannot generate full report.")
        print("   Ensure planning files exist in the project directory.")

    if output_file:
        generate_markdown_report(project_dir, files, output_file)
    else:
        generate_markdown_report(project_dir, files)


if __name__ == "__main__":
    main()
