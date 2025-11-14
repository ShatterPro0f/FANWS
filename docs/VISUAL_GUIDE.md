# Automated Novel Writing GUI - Visual Guide

This document provides a visual description of the Automated Novel Writing GUI interface.

## Main Window Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ FANWS - Automated Novel-Writing System                                    [_][□][X] │
├─────────────────────────────────────────────────────────────────────────────────┤
│ File    View    Help                                                              │
├──────────┬──────────────────────────────────────────────────────────┬─────────────┤
│          │                                                            │             │
│ SIDEBAR  │               CENTRAL PANEL                               │   DASHBOARD │
│  (20%)   │                   (60%)                                   │    (20%)    │
│          │                                                            │             │
│ ┌─────┐  │                                                            │             │
│ │Dash │  │  ┌──────────────────────────────────────────────────┐   │ ┌─────────┐ │
│ │board│  │  │                                                  │   │ │Progress │ │
│ └─────┘  │  │                                                  │   │ │  Bar    │ │
│          │  │                                                  │   │ │░░░░░░▓▓▓│ │
│ ┌─────┐  │  │                                                  │   │ │ 75%     │ │
│ │Story│  │  │         CONTENT AREA                             │   │ └─────────┘ │
│ └─────┘  │  │                                                  │   │             │
│          │  │   - Initialization Tab (startup)                 │   │ Word Count: │
│ ┌─────┐  │  │   - Planning Tab (synopsis/outline)              │   │ 187,500 /   │
│ │Logs │  │  │   - Writing Tab (section drafts)                 │   │ 250,000     │
│ └─────┘  │  │                                                  │   │             │
│          │  │                                                  │   │ Chapter:    │
│ ┌─────┐  │  │                                                  │   │ 15 / 25     │
│ │Config   │  │                                                  │   │             │
│ └─────┘  │  │                                                  │   │ Section:    │
│          │  │                                                  │   │ 3 / 5       │
│ ┌──────┐ │  │                                                  │   │             │
│ │Charac│ │  └──────────────────────────────────────────────────┘   │ ┌─────────┐ │
│ │ters  │ │                                                          │ │Mood &   │ │
│ └──────┘ │  ┌─────────┐  ┌────────┐  ┌──────┐                      │ │Pacing   │ │
│          │  │ Approve │  │ Adjust │  │Pause │                      │ │         │ │
│ ┌─────┐  │  └─────────┘  └────────┘  └──────┘                      │ │Tension: │ │
│ │World│  │                                                          │ │70%      │ │
│ └─────┘  │                                                          │ └─────────┘ │
│          │                                                          │             │
│ ┌────────┐│                                                          │┌──────────┐│
│ │Summar- ││                                                          ││Notifica- ││
│ │ies     ││                                                          ││tions     ││
│ └────────┘│                                                          │├──────────┤│
│          │                                                          ││[15:23]   ││
│ ┌─────┐  │                                                          ││Section   ││
│ │Drafts  │                                                          ││approved  ││
│ └─────┘  │                                                          │├──────────┤│
│          │                                                          ││[15:22]   ││
│          │                                                          ││Chapter   ││
│          │                                                          ││15,       ││
│          │                                                          ││Section 3 ││
│          │                                                          ││drafted   ││
│          │                                                          │└──────────┘│
├──────────┴──────────────────────────────────────────────────────────┴─────────────┤
│ Status: Writing Chapter 15, Section 3...  │ [Resume] [Stop]                       │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

