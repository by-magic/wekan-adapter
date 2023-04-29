import datetime
import logging
import sys
from typing import Dict, List, Tuple, Union

from scripts import api, database

# to get status use `LIST_NAMES_TO_STATUS.get(name, database.StatusEnum.UNKNOWN)`
LIST_NAMES_TO_STATUS = {
    "новые": database.StatusEnum.NEW,
    "в работе": database.StatusEnum.IN_PROGRESS,
    "можно проверять": database.StatusEnum.REVIEW,
    "выполнено": database.StatusEnum.COMPLETED,
    "архив": database.StatusEnum.ARCHIVE,
}


def get_list_cards(board: Union[str, api.InlineBoard],
                   list_: Union[str, api.InlineList],
                   token: Union[str, api.InlineToken]) -> List[api.Card]:
    """
    Get cards from board's list.

    :param board: board ID (as string) or Board object
    :param list_: list ID (as string) or List object
    :param token: token
    :return: list of cards
    """
    all_cards = []

    list_cards = api.get_all_cards(board, list_, token)
    for card in list_cards:
        try:
            all_cards.append(api.get_card(board, list_, card, token))
        except api.RouteError as e:
            if e.status != 204:
                raise e
    return all_cards


def get_card_timestamp(board: Union[str, api.InlineBoard],
                       card: Union[str, api.Card],
                       token: Union[str, api.InlineToken]) -> Union[datetime.datetime, None]:
    """
    Get card's completion timestamp.

    :param board: board ID (as string) or Board object
    :param card: card ID (as string) or Card object
    :param token: token
    :return: timestamp
    """
    all_comments = api.get_all_comments(board, card, token)
    timestamp = None
    if all_comments:
        try:
            for j in all_comments:
                if j.comment.find('Часы успешно отправлены в кабинет.') != - 1:
                    current_comment = api.get_comment(board, card, j.id, token)
                    timestamp = current_comment.created_at
        except api.RouteError as e:
            if e.status != 204:
                raise e
    return timestamp


def get_complete_field_id(board: Union[str, api.InlineBoard],
                          token: Union[str, api.InlineToken]) -> Union[str, None]:
    """
    Get complete field id from board custom fields.

    :param board: board ID (as string) or Board object
    :param token: token
    :return: complete field id
    """
    custom_fields = api.get_all_custom_fields(board, token)
    for field in custom_fields:
        if field.name == "Выполнено":
            return field.id
    return None


def get_card_complete_status(complete_field_id: str,
                             card: api.Card) -> bool:
    """
    Check completion status.

    :param complete_field_id: complete field ID (as string)
    :param card: card ID (as Card object)
    :return: bool value of complete field status
    """
    for field in card.custom_fields:
        if field.id == complete_field_id:
            return bool(field.value)
    return False


def get_users(token: Union[str, api.InlineToken]) -> Dict[str, api.User]:
    """
    Get all users.

    :param token: token
    :return: dictionary of users
    """
    users = {}
    for user in api.get_all_users(token):
        users[user.id] = api.get_user(user, token)
    return users


def map_card_to_database(board: api.InlineBoard,
                         list_: api.InlineList,
                         card: api.Card,
                         complete_field_id: str,
                         token: Union[str, api.InlineToken]) -> database.Card:
    """
    Map data from api to database.

    :param board: board ID (as Board object)
    :param list_: list ID (as List object)
    :param card: card ID (as Card object)
    :param complete_field_id: field ID (as string)
    :param token: token
    :return: card as database object
    """
    search_card = database.Card.objects(board_id=board.id, card_id=card.id)
    db_card = search_card[0] if search_card else database.Card(board_id=board.id, card_id=card.id)

    db_card.status = LIST_NAMES_TO_STATUS.get(list_.title, database.StatusEnum.UNKNOWN)
    db_card.completed = get_card_complete_status(complete_field_id, card)
    db_card.last_activity = card.date_last_activity

    db_card.info = database.CardInfo()
    db_card.info.title = card.title
    db_card.info.hours = card.spent_time if card.spent_time is not None and card.spent_time < sys.maxsize else 0
    db_card.info.timestamp = get_card_timestamp(board, card, token)
    db_card.info.assignees = card.assignees
    db_card.info.start_at = card.start_at
    db_card.info.due_at = card.due_at
    db_card.info.end_at = card.end_at
    db_card.info.received_at = card.received_at

    return db_card


def get_updated_cards(board: api.InlineBoard,
                      cards_last_activity: Dict[Tuple[str, str], datetime.datetime],
                      token: Union[str, api.InlineToken]) -> List[database.Card]:
    """
    Get cards with updated last-activity timestamp.

    :param board: board ID (as Board object)
    :param cards_last_activity: dictionary of last activity for each card
    :param token: token
    :return: list of cards
    """
    updated_cards = []
    complete_field_id = get_complete_field_id(board, token)
    board_lists = api.get_all_lists(board, token)
    for list_ in board_lists:
        for card in get_list_cards(board, list_, token):
            if (card.board_id, card.id) not in cards_last_activity or \
                    cards_last_activity[(card.board_id, card.id)].utctimetuple() != card.date_last_activity.utctimetuple() or \
                    not database.Card.objects(card_id=card.id)[0].info.title:
                updated_cards.append(map_card_to_database(board, list_, card, complete_field_id, token))
    return updated_cards


def map_users_with_db(board: api.InlineBoard,
                        db_cards: List[database.Card],
                        token: api.InlineToken) -> None:
    """
    Save users to database.

    :param board: board ID (as Board object)
    :param db_cards: list of cards
    :param token: token
    :return: None
    """
    for card in db_cards:
        assignees = []
        for assignee in card.info.assignees:
            user = api.get_user(assignee, token)
            if user.emails:
                slug = user.emails[0].address.split("@")[0]
                search_slug_user = database.User.objects(slug=slug)
                if search_slug_user:
                    assignees.append(search_slug_user[0])
                else:
                    logging.warning('No such user in database.')
        card.users = assignees
        try:
            card.save()
        except OverflowError as e:
            logging.warning(e.args[0])
    logging.info(f"{len(db_cards)} card(s) from board '{board.id}' saved")


def get_cards_last_activity() -> Dict[Tuple[str, str], datetime.datetime]:
    """
    Get card last activity.

    :return: dictionary of last activity for each card
    """
    cards_last_activity = {}
    for card in database.Card.objects():
        cards_last_activity[(card.board_id, card.card_id)] = card.last_activity
    return cards_last_activity


def get_cards_activity_board(board: api.InlineBoard) -> Dict[Tuple[str, str], datetime.datetime]:
    """
    Get card last activity.

    :param board: board ID (as Board object)
    :return: dictionary of last activity for each card
    """
    cards_activity = {}
    for card in database.Card.objects(board_id__exact=board.id):
        cards_activity[(board.id, card.card_id)] = card.last_activity
    return cards_activity
