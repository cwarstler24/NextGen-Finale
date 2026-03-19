---
description: The Frying Saucer uses CI/CD pipelines, tooling, and automated testing to maintain the application. 
---

# CI/CD Developer’s Assistant Guide

The Frying Saucer uses CI/CD pipelines, tooling, and automated testing to maintain the application. Testing for The Frying Saucer has 425 automated tests that uses by GitHub Actions.

!!! info "info"
    You must be in the main directory of the repository to run tests. Tests run automatically in GitHub Actions on every push and on every branch.

## CI/CD Pipeline Overview

The CI/CD pipeline is responsible for automatically validating code quality, running tests, and managing dependencies.  

**CI/CD Pipeline**  
Automates linting, testing, and dependency management. Runs automatically on **every push to every branch**, including `main`.

**Linting**  
A form of **static code analysis**. Linting checks for code inconsistences, potential bugs, overall code structure, and code smells.

**Testing the Frontend and Backend Pipelines**  
Testing in this project is split between the frontend and backend so both layers are validated in CI. The frontend uses **Vitest** with the Vue toolchain to run fast component tests, while the backend uses **Pytest** for automated Python test execution. These test workflows run through **GitHub Actions** on every push, helping catch regressions before changes are merged.

## GitHub Actions Overview

There are **5 GitHub Actions** configured in the repository:

1. Frontend Tests  
2. Backend Tests  
3. Frontend Lint  
4. Backend Lint  
5. Automatic Dependency Submission  

!!! note "note"
    This includes 2 lint workflows, 2 test workflows, and 1 dependency automation workflow.

## Automatic Dependency Submission

Automatic dependency submission checks project dependencies for known issues and vulnerabilities. If a dependency issue is found a **pull request is automatically created on GitHub**. The pull request contains recommended dependency updates.

**Python Dependency Automation**  
 `submit-pypi` scans **all Python packages installed with `pip`**. It checks every package, every installed version, and uses **Dependabot** to generate pull requests when needed. **Dependabot** looks up dependency versions, detects known vulnerabilities, and upgrades automatically.

## Linting Tools

**Pylint**  
Pylint enforces python coding standards and checks for code smells, styling issues, and potential bugs.

**ESLint**
ESLint is used for frontend testing and it enforces JavaScript and Vue's best practices.

## Testing Tools

**Vitest**  
Vitest is a frontend testing tool that is built on Vite. It is an opened-sourced testing framework that provides fast test execution and an integrated development server.

**Pytest**
Pytest is used for backend testing and provides a simple, automated way to validate Python functionality as part of the CI workflow.
