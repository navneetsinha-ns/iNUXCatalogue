# A Beginner-Friendly Guide to Git and GitHub

Before beginning, it helps to understand the difference between Git and GitHub, two terms that are often confused. **Git** is a version control system, which simply means it keeps track of changes you make to your files, lets you save different versions of your project, and allows you to switch between those versions safely. It runs locally on your computer. **GitHub**, on the other hand, is an online platform where Git projects can be stored, shared, and collaborated on. You can think of Git as the tool that manages your project’s history, and GitHub as the place where that history is stored online so you can access it from anywhere or work with others.


Now let's get started.

## Getting a Copy of a Repository

**If you find a repository and you want your own copy of it, how do you get it?**

On GitHub, making your own copy of someone else’s repository (as long as it’s allowed) is called **forking**. When you fork a repo, GitHub creates that copy under your own account. But that only **gives you the copy online**.

If you also want it **on your computer**, you simply **clone** your fork. Cloning just downloads your GitHub copy so you can work on it locally.

Read along to see how this works step by step.

To fork a repository, you click the **Fork** button on GitHub. That’s it — GitHub instantly makes your own copy.

Then you clone your fork (if you want an offline copy):

1. Go to the folder on your computer where you want the project.  
2. Click the address bar, type `cmd`, and hit Enter — this opens the command prompt.  
3. In the command prompt, type:
```
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
```

This downloads your GitHub copy onto your computer.

### Why do you do this?

Because you want to work locally on your computer. It’s faster, safer, and you don’t need the internet for every little change. It also lets you test things freely without affecting the original project.


## Understanding “main”

After you clone a repository, people will say “you’re on `main`,” but you won’t see any folder called `main`.

That’s because **main is not a folder** — it’s simply the name Git gives to the version of the project you’re currently looking at.


## Branches: What They Are and Why They Matter

When you create a **branch** ( more about it in a bit), you still won’t see a new folder appear. You’ll see the same files and folders, but Git treats them as belonging to a different version of the project.

Internally, Git now has:

- one timeline for **main**,  
- another timeline for **branch1**,  
- and if you create more branches, each gets its own timeline.

So you might wonder:

### If the files are same how does Git know whether you're on main, branch1, branch2, and so on?

Simple — you tell it using branch commands.

## Checking and Switching Branches

To check which branch you're on:

```
git branch
```

The branch with the `*` next to it is your current one.

To switch to another branch:

```
git checkout <branch-name>
```

When you switch branches, Git updates the files behind the scenes to match the state of that branch. **The same file can look different depending on which branch you're on, because each branch can have its own version.**

## Why Use a Branch?

Because it protects your work.

- If something goes wrong, your `main` stays safe.  
- If things go well, you simply merge your branch back into `main` later.

## How to Create a Branch

There are many ways, but here are the two simplest:

**Option 1: Create and then switch**
```
git branch <branch-name>
git checkout <branch-name>
```

**Option 2: Create and switch in one step**

```
git checkout -b <branch-name>
```


That’s it — your new branch is ready and you're now working inside it.

### What should you know about branches?

- Your `main` branch stays clean.  
- Your branch is your playground for changes.  
- When you're done, you save your work and share it.

---

# After Making Changes in Your Branch

Git does not automatically save anything.  
You have to tell Git **what** to save and **when** to save it.

This happens in three steps:
```
git status
git add
git commit

```

---

## 1. `git status` — Look at What Changed

Before saving anything, run:



```
git status
```


Git shows you every file you touched — intentional or unintentional.  
This is your chance to notice things like:

- “I didn’t mean to change that file.”  
- “This part shouldn’t be saved yet.”

`git status` gives you awareness of what’s going on.

---

## 2. `git add` — Choose What to Save

Now you tell Git exactly which changes belong in your next save:



```
git add .

```

This selects all modified files.

Or, if you want to be more careful:

```
git add filename
git add file1 file2
git add folder/
```


This is where you decide which changes are ready and which ones are not.

Why does this matter?

Because in real projects, you might fix a bug, adjust formatting, and accidentally edit a random file — all at the same time.  
`git add` lets you pick only the changes that belong together, keeping your work organised.

