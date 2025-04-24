# GitHub Setup Guide for Context-Aware Privacy Blurring

This guide will walk you through the process of pushing your Context-Aware Privacy Blurring project to GitHub.

## Prerequisites

- GitHub account
- Git installed on your local machine
- Access to terminal/command prompt

## Steps to Push to GitHub

### 1. Create a New Repository on GitHub

1. Log in to your GitHub account
2. Click on the '+' icon in the top-right corner and select 'New repository'
3. Name your repository (e.g., "context-aware-privacy-blurring")
4. Add a description: "AI-driven adaptive privacy protection system that automatically detects and selectively blurs sensitive content in real-time video streams"
5. Choose public or private visibility based on your preference
6. Do NOT initialize the repository with README, .gitignore, or license (you already have these files locally)
7. Click "Create repository"

### 2. Link Your Local Repository to GitHub

After creating the repository, GitHub will display commands to push an existing repository. Use the following commands in your terminal:

```bash
# Make sure you're in your project directory
cd path/to/context-aware-privacy-blurring

# Set the remote repository URL (replace 'yourusername' with your actual GitHub username)
git remote add origin https://github.com/yourusername/context-aware-privacy-blurring.git

# Verify the remote was added
git remote -v

# Push your code to GitHub (main branch)
git push -u origin main
```

You will be prompted to enter your GitHub username and password (or personal access token if you have 2FA enabled).

### 3. Set Up GitHub Personal Access Token (If Using 2FA)

If you have two-factor authentication enabled on your GitHub account:

1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Click "Generate new token"
3. Give the token a descriptive name (e.g., "Context-Aware Privacy Blurring")
4. Select scopes: 'repo', 'workflow', and 'read:org'
5. Click "Generate token"
6. Copy the token immediately (you won't be able to see it again)
7. Use this token as your password when pushing to GitHub

### 4. Verify Your Repository

1. Go to https://github.com/yourusername/context-aware-privacy-blurring
2. Confirm that all your files have been uploaded
3. Review the README.md which should be displayed on the repository homepage

## Ongoing GitHub Usage

### Making Changes

After making changes to your local files:

```bash
# Check which files have changed
git status

# Add changed files
git add .

# Commit changes with a descriptive message
git commit -m "Brief description of changes"

# Push to GitHub
git push
```

### Creating a Branch

For developing new features:

```bash
# Create and switch to a new branch
git checkout -b feature-name

# Work on your changes...

# Push the branch to GitHub
git push -u origin feature-name
```

### Creating a Release

To create a version release:

1. Go to your repository on GitHub
2. Click "Releases" on the right sidebar
3. Click "Create a new release"
4. Add a tag version (e.g., "v1.0.0")
5. Add a release title and description
6. Optionally attach binaries
7. Click "Publish release"

## Collaboration

### Adding Collaborators

1. Go to your repository on GitHub
2. Click "Settings" > "Manage access"
3. Click "Invite a collaborator"
4. Enter the GitHub username or email of the person
5. Select their role (read, triage, write, maintain, or admin)
6. Click "Add"

### Pull Requests

For collaborators to contribute:

1. They should fork your repository
2. Clone their fork locally
3. Create a branch for their changes
4. Push changes to their fork
5. Create a pull request to your repository
6. You review and merge their changes

## Documentation

Remember to keep your documentation up to date:

- `README.md` - General project information and quick start guide
- `SETUP_GUIDE.md` - Detailed installation instructions
- `LICENSE` - License information
- `dependencies.txt` - List of project dependencies

## Best Practices

- Commit often with clear, concise messages
- Keep sensitive data out of your repository (use .env for local environment variables)
- Use branches for new features or bug fixes
- Write clear documentation
- Respond to issues and pull requests promptly