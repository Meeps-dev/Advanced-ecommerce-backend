# CI/CD Runbook

This project uses GitHub Actions for continuous integration and branch-based deployment to Render.

## Branch flow

- `develop` maps to the development environment.
- `staging` maps to the staging environment.
- `main` maps to production.

Recommended promotion flow:

1. Create a feature branch from `develop`.
2. Open a pull request into `develop`.
3. Merge `develop` into `staging` after validation.
4. Merge `staging` into `main` for production release.

## Workflows

The repository already includes these workflows:

- [CI](../.github/workflows/ci.yml)
- [Deploy dev](../.github/workflows/deploy-dev.yml)
- [Deploy staging](../.github/workflows/deploy-staging.yml)
- [Deploy production](../.github/workflows/deploy-prod.yml)

### CI workflow

The CI workflow runs on pull requests and pushes to `develop`, `staging`, and `main`.

It validates the project in stages:

- unit tests
- integration tests
- e2e tests

If any stage fails, deployment should not proceed.

### Deploy workflows

- `deploy-dev.yml` runs for `develop` and deploys to the Render dev service.
- `deploy-staging.yml` runs for `staging` and deploys to the Render staging service.
- `deploy-prod.yml` runs for `main` and deploys to the Render production service.

Production deploys should remain protected by a GitHub Environment approval gate.

## Render setup

Each environment should have its own Render service and environment configuration.

Required runtime values typically include:

- `DATABASE_URL`
- `REDIS_URL`
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`
- `SECRET_KEY`
- `RESEND_API_KEY`
- `PAYSTACK_SECRET_KEY`
- `SENTRY_DSN`

Production and staging should run with `SEED_DATA=false`.

## Local promotion workflow

Use this sequence from your laptop:

1. Pull the latest changes.
2. Work on a feature branch.
3. Push the feature branch to GitHub.
4. Open a pull request into `develop`.
5. After validation, promote `develop` to `staging`.
6. After staging approval, promote `staging` to `main`.

Avoid direct pushes to protected branches.

## Release checks

After each deploy, verify:

- `/api/v1/health/db`
- login or auth flow
- one read endpoint from the catalog or orders domain

If a production release fails, redeploy the last known good commit in Render and re-run the smoke checks.

## Troubleshooting

- If CI fails, inspect the failing job first and fix the test or environment issue before retrying the deploy.
- If Render deploys but the service is unhealthy, confirm environment variables and database connectivity.
- If production deploys are blocked, check the GitHub Environment approval settings for `production`.
