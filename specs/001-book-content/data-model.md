# Data Model: Textbook Content Structure

This document defines the data structure for the content of the "Physical AI & Humanoid Robotics Textbook". This model will be used to ensure consistency across all generated MDX files.

## Chapter

A `Chapter` is a top-level container for a major topic.

-   **`title`**: `string` - The title of the chapter (e.g., "What is Physical AI").
-   **`slug`**: `string` - The URL-friendly slug for the chapter (e.g., "what-is-physical-ai").
-   **`summary`**: `string` - A brief introduction to the chapter's content.
-   **`modules`**: `Module[]` - An array of `Module` objects that make up the chapter.

## Module

A `Module` is a smaller, focused unit of content within a chapter.

-   **`title`**: `string` - The title of the module (e.g., "Key Concepts in Physical AI").
-   **`content`**: `string` (Markdown) - The main body of the module's content.
-   **`diagrams`**: `Diagram[]` - An array of `Diagram` objects to be included in the module.
-   **`examples`**: `Example[]` - An array of `Example` objects illustrating concepts.
-   **`activities`**: `Activity[]` - An array of `Activity` objects for hands-on learning.
-   **`quiz`**: `Quiz` - A `Quiz` object to assess understanding of the module.

## Diagram

A `Diagram` represents a visual aid.

-   **`title`**: `string` - A title or caption for the diagram.
-   **`type`**: `enum('ascii', 'mermaid')` - The type of diagram.
-   **`content`**: `string` - The ASCII art or Mermaid.js syntax for the diagram.

## Example

An `Example` provides a real-world or code-based illustration of a concept.

-   **`title`**: `string` - A title for the example.
-   **`content`**: `string` (Markdown/Code) - The example content, which may include code blocks.

## Activity

An `Activity` is a hands-on exercise for the student.

-   **`title`**: `string` - The title of the activity.
-   **`description`**: `string` (Markdown) - Instructions for the activity.
-   **`expected_outcome`**: `string` (Markdown) - What the student should achieve.

## Quiz

A `Quiz` assesses the student's understanding of a module.

-   **`questions`**: `Question[]` - An array of `Question` objects.

## Question

A `Question` is a single quiz question.

-   **`text`**: `string` - The text of the question.
-   **`type`**: `enum('multiple-choice', 'true-false', 'short-answer')` - The type of question.
-   **`options`**: `string[]` - An array of options for multiple-choice questions.
-   **`correct_answer`**: `string` - The correct answer.
-   **`explanation`**: `string` (Markdown) - An explanation of the correct answer.