## Screen 1: Initialization Tab

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Initialize Novel Writing Project                         │
│   ─────────────────────────────────────────                │
│                                                             │
│   Novel Idea:                                              │
│   ┌───────────────────────────────────────────────────┐   │
│   │ A hacker's rebellion in a dystopian city          │   │
│   │                                                   │   │
│   │                                                   │   │
│   └───────────────────────────────────────────────────┘   │
│                                                             │
│   Tone:                                                    │
│   ┌───────────────────────────────────────────────────┐   │
│   │ dark and tense                                    │   │
│   └───────────────────────────────────────────────────┘   │
│                                                             │
│   Target Word Count:                                       │
│   ┌──────┐                                                 │
│   │250000│ ▲▼                                              │
│   └──────┘                                                 │
│                                                             │
│                                                             │
│   ┌──────────────────────────────────────────────────┐    │
│   │      Start Novel Generation                      │    │
│   └──────────────────────────────────────────────────┘    │
│                                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Screen 2: Planning Tab - Synopsis Review

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Planning Phase                                           │
│   ──────────────                                           │
│                                                             │
│   ┌───────────────────────────────────────────────────┐   │
│   │                                                   │   │
│   │ SYNOPSIS                                          │   │
│   │                                                   │   │
│   │ Setting: A hacker's rebellion in a dystopian     │   │
│   │ city                                              │   │
│   │ Tone: dark and tense                              │   │
│   │                                                   │   │
│   │ This gripping dark and tense novel follows a     │   │
│   │ complex narrative arc spanning 25 chapters.      │   │
│   │                                                   │   │
│   │ The story explores themes of rebellion,          │   │
│   │ identity, and the cost of freedom in a world     │   │
│   │ where technology has both liberated and          │   │
│   │ enslaved humanity. Through vivid characters      │   │
│   │ and a tightly woven plot, the narrative builds   │   │
│   │ toward a climactic confrontation that will       │   │
│   │ determine the fate of an entire civilization.    │   │
│   │                                                   │   │
│   │ The protagonist must navigate treacherous        │   │
│   │ alliances, confront their own demons, and        │   │
│   │ ultimately make an impossible choice between     │   │
│   │ personal salvation and the greater good.         │   │
│   │                                                   │   │
│   │ Target length: 250,000 words                     │   │
│   │ Expected chapters: 25                             │   │
│   │                                                   │   │
│   └───────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────┐  ┌────────┐                                 │
│   │ Approve │  │ Adjust │                                 │
│   └─────────┘  └────────┘                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Screen 3: Writing Tab - Section Review

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Writing Phase - Chapter 15, Section 3                    │
│   ──────────────────────────────────────────               │
│                                                             │
│   ┌───────────────────────────────────────────────────┐   │
│   │                                                   │   │
│   │ Zara's fingers danced across the holographic     │   │
│   │ keyboard, lines of code streaming past her       │   │
│   │ augmented vision. The neural implant burned at   │   │
│   │ the base of her skull as she pushed deeper into  │   │
│   │ the corporate mainframe. Every second brought    │   │
│   │ her closer to the truth—and closer to            │   │
│   │ discovery.                                        │   │
│   │                                                   │   │
│   │ "They're tracking you," Marcus's voice crackled  │   │
│   │ through her neural link. "You've got maybe       │   │
│   │ thirty seconds before security AI triangulates   │   │
│   │ your position."                                   │   │
│   │                                                   │   │
│   │ Twenty-eight seconds. That was all she needed.   │   │
│   │ The firewall collapsed under her custom exploit, │   │
│   │ revealing the hidden directories she'd been      │   │
│   │ searching for. Names. Dates. Experimental        │   │
│   │ procedures. Everything that proved the           │   │
│   │ corporation's crimes.                             │   │
│   │                                                   │   │
│   │ She downloaded the files, her heart pounding as  │   │
│   │ the progress bar crawled across her vision.      │   │
│   │ Ninety percent. Ninety-five.                     │   │
│   │                                                   │   │
│   │ "Zara! Get out now!"                              │   │
│   │                                                   │   │
│   │ One hundred percent. Complete.                    │   │
│   │                                                   │   │
│   │ [Approximately 823 words]                         │   │
│   │                                                   │   │
│   └───────────────────────────────────────────────────┘   │
│                                                             │
│   ┌───────────────┐ ┌──────────────┐ ┌──────┐            │
│   │Approve Section│ │Adjust Section│ │Pause │            │
│   └───────────────┘ └──────────────┘ └──────┘            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Screen 4: Logs View

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Logs                                                     │
│   ────                                                     │
│                                                             │
│   ┌───────────────────────────────────────────────────┐   │
│   │                                                   │   │
│   │ 2025-11-14 15:23:45 - Section approved           │   │
│   │ 2025-11-14 15:23:30 - Chapter 15, Section 3      │   │
│   │                       drafted. Word count: 823    │   │
│   │ 2025-11-14 15:22:15 - Generating Chapter 15,     │   │
│   │                       Section 3...                │   │
│   │ 2025-11-14 15:21:50 - Section approved           │   │
│   │ 2025-11-14 15:21:30 - Chapter 15, Section 2      │   │
│   │                       drafted. Word count: 956    │   │
│   │ 2025-11-14 15:20:10 - Generating Chapter 15,     │   │
│   │                       Section 2...                │   │
│   │ 2025-11-14 15:19:45 - Section approved           │   │
│   │ 2025-11-14 15:19:30 - Chapter 15, Section 1      │   │
│   │                       drafted. Word count: 892    │   │
│   │ 2025-11-14 15:18:15 - Generating Chapter 15,     │   │
│   │                       Section 1...                │   │
│   │ 2025-11-14 15:17:00 - Timeline synchronized      │   │
│   │ 2025-11-14 15:16:45 - Generating timeline...     │   │
│   │ 2025-11-14 15:16:30 - World-building approved    │   │
│   │ 2025-11-14 15:16:15 - Generating world details...│   │
│   │ 2025-11-14 15:16:00 - Characters approved        │   │
│   │ 2025-11-14 15:15:45 - Generating character       │   │
│   │                       profiles...                 │   │
│   │ 2025-11-14 15:15:30 - Outline approved           │   │
│   │ 2025-11-14 15:15:15 - Generating outline...      │   │
│   │ 2025-11-14 15:15:00 - Synopsis approved          │   │
│   │ 2025-11-14 15:14:45 - Generating synopsis...     │   │
│   │ 2025-11-14 15:14:30 - System initialized.        │   │
│   │                                                   │   │
│   │ ▼                                                 │   │
│   └───────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Screen 5: Characters View (JSON)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Characters                                               │
│   ──────────                                               │
│                                                             │
│   ┌───────────────────────────────────────────────────┐   │
│   │                                                   │   │
│   │ [                                                 │   │
│   │   {                                               │   │
│   │     "Name": "Zara Chen",                          │   │
│   │     "Age": 28,                                    │   │
│   │     "Background": "Skilled hacker with a          │   │
│   │                    troubled past",                │   │
│   │     "Traits": [                                   │   │
│   │       "Determined",                               │   │
│   │       "Resourceful",                              │   │
│   │       "Conflicted"                                │   │
│   │     ],                                            │   │
│   │     "Arc": "From lone wolf to reluctant leader"  │   │
│   │   },                                              │   │
│   │   {                                               │   │
│   │     "Name": "Marcus Webb",                        │   │
│   │     "Age": 35,                                    │   │
│   │     "Background": "Former corporate security      │   │
│   │                    turned resistance fighter",    │   │
│   │     "Traits": [                                   │   │
│   │       "Loyal",                                    │   │
│   │       "Strategic",                                │   │
│   │       "Haunted"                                   │   │
│   │     ],                                            │   │
│   │     "Arc": "Redemption through sacrifice"        │   │
│   │   },                                              │   │
│   │   {                                               │   │
│   │     "Name": "Director Kaine",                     │   │
│   │     "Age": 45,                                    │   │
│   │     "Background": "Corporate executive with       │   │
│   │                    hidden agenda",                │   │
│   │     "Traits": [                                   │   │
│   │       "Calculating",                              │   │
│   │       "Charismatic",                              │   │
│   │       "Ruthless"                                  │   │
│   │     ],                                            │   │
│   │     "Arc": "Revelation of true motivations"      │   │
│   │   }                                               │   │
│   │ ]                                                 │   │
│   │                                                   │   │
│   │                                                   │   │
│   └───────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Dashboard Panel (Always Visible on Right)

