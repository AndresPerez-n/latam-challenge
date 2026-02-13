# Challenge

## Model decision

I went with the Logistic Regression using the top 10 features and class balancing. Both XGBoost and LR gave pretty much the same results, so I picked the simpler one since it doesn't need any extra library and trains faster.

The class balancing part was key — without it the model just predicts everything as "not delayed" which is useless. With balanced weights it actually catches delays (recall above 0.60 for class 1).

Also found a bug in model.py: `Union()` should be `Union[]`, parentheses vs brackets.

## API

Built the predict endpoint with FastAPI. Added pydantic validators so it rejects bad input (wrong month, invalid airline, etc) with a 400 status. The model loads and trains when the app starts up.

## Deploy

Used GCP Cloud Run with a Docker container. Ran the stress test with 100 concurrent users for 60 seconds — around 9500 requests with zero failures.

## CI/CD

Set up GitHub Actions. CI runs model and API tests on every push and PR. CD builds the docker image and deploys to Cloud Run when we push to main.
