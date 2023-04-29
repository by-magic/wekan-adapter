from scripts.config import config
from scripts.api import api
from scripts import adapter, database

import logging
import logging.handlers


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.handlers.RotatingFileHandler(
                filename="log.log", 
                mode="a",
                maxBytes=5*1024*1024,
                backupCount=2,
                encoding=None,
                delay=0
            ),
            logging.StreamHandler()
        ]
    )

    logging.info(f"Program started")

    database.connect(
        username=config.MONGO_USER,
        password=config.MONGO_PASSWORD,
        ip=config.MONGO_HOST,
        port=config.MONGO_PORT,
        db=config.MONGO_DB
    )

    token = api.login(config.WEKAN_USERNAME, config.WEKAN_PASSWORD)
    for board in api.get_boards_from_user(config.WEKAN_ADMIN_USER, token):
        cards_last_activity = adapter.get_cards_activity_board(board)
        db_cards = adapter.get_updated_cards(board, cards_last_activity, token)
        adapter.map_users_with_db(board, db_cards, token)
    
    logging.info(f"'{len(db_cards)}' cards were added or updated")
    logging.info(f"Program finished")

    database.disconnect()


if __name__ == "__main__":
    main()
