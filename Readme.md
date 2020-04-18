Project setup:

`$ cp .env.template .env`

`$ docker-compose up`

Running tests:

`$ docker-compose run backend python manage.py test`

API endpoints documentation available at:

http://localhost:8000/api/

### Answer for Task 2
For now mails are being sent synchronously and user has to wait for response until all mails will be sent 
which isn't very optimal.

Better approach is to use Celery and delegate sending emails from main thread to worker which can send them asynchronously.