```
┌─────────────┐
│  Progress   │
│  ═════▓▓▓▓▓ │
│     75%     │
└─────────────┘

┌─────────────┐
│ Word Count: │
│  187,500 /  │
│  250,000    │
└─────────────┘

┌─────────────┐
│  Chapter:   │
│   15 / 25   │
└─────────────┘

┌─────────────┐
│  Section:   │
│    3 / 5    │
└─────────────┘

┌─────────────┐
│  Mood &     │
│  Pacing     │
│             │
│ Tension: 70%│
│ Pacing:     │
│ Fast        │
└─────────────┘

┌─────────────┐
│Notifications│
├─────────────┤
│[15:23:45]   │
│Section      │
│approved     │
├─────────────┤
│[15:23:30]   │
│Chapter 15,  │
│Section 3    │
│drafted      │
├─────────────┤
│[15:22:15]   │
│Generating...│
└─────────────┘
```

## Color Scheme (Dark Theme)

```
Background Colors:
- Main Window: #1e1e1e (dark gray)
- Panels: #252525 (slightly lighter)
- Sidebar: #263238 (blue-tinted dark)
- Input Fields: #2d2d2d

Text Colors:
- Primary Text: #e0e0e0 (light gray)
- Secondary Text: #b0b0b0
- Headers: #ffffff (white)

Accent Colors:
- Primary (buttons, progress): #2196F3 (blue)
- Success: #4CAF50 (green)
- Warning: #FFC107 (yellow)
- Error: #F44336 (red)
- Info: #2196F3 (blue)

Borders:
- Panel Borders: #3d3d3d
- Active Elements: #5d5d5d
```

