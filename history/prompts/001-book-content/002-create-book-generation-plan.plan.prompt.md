---
id: 002
title: Create Book Generation Plan
stage: plan
date: 2025-12-06
surface: agent
model: gemini
feature: 001-book-content
branch: 001-book-content
user: 
command: /sp.plan # Book Generation Plan

## Phase 1 — Book Skeleton
1. Generate:
   - Title Page
   - Preface
   - Table of Contents
   - Chapter Outline

## Phase 2 — Core Chapters (10 Total)
Ch1 — What is Physical AI  
Ch2 — Humanoid Robotics Foundations  
Ch3 — Sensors & Perception  
Ch4 — ROS 2 Fundamentals  
Ch5 — Gazebo & Unity Simulation  
Ch6 — NVIDIA Isaac Sim & Isaac ROS  
Ch7 — Vision-Language-Action Robotics  
Ch8 — Conversational Robotics (GPT + Whisper)  
Ch9 — Humanoid Locomotion & Manipulation  
Ch10 — Capstone: Autonomous Humanoid Robot

Each chapter includes:
• Introduction  
• Key Concepts  
• Diagrams  
• Real-world examples  
• Student activities  
• Mini quiz  

## Phase 3 — Weekly Breakdown
Create a 12–13 week curriculum following the official hackathon syllabus.

## Phase 4 — Hardware Appendix
Include:
- Workstation specs  
- Jetson Orin Nano setup  
- RealSense integration  
- Robot Lab tiers (budget → premium)  

## Phase 5 — Docusaurus Integration (MCP Context Required)
Using **https://docusaurus.io/docs via the MCP server**, generate:
- MDX for all chapters
- `/docs/intro.md`
- `/docs/chapters/*.md`
- `/docs/capstone/*.md`
- `/docs/hardware/*.md`
- `sidebars.js` structure
- `docusaurus.config.js` template
- GitHub Pages deployment instructions

Must follow:
- MDX rules
- Folder conventions
- Sidebar linking
- Frontmatter formatting
- Component usage (if needed)

## Phase 6 — Final Assembly
1. Output the full MDX book folder tree.
2. Output instructions for `npm run build` & GitHub Pages deploy.
3. Provide optional custom theme or layout (if asked).
labels: ["plan", "robotics", "textbook"]
links:
  spec: specs/001-book-content/spec.md
  plan: specs/001-book-content/plan.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-book-content/plan.md
  - specs/001-book-content/research.md
  - specs/001-book-content/data-model.md
  - specs/001-book-content/contracts/mdx-frontmatter.json
  - specs/001-book-content/quickstart.md
tests:

---

## Prompt

/sp.plan # Book Generation Plan

## Phase 1 — Book Skeleton
1. Generate:
   - Title Page
   - Preface
   - Table of Contents
   - Chapter Outline

## Phase 2 — Core Chapters (10 Total)
Ch1 — What is Physical AI  
Ch2 — Humanoid Robotics Foundations  
Ch3 — Sensors & Perception  
Ch4 — ROS 2 Fundamentals  
Ch5 — Gazebo & Unity Simulation  
Ch6 — NVIDIA Isaac Sim & Isaac ROS  
Ch7 — Vision-Language-Action Robotics  
Ch8 — Conversational Robotics (GPT + Whisper)  
Ch9 — Humanoid Locomotion & Manipulation  
Ch10 — Capstone: Autonomous Humanoid Robot

Each chapter includes:
• Introduction  
• Key Concepts  
• Diagrams  
• Real-world examples  
• Student activities  
• Mini quiz  

## Phase 3 — Weekly Breakdown
Create a 12–13 week curriculum following the official hackathon syllabus.

## Phase 4 — Hardware Appendix
Include:
- Workstation specs  
- Jetson Orin Nano setup  
- RealSense integration  
- Robot Lab tiers (budget → premium)  

## Phase 5 — Docusaurus Integration (MCP Context Required)
Using **https://docusaurus.io/docs via the MCP server**, generate:
- MDX for all chapters
- `/docs/intro.md`
- `/docs/chapters/*.md`
- `/docs/capstone/*.md`
- `/docs/hardware/*.md`
- `sidebars.js` structure
- `docusaurus.config.js` template
- GitHub Pages deployment instructions

Must follow:
- MDX rules
- Folder conventions
- Sidebar linking
- Frontmatter formatting
- Component usage (if needed)

## Phase 6 — Final Assembly
1. Output the full MDX book folder tree.
2. Output instructions for `npm run build` & GitHub Pages deploy.
3. Provide optional custom theme or layout (if asked).

## Response snapshot

I have successfully created the implementation plan for the "Physical AI & Humanoid Robotics Textbook". The plan is located at `specs/001-book-content/plan.md`. I have also generated the following artifacts:

- `specs/001-book-content/research.md`: Outlines research tasks for Docusaurus best practices.
- `specs/001-book-content/data-model.md`: Defines the content structure for the textbook.
- `specs/001-book-content/contracts/mdx-frontmatter.json`: Defines the frontmatter schema for MDX files.
- `specs/001-book-content/quickstart.md`: Provides setup instructions for the Docusaurus project.

The agent context has been updated with the technologies from the plan. The next step is to proceed with the tasks generation using `/sp.tasks`.

## Outcome

- ✅ Impact: A detailed implementation plan has been created, outlining the phases of the book generation process and defining the technical context, project structure, and key design artifacts.
- 🧪 Tests: Not applicable for this task.
- 📁 Files: `specs/001-book-content/plan.md`, `specs/001-book-content/research.md`, `specs/001-book-content/data-model.md`, `specs/001-book-content/contracts/mdx-frontmatter.json`, `specs/001-book-content/quickstart.md` created/updated.
- 🔁 Next prompts: You can now proceed to the tasks generation phase using `/sp.tasks`.
- 🧠 Reflection: The user provided a clear, phased plan, which was easily translated into the formal planning documents.

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None
