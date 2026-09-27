# CCA 2 Report Notes – BillSync

Use this content to prepare the required 4–6 page PDF.

## 1. Problem statement and features

People often manage recurring bills and subscriptions through memory, notes,
or multiple apps. BillSync provides one simple place to record a bill, amount,
due date, category, payment status, and notes.

Features:
- Add a bill/subscription through a validated form.
- View all saved bills.
- Calculate total unpaid amount and overdue count.
- Delete a bill.
- Access bill data through `/api/bills`.
- Check application health through `/health`.
- Show the running commit ID in the footer.

## 2. Architecture and pipeline

Application architecture:

Browser → Flask/Jinja2 → In-memory bill store

CI/CD:

Git push/PR → Lint + pytest → Docker build → Docker `/health` smoke test
→ Render deploy on main → Live application

## 3. Pipeline stages

### Stage 1 – Lint and Test
GitHub Actions installs Python dependencies, runs flake8, and runs pytest.
Screenshot: paste the green test job here.

### Stage 2 – Docker Build
The workflow builds the application into a Docker image and starts it.
Screenshot: paste the Docker build job here.

### Stage 3 – Smoke Test
The workflow calls `/health`. A successful response proves the container is
running and the application responds over HTTP.
Screenshot: paste the successful smoke-test log here.

### Stage 4 – Deploy
Only a push to `main` can run the deploy job. The deploy job requires the build
job to pass and triggers Render using the `RENDER_DEPLOY_HOOK` GitHub Secret.
Screenshot: paste the successful deploy job here.

### Stage 5 – Verify
Open the Render URL and show the footer with the short commit ID.
Screenshot: paste the live site here.

## 4. Failure demo

Temporarily make one automated test fail on a feature branch. Push it and show
the failed test job. Because later jobs depend on earlier jobs, deployment does
not run. Fix the test, merge to main, and show the green pipeline.

Screenshot 1: failed test run.
Screenshot 2: deploy skipped.
Screenshot 3: successful corrected run.

## 5. Challenges faced and learning

Suggested points to discuss:
- Converting a static application into a server-rendered Flask application.
- Designing validation for user-submitted bill data.
- Writing meaningful automated tests.
- Understanding the dependency chain between CI and CD jobs.
- Building and testing the Docker image.
- Keeping the Render deploy hook in GitHub Secrets instead of source code.
- Understanding how Git branches and pull requests support safe feature work.

## 6. Required links

GitHub repository: <fill after creating your repository>
Live application: <fill after Render deployment>
Actions page: <fill after first workflow run>

## 7. Title-page details

Student Name: <fill>
PRN: <fill>
Roll No. / Panel: <fill>
Project Title: BillSync – Bill & Subscription Manager
Date of Submission: <fill>
