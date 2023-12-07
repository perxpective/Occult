# Occult Development Notes

## Table of Contents
- [Occult Development Notes](#occult-development-notes)
  - [Table of Contents](#table-of-contents)
  - [Development Instructions](#development-instructions)

## Development Instructions
**Cloning the Repository**

To clone the repository, run the following command in your terminal:
```bash
git clone https://github.com/perxpective/Occult.git
```

**Switching to a New Branch**

All work should be done on the `dev` branch. To switch to the `dev` branch, run the following command:
```bash
git checkout dev
```

> ⚠ **WARNING**: Do not work on the `master` branch. The `master` branch is only for the final, working version of the project!

**Pulling the Latest Changes**

- Ensure that your delegated work is isolated on a separated branch.
- It is always good practice to pull the latest changes from the `dev` branch before you start working on your own branch. You should also pull periodically to ensure that your branch is up-to-date with the `dev` branch.

```bash
git pull
```

**Creating a New Branch**

There may be instances where separate branches need to be created for separate features. In this case, you can create a new branch with the following command:

```bash
git checkout -b <branch-name>
```

**Committing Changes**

- Changes are automatically tracked on your local machine. 
- To commit your changes to the repository, ssimply navigate to the Source Control tab in VSCode and click the checkmark icon to commit your changes. You will be prompted to enter a commit message. 
- Enter a short, descriptive message that describes the changes you made. 
- Then, click the checkmark icon again to push your changes to the repository.
- Remember to click on the Sync Changes button to push and pull changes from the remote repository.

Alternatively, you can commit your changes from the terminal. To do so, run the following commands:

```bash
git add .
git commit -m "<commit-message>"
git push
```

**Merging Branches**

- On the GitHub repository, you can create a pull request to merge your branch with the `dev` branch (or the `main` branch where necessary).
- Indicate the changes you made in the pull request and request a review from another team member.
- The team leader shall review the pull request and merge the branch if the changes are satisfactory.