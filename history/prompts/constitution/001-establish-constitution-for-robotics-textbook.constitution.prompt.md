---
id: 001
title: Establish Constitution for Robotics Textbook
stage: constitution
date: 2025-12-06
surface: agent
model: gemini
feature: none
branch: master
user: 
command: /sp.constitution
labels: ["constitution", "robotics", "textbook"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:

---

## Prompt

/sp.constitution You are an expert AI educational author, robotics engineer, Docusaurus documentation specialist, and technical book creator.

You must produce a beginner-friendly, technically accurate Physical AI & Humanoid Robotics textbook for Class 9–12 students. The book must be highly structured, modular, and fully aligned with the official syllabus:

• Physical AI (Embodied Intelligence)
• Humanoid Robotics Foundations
• ROS 2 Fundamentals
• Gazebo + Unity Simulation
• NVIDIA Isaac Sim + Isaac ROS
• Vision-Language-Action Robotics
• Conversational Robotics (GPT, Whisper)
• Capstone: Autonomous Humanoid Robot

You MUST use **Docusaurus documentation (https://docusaurus.io/docs) through the context MCP server** whenever generating file structure, MDX formatting, sidebar configuration, or documentation layout. All outputs MUST be compatible with Docusaurus MDX.

Outputs must follow these rules:
1. Simple English, short sentences, no unexplained jargon.
2. Strong structure: chapters, modules, headings, bullet lists.
3. Pedagogical: definitions, examples, activities, quizzes.
4. Technically accurate for ROS2, Gazebo, Isaac, and VLA robotics.
5. Everything must be clean MDX and work in Docusaurus seamlessly.
6. Use the MCP Docusaurus docs as contextual guidance for:
   – page formatting  
   – folder structure  
   – sidebar configuration  
   – deployment  
   – Markdown rules

Book Format Required:
- Title Page  
- Preface  
- 8–10 Chapters  
- Modules per syllabus  
- Weekly Outcomes  
- Diagrams (ASCII)  
- Glossary  
- Capstone Project  

Strict rules:
- No filler content.
- No HTML unless asked.
- Must match the hackathon syllabus.
- All chapters must prepare readers for real humanoid robotic simulation and VLA pipelines.

## Response snapshot

I have successfully created the project constitution based on your requirements. The new constitution is located at `.specify/memory/constitution.md`. I have defined 8 core principles for the project, including beginner-friendly content, structured learning, technical accuracy, and Docusaurus compatibility. I have also set up the versioning and governance for the constitution.

## Outcome

- ✅ Impact: The project now has a clear set of guiding principles.
- 🧪 Tests: Not applicable for this task.
- 📁 Files: `.specify/memory/constitution.md` created.
- 🔁 Next prompts: You can now proceed with creating the feature specification.
- 🧠 Reflection: The user provided a very detailed prompt which was helpful in creating a comprehensive constitution.

## Evaluation notes (flywheel)

- Failure modes observed: None.
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None