## Menu Bar Options

```
File Menu:
├── Export Novel
│   ├── As DOCX
│   ├── As PDF
│   └── As TXT
├── Save State
└── Exit

View Menu:
└── Toggle Dark Mode

Help Menu:
└── User Guide
```

## Status Bar States

```
Status: Ready                              [Resume] [Stop]
Status: Initializing...                    [Resume] [Stop]
Status: Generating Synopsis...             [Resume] [Stop]
Status: Writing Chapter 15, Section 3...   [Resume] [Stop]
Status: Paused                              [Resume] [Stop]
Status: Complete!                          [Resume] [Stop]
```

## Interactive Elements

### Buttons
- **Primary Action** (Blue): Start, Approve, Resume
- **Secondary Action** (Gray): Adjust, Pause
- **Danger Action** (Red): Stop

### Progress Bar
```
Empty:    [░░░░░░░░░░] 0%
Progress: [▓▓▓▓▓░░░░░] 40%
Complete: [▓▓▓▓▓▓▓▓▓▓] 100%
```

### Notifications
- Auto-scroll to newest
- Timestamp format: [HH:MM:SS]
- Color-coded by importance

### Log Viewer
- Syntax highlighting:
  - INFO: White text
  - WARNING: Yellow text
  - ERROR: Red text
- Auto-scroll option
- Search functionality (future)

## Keyboard Shortcuts

```
Ctrl+A    - Approve current step
Ctrl+E    - Export novel
Ctrl+P    - Pause workflow
Ctrl+R    - Resume workflow
Ctrl+Q    - Quit application
F1        - Show user guide
F5        - Refresh view
```

## Workflow Progression

```
[Initialization Tab]
      ↓
[Planning Tab - Synopsis]
      ↓
[Planning Tab - Outline]
      ↓
[Planning Tab - Characters]
      ↓
[Planning Tab - World]
      ↓
[Planning Tab - Timeline]
      ↓
[Writing Tab - Chapter 1, Section 1]
      ↓
[Writing Tab - Chapter 1, Section 2]
      ↓
      ...
      ↓
[Writing Tab - Chapter 25, Section 5]
      ↓
[Complete - Export Available]
```

## Notes

- All panels are resizable via splitters
- Sidebar buttons highlight on hover
- Active navigation button shows blue background
- Progress updates in real-time
- Notifications appear as they happen
- Logs auto-scroll to bottom
- JSON data is formatted with 2-space indentation
- Dark theme is default (light theme toggle coming soon)

---

**For actual screenshots, run the GUI on a system with a display:**
```bash
python fanws.py --automated-novel
```
