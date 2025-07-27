
# NHL Player-to-Player: Development and Deployment Roadmap

This document outlines a roadmap for developing, deploying, and maintaining your NHL Player-to-Player web application. It includes suggestions for code consolidation, project structure, and a step-by-step guide to deploying your application for free.

## 1. Code Consolidation and Project Structure

Your current project structure is a bit fragmented, with multiple backends and an old client. To make your project easier to manage and deploy, I recommend the following changes:

*   **Consolidate your backend:** You currently have a Node.js/Express backend and a Python/FastAPI backend. I recommend consolidating them into one. Since your `api_server.py` is more complete, I suggest using Python and FastAPI for your backend.
*   **Simplify your project structure:** I recommend a monorepo-like structure with a `frontend` and `backend` directory at the root. This will make it easier to manage your code and deploy your application.

Here's a suggested project structure:

```
/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ... (your other Python files)
├── frontend/
│   ├── NHL_Player-to-Player/
│   │   ├── src/
│   │   └── ... (your Vue.js files)
└── ... (your other files)
```

**Action Items:**

1.  Move the contents of your `client/NHL_Player-to-Player` directory to a new `frontend` directory at the root of your project.
2.  Move the contents of your `database_test` directory to a new `backend` directory at the root of your project.
3.  Rename `api_server.py` to `main.py`.
4.  Create a `requirements.txt` file in your `backend` directory and add your Python dependencies to it (e.g., `fastapi`, `uvicorn`, `requests`, `sqlite3`).
5.  Delete the `backend` and `old_client` directories.

## 2. Backend Improvements

Your Python/FastAPI backend is a great start. Here are a few suggestions for improving it:

*   **Asynchronous tasks:** For long-running tasks like web scraping or data processing, consider using an asynchronous task queue like [Celery](https://docs.celeryq.dev/en/stable/) with [Redis](https://redis.io/). This will prevent your API from timing out and improve the user experience.
*   **Database migrations:** As you develop your application, your database schema will likely change. To manage these changes, I recommend using a database migration tool like [Alembic](https://alembic.sqlalchemy.org/en/latest/).
*   **Environment variables:** To keep your code clean and secure, I recommend using environment variables for configuration. You can use a library like [python-dotenv](https://pypi.org/project/python-dotenv/) to manage your environment variables.

## 3. Deployment

Here's a step-by-step guide to deploying your application for free using Vercel for the frontend and Render for the backend and database.

### Frontend (Vercel)

1.  **Push your code to GitHub:** Create a new repository on GitHub and push your code to it.
2.  **Create a Vercel account:** Sign up for a free account on [Vercel](https://vercel.com/).
3.  **Create a new project:** Create a new project on Vercel and connect it to your GitHub repository.
4.  **Configure your project:** Vercel will automatically detect that you're using Vue.js and configure the build settings for you. You'll need to set the root directory to `frontend/NHL_Player-to-Player`.
5.  **Deploy:** Click the "Deploy" button to deploy your frontend.

### Backend (Render)

1.  **Create a Render account:** Sign up for a free account on [Render](https://render.com/).
2.  **Create a new web service:** Create a new web service on Render and connect it to your GitHub repository.
3.  **Configure your web service:**
    *   **Name:** Give your web service a name (e.g., `nhl-player-to-player-backend`).
    *   **Region:** Choose a region that's close to your users.
    *   **Branch:** Choose the branch you want to deploy (e.g., `main`).
    *   **Root Directory:** `backend`
    *   **Build Command:** `pip install -r requirements.txt`
    *   **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4.  **Create a new database:** Create a new PostgreSQL database on Render.
5.  **Connect your backend to your database:** Add the database URL to your backend's environment variables.
6.  **Deploy:** Click the "Create Web Service" button to deploy your backend.

## 4. CI/CD

To automate the deployment of your application, you can set up a CI/CD workflow using GitHub Actions. This will automatically deploy your application whenever you push changes to your repository.

Here's a sample GitHub Actions workflow that you can use:

```yaml
name: Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: amondnet/vercel-action@v20
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
          working-directory: frontend/NHL_Player-to-Player

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: akhileshns/heroku-deploy@v3.12.12
        with:
          heroku_api_key: ${{ secrets.HEROKU_API_KEY }}
          heroku_app_name: 'nhl-player-to-player-backend'
          heroku_email: ${{ secrets.HEROKU_EMAIL }}
          usedocker: true
          docker_heroku_process_type: web
          docker_build_context: backend
          appdir: backend
```

**Note:** This is just a sample workflow. You'll need to replace the secrets with your own.

## Conclusion

This roadmap provides a high-level overview of the steps you can take to get your application from your local machine to the web. By following these steps, you'll be able to create a tangible product that you can share with your friends and potential employers. Good luck!
