name: Dokoola Backend Scaffolding CI/CD

on:
  push:
    branches: ["main"]
  pull_request:
    branches: ["main"]

jobs:
  scaffold:
    runs-on: ubuntu-latest
    name: Scaffold

    container: python

    steps:
      - uses: actions/checkout@v3

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Scafollding
        run: cp ./.env.prod ./.env && python manage.py scaffold
