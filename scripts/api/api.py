from typing import Union

import requests
import logging

from ..config import config
from .responses import *


class LoginError(Exception):
    """Raise when get error during log-in"""

    def __init__(self, route: str, error: InlineApiError):
        self.route = route
        self.error = error
        super().__init__(
            f"Error captured on route '{self.route}'. "
            f"Reason: '{self.error.reason}'. "
        )


class RouteError(Exception):
    """Raise when get invalid status code for a route"""

    def __init__(self, route: str, status: int):
        self.route = route
        self.status = status
        super().__init__(
            f"Error captured on route '{self.route}' with status '{self.status}'. "
        )


def login(username: str, 
          password: str) -> InlineToken:
    """
    Authorization in Wekan service. Generates token.

    :param username: username
    :param password: password
    :return: token with expiration date
    """
    headers = {
        'Content-type': 'application/json',
        'Accept': '*/*'
    }
    body = {
        'username': username,
        'password': password
    }
    route = "/users/login"
    logging.info(f"Get token from '{config.WEKAN_BASE_URL}'")
    response = requests.post(f'{config.WEKAN_BASE_URL}{route}', json=body, headers=headers)
    if response.status_code != 200:
        raise LoginError(route, InlineApiError(**response.json()))
    return InlineToken(**response.json())


def send_get(route: str, 
             token: Union[str, InlineToken]) -> requests.Response:
    """
    Simple request to the API. API docs said that there is no error.

    :param route: requested route
    :param token: token
    :return: raw response
    """
    headers = {
        'Authorization': f'Bearer {token.token if isinstance(token, (InlineToken,)) else token}',
        'Content-type': 'application/json',
    }
    response = requests.get(f'{config.WEKAN_BASE_URL}{route}', headers=headers)
    if response.status_code != 200:
        raise RouteError(route, response.status_code)
    if not response.content:
        raise RouteError(route, 204)
    return response


def get_boards_from_user(user: Union[str, InlineUser, User], 
                         token: Union[str, InlineToken]) -> List[InlineBoard]:
    """
    Get all boards from specified user.

    :param user: user ID (as string) or User object
    :param token: token
    :return: list of boards IDs
    """
    user_id = user.id if isinstance(user, (InlineUser, User)) else user

    response = send_get(f'/api/users/{user_id}/boards', token)
    return [InlineBoard(**i) for i in response.json()]


def get_board(board: Union[str, InlineBoard], 
              token: Union[str, InlineToken]) -> InlineBoard:
    """
    Get full board information.

    :param board: board ID (as string) or Board object
    :param token: token
    :return: board info
    """
    board_id = board.id if isinstance(board, (InlineBoard,)) else board

    response = send_get(f'/api/boards/{board_id}', token)
    return InlineBoard(**response.json())


def get_all_lists(board: Union[str, InlineBoard], 
                  token: Union[str, InlineToken]) -> List[InlineList]:
    """
    Get all lists from specified board.

    :param board: board ID (as string) or Board object
    :param token: token
    :return: list of Wekan lists IDs
    """
    board_id = board.id if isinstance(board, (InlineBoard,)) else board

    response = send_get(f'/api/boards/{board_id}/lists', token)
    return [InlineList(**i) for i in response.json()]


def get_all_custom_fields(board: Union[str, InlineBoard], 
                          token: Union[str, InlineToken]) -> List[InlineCustomField]:
    """
    Get custom fields for specified board.

    :param board: board ID (as string) or Board object
    :param token: token
    :return: list of custom fields
    """
    board_id = board.id if isinstance(board, (InlineBoard,)) else board

    response = send_get(f'/api/boards/{board_id}/custom-fields', token)
    return [InlineCustomField(**i) for i in response.json()]


def get_all_cards(board: Union[str, InlineBoard], 
                  list_: Union[str, InlineList],
                  token: Union[str, InlineToken]) -> List[InlineCard]:
    """
    Get all cards from list.

    :param board: board ID (as string) or Board object
    :param list_: list ID (as string) or List object
    :param token: token
    :return: list of cards
    """
    board_id = board.id if isinstance(board, (InlineBoard,)) else board
    list_id = list_.id if isinstance(list_, (InlineList,)) else list_

    response = send_get(f'/api/boards/{board_id}/lists/{list_id}/cards', token)
    return [InlineCard(**i) for i in response.json()]


def get_card(board: Union[str, InlineBoard], 
             list_: Union[str, InlineList], 
             card: Union[str, InlineCard, Card],
             token: Union[str, InlineToken]) -> Card:
    """
    Get full card info.

    :param board: board ID (as string) or Board object
    :param list_: list ID (as string) or List object
    :param card: card ID (as string) or Card object
    :param token: token
    :return: card info
    """
    board_id = board.id if isinstance(board, (InlineBoard,)) else board
    list_id = list_.id if isinstance(list_, (InlineList,)) else list_
    card_id = card.id if isinstance(card, (InlineCard, Card)) else card

    response = send_get(f'/api/boards/{board_id}/lists/{list_id}/cards/{card_id}', token)
    return Card(**response.json())


def get_all_comments(board: Union[str, InlineBoard], 
                     card: Union[str, InlineCard, Card],
                     token: Union[str, InlineToken]) -> List[InlineComment]:
    """
    Get all comments for the card.

    :param board: board ID (as string) or Board object
    :param card: card ID (as string) or Card object
    :param token: token
    :return: list of comments
    """
    board_id = board.id if isinstance(board, (InlineBoard,)) else board
    card_id = card.id if isinstance(card, (InlineCard, Card)) else card

    response = send_get(f'/api/boards/{board_id}/cards/{card_id}/comments', token)
    return [InlineComment(**i) for i in response.json()]


def get_comment(board: Union[str, InlineBoard], 
                card: Union[str, InlineCard, Card],
                comment: Union[str, InlineComment, Comment], 
                token: Union[str, InlineToken]) -> Comment:
    """
    Get full comment info.

    :param board: board ID (as string) or Board object
    :param card: card ID (as string) or Card object
    :param comment: comment ID (as string) or Comment object
    :param token: token
    :return: comment info
    """
    board_id = board.id if isinstance(board, (InlineBoard,)) else board
    card_id = card.id if isinstance(card, (InlineCard, Card)) else card
    comment_id = comment.id if isinstance(card, (InlineComment, Comment)) else comment

    response = send_get(f'/api/boards/{board_id}/cards/{card_id}/comments/{comment_id}', token)
    return Comment(**response.json())


def get_all_users(token: Union[str, InlineToken]) -> List[InlineUser]:
    """
    Get all users in service.

    :param token: token
    :return: list of users
    """
    response = send_get(f'/api/users', token)
    return [InlineUser(**i) for i in response.json()]


def get_user(user: Union[str, InlineUser, User], 
             token: Union[str, InlineToken]) -> User:
    """
    Get full user info.

    :param user: user ID (as string) or User object
    :param token: token
    :return: user info
    """
    user_id = user.id if isinstance(user, (InlineUser, User)) else user

    response = send_get(f'/api/users/{user_id}', token)
    return User(**response.json())
