# Wekan Adapter


## Overview

Wekan adapter is an adapter created to receive and collect information from task boards - Wekan canban.

To work, you need to get an API key. It can be obtained via interface using instructions.

To make the script work, you need to build and run the docker container after defining the configuration data in the environment file.
In the case of CI/CD - specify the data in variables.

For more detailed instructions, follow the [link](https://git.miem.hse.ru/394/scripts-templates/-/tree/python "Python project template").

## Main libraries, services and technologies

1. Python 3.8 / 3.10 - https://www.python.org/downloads/release/python-3814/
2. Docker - https://www.docker.com/
3. pydantic - https://pypi.org/project/pydantic/
4. mongoengine - http://mongoengine.org/
5. footprint-mongoengine - https://footprint.auditory.ru/pypi/
6. Wekan REST API - https://wekan.github.io/api/v2.71/
7. Gitlab CI/CD - https://docs.gitlab.com/ee/ci/

## API Routes

Method| Route                                                          |Description
------|----------------------------------------------------------------|---
POST  | `/users/login`                                                 |Auth
GET   | `/api/users`                                                   |Get all users
GET   | `/api/users/{user_id}`                                         |Get full user info
GET   | `/api/users/{user_id}/boards`                                  |Get all boards
GET   | `/api/boards/{board_id}`                                       |Get full board info
GET   | `/api/boards/{board_id}/lists`                                 |Get all lists from board
GET   | `/api/boards/{board_id}/custom-fields`                         |Get custom fields info
GET   | `/api/boards/{board_id}/lists/{list_id}/cards`                 |Get all cards from list
GET   | `/api/boards/{board_id}/lists/{list_id}/cards/{card_id}`       |Get full card info
GET   | `/api/boards/{board_id}/cards/{card_id}/comments`              |Get all card comments
GET   | `/api/boards/{board_id}/cards/{card_id}/comments/{comment_id}` |Get full comment info


## Expected data format

```json
[
    {
        "_id": "mongo_card_id",
        "users":["mongo_user_id", ...],
        "board_id": "board_id",
        "card_id": "card_id",
        "info":
        {
            "hours": "spent_time",
            "timestamp": "timestamp",
            "assignees": ["user_id", ...]
        },
        "status": "status",
        "completed": true/false,
        "last_activity": "timestamp"
    }
]
```

## Main functions

1. `get_list_cards` - get all cards from certain board;
2. `get_card_timestamp` - get card's completion time;
3. `get_complete_field_id` - get field id from board custom fields if it is completed;
4. `get_card_complete_status` - check completion status;
5. `get_users` - get all users from wekan;
6. `map_card_to_database` - map data from api to database format;
7. `get_updated_cards` - get cards with updated last-activity timestamp;
8. `save_users` - save users to database;
9. `get_card_last_activity` - get card last activity.

## Installation

To install adapter, you should clone this project by using command:
```
git clone https://git.miem.hse.ru/394/adapters/wekan.git
```

To work correctly, you need to install all the dependencies using `requirements.txt` by using command:
```
pip install --extra-index-url https://footprint.auditory.ru/pypi/simple -r requirements.txt
```


## Docker

If you are using docker, then first you need to build an image using the command:
```
docker build -t wekan .
```
To run the script you need to provide environment variables.

It is quite easy, because python-dotenv automatically parse `.env` files and OS environment for you.

After you need to run the container using command:
```
docker run --rm --env-file .env  wekan
```

