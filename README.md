# Physical AI & Humanoid Robotics Textbook

This website is the home of the "Physical AI & Humanoid Robotics Textbook". It is built using [Docusaurus](https://docusaurus.io/), a modern static website generator.

## Installation

```bash
yarn
```

## Local Development

```bash
yarn start
```

This command starts a local development server and opens up a browser window. Most changes are reflected live without having to restart the server.

## Build

```bash
yarn build
```

This command generates static content into the `build` directory and can be served using any static contents hosting service.

## Deployment to GitHub Pages

### 1. Configure `docusaurus.config.ts`

Before deploying, make sure to update the following fields in the `docusaurus.config.ts` file:

- `url`: The URL of your GitHub Pages site (e.g., `https://<your-github-username>.github.io`)
- `baseUrl`: `/<your-repo-name>/`
- `organizationName`: Your GitHub username or organization name.
- `projectName`: Your repository name.

### 2. Deploy

Using SSH:
```bash
USE_SSH=true yarn deploy
```

Not using SSH:
```bash
GIT_USER=<Your GitHub username> yarn deploy
```

This command will build the website and push the `build` directory to the `gh-pages` branch of your repository. You will then need to configure your repository's GitHub Pages settings to use the `gh-pages` branch as the source.

Your textbook is now live!
