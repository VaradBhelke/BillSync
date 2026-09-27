# BillSync – Bill & Subscription Manager

BillSync is an individual CCD (Cloud Computing and DevOps) CCA 2 mini-project.
It is a server-rendered Flask application that lets users add and view bills and
subscriptions, exposes a JSON API, provides a health route, and displays the
running Git commit ID.

## CCA 2 requirements covered

- Form with POST request and input validation
- JSON API: `GET /api/bills`
- Health route: `GET /health`
- Footer showing the current commit ID
- 5 automated pytest tests
- flake8 linting
- Docker container
- GitHub Actions CI/CD
- Docker smoke test before deployment
- Render deployment through a GitHub Secret deploy hook
- Render Auto-Deploy disabled

## Project structure

```text
BillSync/
├── .github/workflows/ci-cd.yml
├── static/style.css
├── templates/index.html
├── app.py
├── test_app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── render.yaml
└── README.md
```

## Run locally

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

Install:

```bash
pip install -r requirements.txt
```

Run tests and lint:

```bash
pytest -v
flake8 --max-line-length=100 --exclude=venv .
```

Start the app:

```bash
python app.py
```

Open `http://localhost:5000`.

## Docker

```bash
docker build --build-arg GIT_SHA=local -t billsync .
docker run -p 5000:5000 billsync
```

Health check:

```bash
curl http://localhost:5000/health
```

## CI/CD flow

```text
Git push / Pull Request
        ↓
Lint + Tests
        ↓
Docker Build
        ↓
Docker Smoke Test (/health)
        ↓
Deploy to Render (main only)
        ↓
Live BillSync application
```

The deploy job depends on the build job, and the build job depends on the
test job. Therefore a failed lint/test/build step prevents deployment.

## GitHub + Render setup

1. Create a public GitHub repository named `BillSync`.
2. Push this project to your own repository.
3. In Render, create a Docker Web Service connected to the repository.
4. Turn Render Auto-Deploy **off**.
5. Copy the Render Deploy Hook URL.
6. In GitHub: Settings → Secrets and variables → Actions.
7. Add a repository secret named `RENDER_DEPLOY_HOOK`.
8. Push to `main` and watch the Actions workflow.
9. The live footer should show the short commit ID.

Never commit passwords, API keys, or the Render deploy hook.

## Failure-demo procedure

For the required CCA screenshot, create a branch and temporarily break a test.
Push the branch and capture the red test run. The deploy job must not run.

Then fix the test, push again, merge to `main`, and capture the green pipeline.
Finally open the live site and capture the footer showing the same commit ID.

## Limitations

Bill data is stored in memory for the CCA mini-project. Restarting the server
clears the data. A production version could use PostgreSQL or DynamoDB.

## CCA report links to fill

- GitHub repository: `<paste your public repository URL>`
- Live application: `<paste your Render URL>`
- GitHub Actions: `<paste your Actions URL>`

