---
name: beautiful-mermaid
description: Render Mermaid diagrams as beautiful SVGs or ASCII art. Supports flowcharts, state diagrams, sequence diagrams, class diagrams, and ER diagrams.
allowed-tools: Bash, Read, Write
---

# Beautiful Mermaid Skill

This skill enables you to create professional-looking diagrams using Mermaid syntax. It supports both high-quality SVG output for visual artifacts and ASCII/Unicode output for terminal/text-based displays.

## Core Features
- **SVG Rendering**: Professional themes, zero DOM dependencies, ultra-fast.
- **ASCII/Unicode Rendering**: Beautiful box-drawing diagrams for text-based environments.
- **Built-in Themes**: 15 themes including Tokyo Night, Catppuccin, Nord, and GitHub styles.

## Usage Patterns

### 1. Rendering ASCII Diagrams (for text/markdown)
Use this when you want to embed a diagram directly in a markdown file or chat response.

```typescript
import { renderMermaidAscii } from 'E:\\AI\\.stepfun\\skills\\beautiful-mermaid\\beautiful-mermaid-0.1.3\\index.ts'

const ascii = renderMermaidAscii(`graph LR; A --> B --> C`)
console.log(ascii)
```

> **注意**: 如果执行位置不同，请使用绝对路径 `E:\AI\.stepfun\skills\beautiful-mermaid\beautiful-mermaid-0.1.3\index.ts` 或相应调整相对路径。

### 2. Rendering SVG Artifacts
Use this to create high-quality visual artifacts for users.

```typescript
import { renderMermaid, THEMES } from 'E:\\AI\\.stepfun\\skills\\beautiful-mermaid\\beautiful-mermaid-0.1.3\\index.ts'

const svg = await renderMermaid(diagram, THEMES['tokyo-night'])
// Save svg to a file and use artifact tool
```

> **注意**: 如果执行位置不同，请使用绝对路径 `E:\AI\.stepfun\skills\beautiful-mermaid\beautiful-mermaid-0.1.3\index.ts` 或相应调整相对路径。

## Supported Diagram Types
- **Flowcharts**: `graph TD`, `graph LR`, etc.
- **State Diagrams**: `stateDiagram-v2`
- **Sequence Diagrams**: `sequenceDiagram`
- **Class Diagrams**: `classDiagram`
- **ER Diagrams**: `erDiagram`

## Theming
You can customize the look using the `THEMES` object or by providing custom `bg` and `fg` colors.
