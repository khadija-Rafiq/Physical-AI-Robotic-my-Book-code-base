---
id: 005
title: "Refactor landing page with new design"
stage: refactor
date_iso: "2025-12-10"
surface: "agent"
model: "gemini-1.5-pro"
feature: "001-book-content"
branch: "main"
user: "user"
command: "Refactor the src/pages/index.tsx file to create a modern, professional landing page for the 'Physical AI & Humanoid Robotics' textbook."
labels: ["refactor", "frontend", "docusaurus"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "src/pages/index.tsx"
  - "src/pages/index.module.css"
tests_yaml:
  - "none"
---

# Prompt

Refactor the src/pages/index.tsx file to create a modern, professional landing page for the 'Physical AI & Humanoid Robotics' textbook.

Design Requirements:

Theme: Remove the default Docusaurus 'green/dinosaur' styling. Use a 'Tech/Futuristic' color palette (Deep Blues, Neon Cyan, and Slate Grey) suitable for a Robotics and AI course.

Hero Section: Create a high-impact Hero section with:

Title: 'Building the Future: Physical AI & Humanoid Robotics'

Subtitle: 'A comprehensive guide to embodied intelligence, Sim2Real transfer, and autonomous agents.'

Call to Action: A primary button 'Start Learning' that links directly to the first module in /docs.

Features Section: Replace the default feature cards with 3 key highlights of this project:

'Interactive Learning' (mentioning the RAG Chatbot).

'Sim2Real Focus' (Simulation to Real-world application).

'Agentic Workflow' (Powered by Autonomous AI Agents).

Module Preview: Add a section below the fold that lists the 7 Book Modules as clickable cards so users can jump to specific topics immediately.

Please update the CSS/styles accordingly to make it look polished.

# Response

I have updated the `index.tsx` and `index.module.css` files as requested, implementing the new design and content for the landing page. Both tasks are now complete. I await your next instruction.
