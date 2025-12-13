# Quickstart: Setting up the Docusaurus Textbook Project

This guide provides instructions for setting up the Docusaurus project for the "Physical AI & Humanoid Robotics Textbook".

## Prerequisites

-   [Node.js](https://nodejs.org/) (version 18.x or later)
-   [Yarn](https://yarnpkg.com/) or [npm](https://www.npmjs.com/)

## Installation

1.  **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Navigate to the Docusaurus project directory:**

    ```bash
    cd docusaurus-book
    ```

3.  **Install dependencies:**

    Using Yarn:
    ```bash
    yarn install
    ```

    Using npm:
    ```bash
    npm install
    ```

## Running the Development Server

1.  **Start the Docusaurus development server:**

    Using Yarn:
    ```bash
    yarn start
    ```

    Using npm:
    ```bash
    npm run start
    ```

2.  **Open the site in your browser:**

    The site will be available at [http://localhost:3000](http://localhost:3000).

## Building the Site

1.  **Build the static site for production:**

    Using Yarn:
    ```bash
    yarn build
    ```

    Using npm:
    ```bash
    npm run build
    ```

    The built files will be located in the `build` directory.

## Deployment

The site can be deployed to any static web host. For GitHub Pages, follow the instructions in the main `README.md` file of the Docusaurus project.
