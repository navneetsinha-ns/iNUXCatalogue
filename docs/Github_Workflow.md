## A Typical Workflow: From Forking to Creating a Pull Request

Here is the usual workflow someone follows when they fork a project, clone it, make changes, and share those changes back with the original owner. This example includes the common commands you will actually use.

### 1. Fork the repository
On GitHub, click **Fork**.  
This creates your own online copy of the project. Git calls this remote **origin**.

The original project you forked from is called **upstream**.

### 2. Clone your fork to your computer
Open the folder where you want the project, then run:

```
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
```
Now you have the project locally and can start working with Git.

### 3. Add the original project as "upstream" (one-time setup)

This lets you pull updates from the original repository:
```
cd REPO_NAME
git remote add upstream https://github.com/ORIGINAL_OWNER/REPO_NAME.git
```

You now have two connections:

origin → your fork

upstream → the original project

### 4. Make sure your main branch is up to date

Before creating a new branch, update your main branch:

```
git checkout main
git pull origin main        # update from your fork
git pull upstream main      # optionally update from the original project
git push origin main        # sync your fork
```

### 5. Create a branch for your work

Always make changes in a branch, not main.
```
git checkout -b feature/my-change
```
Now you are working inside your new branch.

### 6. Make changes to the code

Edit files as needed.
Use Git to see what changed:
```
git status
```
### 7. Stage the changes you want to save

Choose what to include in your commit:
```
git add .
```
Or stage specific files:
```
git add file1.py file2.py
```
### 8. Commit your staged changes

Save your work locally:
```
git commit -m "Describe what you changed"
```
### 9. Push your branch to your fork (origin)

If this is the first push for this branch:
```
git push -u origin feature/my-change
```

Next time, simply:
```
git push
```

Your branch is now online in origin (your fork).

### 10. Create a Pull Request (PR)

Go to your fork on GitHub.
GitHub will suggest:

“Compare & pull request”

Click it, check that:

base = upstream/main

compare = origin/your-branch

Add a message and submit the PR.

The original owner can now review and merge your work.

This workflow is the standard pattern you’ll use again and again:
fork → clone → update main → branch → work → stage → commit → push → PR.

---