So:

- `git status` → shows everything  
- `git add` → selects only what should be saved  

Together, they protect you from accidental or messy commits.

---

## 3. `git commit` — Save the Selected Changes

Once you’ve chosen what to keep, save it with:

```
git commit -m "your message"
```


This creates a snapshot of the selected changes in your branch.  
Not on GitHub yet — just locally.

A commit is your checkpoint.

### In short

- `git status` → “What did I change?”  
- `git add` → “These are the changes I want to save.”  
- `git commit` → “Okay Git, save them now.”  

This three-step flow keeps your work clean, controlled, and easy to understand later.



# Pushing Your Work Online

## `git push` — Send Your Work to Your GitHub

After committing, your work still lives only on your computer. To upload your changes to your GitHub fork:

```
git push
```
This sends your saved work from your local branch to the matching branch online.



## What If It’s a Brand-New Branch?

You might think: “Wait… I cloned this from my fork. Shouldn't Git know where to push automatically?”

Git does know where your fork is — but it does **not** automatically know which remote branch your new local branch should connect to.

Why?

- Your `main` exists both locally and online → Git links these automatically.  
- But any **new branch** exists only locally at first. GitHub has never seen it.

So the first time you push a new branch, you must link it:

```
git push -u origin <branch-name>
```

After this one-time setup, future pushes become:

```
git push
```

This is not because of cloning — it’s because new branches don’t exist online until you push them once.



## Before Pushing: Check Your Branch

Before pushing anything, run:

```
git branch
```
or
```
git status
```
Git will show:
```
On branch feature/my-new-feature
```

If you’re on the wrong branch, switch before pushing.

### Putting it all together:

- `git add` → which files am I saving?  
- `git commit` → save these selected files locally.  
- `git branch` / `git status` → which branch am I on?  
- `git push` → send this branch online — so check first.

Once you push, your GitHub fork updates and your changes become visible.

---

# Creating a Pull Request (PR)

So your branch is pushed to your GitHub fork (your own copy of the original repository). Your work is now online and ready to be shared.

A **Pull Request (PR)** is how you ask the original project owner:

“I’ve made some updates. Would you like to pull them into your project?”

Here’s how to create one.

---

## 1. Go to Your Fork on GitHub
This is the repository under your username — the one created when you clicked **Fork**. If your branch has changes that the original doesn’t,

GitHub will often show: **“Compare & pull request”**

Click it.

*(Sometimes you might be behind instead of ahead — meaning the original owner updated their project after you forked. GitHub handles these cases automatically.)*

---

## 2. Or Create the PR Manually

Go to the **Pull Requests** tab → click **New pull request**.

---

## 3. Check the “Base” and “Compare” Branches

GitHub will show two fields:

- **Base** → the branch in the original project you want to update (usually `main`)  
- **Compare** → your branch that contains the updates  

Example:
```
base: ORIGINAL_OWNER/main
compare: YOUR_USERNAME/your-branch
```

If those look correct, continue.

---

## 4. Add a Title and a Short Message

Examples:

- Fix image handling in PDF generator  
- Add references section to YAML exporter  

This helps the owner understand what you changed.

---

## 5. Click “Create Pull Request”

You’re done.

The project owner can now:

- review your work  
- comment  
- ask for changes  
- or merge your branch into their project  

A PR is simply:

a structured request + a short conversation about your changes.

## Terminology: Some Important Git Concepts

Here are a few words you will see often when working with Git. They sound technical at first, but their meaning is quite simple once you see them in context.

**Origin**  
This is the name Git gives to your own online repository on GitHub (your fork). When you push changes, you normally push them to `origin`.

**Upstream**  
This refers to the original repository you forked from. Upstream is the place you send Pull Requests to if you want the owner to accept your updates.

**Staging**  
Staging means preparing your changes before saving them. When you run `git add`, you are “staging” your work — telling Git which files you want to include in your next commit.

**Commit / Committing**  
A commit is a saved snapshot of your work. After staging your files, you run `git commit` to save those staged changes in your branch. Think of it as pressing a “save progress” button for your project.

