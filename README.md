# Condensate Backend

*Note: this is the backend service for Condensate, a different method of brainstorming. To learn more about Condensate, you can visit the frontend GitHub repo [here](https://github.com/CondensateCrew/Condensate).*

## Introduction

This repo hosts the backend service for Condensate, which is a brainstorming app. The backend is responsible for maintaining databases, making API calls to external services, and communicating with the frontend via RESTful API endpoints.

## Tech Stack

- Python (3.7.6) with pip (19.2.3)
- Flask (1.1.1)
- PostgreSQL (11.5)
- SQLAlchemy (1.3.13)
- Pytest (5.3.5)

## Getting started

#### Install necessary dependencies

*Note: This project is built on Flask, which requires Python. For more information about installing Python, see [here](https://www.python.org/). Pip is used for package management.*

- From within the project directory, enter the python virtual envionment using `source venv/bin/activate`
- Install necessary packages using `pip3 install -r requirements.txt`

#### Set up local database

This project uses a PostgreSQL database. Ensure you have Postgres installed and create a new database. Naming convention can be changed, however to get up and running as quickly as possible, we recommend naming the database `condensate_dev`. The path to the database needs to be specified in the environment variables (see the *Setting Environment Variables* section below).

#### Setting Environment Variables

For now, environment variables must be set manually for new sessions using the following commands:
```
export FLASK_APP="run.py"
export APP_SETTINGS="development"
export DATABASE_URL="postgresql://localhost/condensate_dev"
export FLASK_ENV='development'
```
This will be automated in the future.

#### Migrate

To migrate initially, the following commands need to be run:
```
python3 manage.py db init
python3 manage.py db migrate
python3 manage.py db upgrade
```
For any changes to models or schema afterward, only the last 2 commands need to be run.

#### API Keys

This project uses the [Twinword Dictionary API](https://www.twinword.com/api/word-dictionary.php). Twinword utilizes the [RapidAPI Marketplace](https://rapidapi.com/) for providing api keys. Once an api key is obtained, it must be specified in a `.env` file in the root directory of the project. For security reasons, this file should NOT be included in version control. Simply create an empty `.env` file and add the following: `RAPID_API_KEY="your_key_here"`. This key is accessed using `os.getenv('RAPID_API_KEY')`.

#### Running a Local Server

***Reminder: environment variables must be set prior to running server.***

To start the server, use `flask run` from the root directory. Requests can then be made to `localhost:5000`.

## Endpoints

#### Create a new user:

Sample Request:
```
POST /users

Body:

{
  "first_name": "Keanu",
  "last_name": "Reeves",
  "email": "kreeves@example.com",
  "password": "supersecurepassword"
}
```

Sample Successful Response:
```
Status: 201

{
  "id": 8,
  "first_name": "Keanu",
  "last_name": "Reeves",
  "email": "kreeves@example.com",
  "token": "c1e9a92195d98380747159598983bf96",
  "date_created": "Tue, 25 Feb 2020 17:47:50 GMT",
  "date_modified": "Tue, 25 Feb 2020 17:47:50 GMT"
}
```

Error Response:
```
Status: 400

{
  "message": "A user with this email already exists."
}
```
OR
```
Status: 400

{
  "message": "Missing parameter."
}
```

#### Login:

Sample Request:
```
POST /login

Body:

{
  "email": "kreeves@example.com",
  "password": "supersecurepassword"
}
```

Sample Successful Response:
```
Status: 303

{
  "token": "c1e9a92195d98380747159598983bf96",
  "first_name": "Keanu",
  "last_name": "Reeves"
}
```

#### Access user information (e.g. for the dashboard):

Sample Request:
```
POST /dashboard

Body:

{
  "token": "c1e9a92195d98380747159598983bf96"
}
```

Sample Successful Response:
```
Status: 200

{
  "user": {
      "id": 8,
      "first_name": "Keanu",
      "last_name": "Reeves",
      "email": "kreeves@example.com"
  },
  "brainstorms": [],
  "actions": [
    {
      "id": 1,
      "action": "Create an App"
    },
    {
      "id": 2,
      "action": "Write a Story"
    },
    {
      "id": 3,
      "action": "Plan a Lesson"
    },
    {
      "id": 4,
      "action": "Make a Recipe"
    },
    {
      "id": 5,
      "action": "Write a Song"
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "Education"
    },
    {
      "id": 2,
      "name": "Technology"
    },
    {
      "id": 3,
      "name": "Environment"
    },
    {
      "id": 4,
      "name": "Food"
    },
    {
      "id": 5,
      "name": "Music"
    }
  ]
}
```

Error Response:
```
Status: 404

{
  "message": "Could not find a user with that token."
}
```

#### Retrieve words and sentences for a new brainstorming session:

Sample Request:
```
POST /game_setup

Body:

{
  "token": "c1e9a92195d98380747159598983bf96"
}
```

Sample Successful Response (includes 64 words with sentences):
```
Status: 200

[
    {
        "word": "wife",
        "sentence": "Carol is the first wife of Danny, and the mother of Jamie."
    },
    {
        "word": "map",
        "sentence": "One centimeter on the map represents one kilometer of distance on the ground."
    },
    {
        "word": "movie",
        "sentence": "A camcorder was used to film the movie."
    },
    {
        "word": "insect",
        "sentence": "Ant is a hard working insect."
    },
    {
        "word": "bath",
        "sentence": "How do you clean the bath with a piddling short shower hose "
    },
    ...
]
```

Error Response:
```
Status: 400

{
  "error": "Missing token."
}
```
OR
```
Status: 404

{
  "error": "User not found."
}
```

#### Save a user idea:

Sample Request:
```
POST /ideas

Body:

{
	"idea": "Test idea for Keanu Reeves",
	"id": "c1e9a92195d98380747159598983bf96",
	"action": "Create an App",
	"isGenius": "False",
	"question": "Create an app about learning to code",
	"categories": [{"name": "Education"}, {"name": "Technology"}]
}
```

Sample Successful Response:
```
Status: 200

{
  "success": "Create an app about learning to code idea for Keanu Reeves has been successfully created!"
}
```

Error Response:
```
Status: 400

{
  "error": "Missing parameters."
}
```
OR
```
Status: 404

{
  "error": "User not found."
}
```
OR
```
Status: 400

"Create an app about learning to code idea already exists in the database for Keanu Reeves."
```

#### Delete a user idea:

Sample Request:
```
DELETE /ideas

Body:

{
  "token": "c1e9a92195d98380747159598983bf96",
  "idea_id": 2
}
```

Sample Successful Response:
```
Status: 204
```

Error Response:
```
Status: 400

{
  "error": "Missing parameters."
}
```
OR
```
Status: 404

{
  "error": "Idea not found."
}
```
OR
```
Status: 404

{
  "error": "User not found."
}
```

#### Create a custom user action:

Sample Request:
```
POST /actions

Body:

{
  "token": "c1e9a92195d98380747159598983bf96",
  "action": "Write a screenplay"
}
```

Sample Successful Response:
```
{
  "id": 2,
  "action": "Write a screenplay",
  "user_id": 8
}
```

Error Response:
```
Status: 404

{
  "message": "You already have that action!"
}
```
OR
```
Status: 404

{
  "message": "Invalid user token."
}
```

#### Seed database with random words and default actions and categories:

Request:
```
GET /seed
```

Reponse:
```
{
  "Words Added": 441,
  "Actions Added": 5,
  "Categories Added": 5
}
```

## Database Schema

![]()

## Project Board

*Note: the project board below is shared by frontend and backend sides of the project.*

[GitHub Project Board](https://github.com/orgs/CondensateCrew/projects/1)

## Core Contributors (Backend Only)

[Graham Thompson](https://github.com/grwthomps)  
[Ryan Hantak](https://github.com/rhantak)
