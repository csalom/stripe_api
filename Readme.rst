========================
Stripe API
========================

Dependencies
------------

* Git.
* Python 3.9
* Virtualenv, pyenv or docker/docker-compose


Installation and run
--------------------

#. Clone project from repo ::

    mkdir ~/workspace/stripe_api
    cd stripe_api/
    git clone stripe_api_repo # TODO: ####

#. Setup and activate Python virtualenv ::

    pyenv virtualenv virtualenv_name
    pyenv activate virtualenv_name

#. Create configuration ::

    For testing purpose, the envs variables are set with a default value.
    You can change the values settings these env variables:
      - DEBUG
      - ALLOWED_HOSTS
      - DATABASE_NAME
      - DATABASE_USER
      - DATABASE_PASSWORD
      - DATABASE_HOST
      - DATABASE_PORT
      - DATABASE_CONN_MAX_AGE
      - STRIPE_API_KEY
      - STRIPE_WEBHOOK_SECRET
      - LOG_FILE
      - LOG_LEVEL
      - DJANGO_LOG_LEVEL


#. Create data base ::

    You will need a postgres DB, by default called 'stripe' and with user/password 'postgres'.
    This values can be changed with the envs variables. Then you can set up the DB applying the migrations.
    You may want to create a super user to be able to access to the admin page and take a look on the data that
    will be generated using the api.

    python manage.py migrate
    python manage.py createsuperuser

#. Run local server an check tests ::

    The tests are developed using pytest. To execute them, move to the source directory and do:
    pytest



#. Docker installation ::

    The project is ready to use/deploy using docker and docker-compose. On the docker-compose.yml file you will find the
    the required commands and environment variables. You can change the default values there and then run the project:

    docker-compose up stripe_api

