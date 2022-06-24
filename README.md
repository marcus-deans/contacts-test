# contacts-test
New contacts backend in single script

Enter with `cd contacts-test`, then call `poetry install` and `poetry shell`. The FastAPI server is specified in `cd contacts-test/app` in file `main.py`. Can run directly by invoking `uvicorn main:app --reload` from this folder.

Deploy to Heroku by creating Docker container for the project. First `cd contacts-test` and run `docker build . -t contacts`. Then push to Heroku server (with Heroku CLI installed) using `docker ps` then `heroku  container:login` then `heroku container:push web` then `heroku continer:release web`.
