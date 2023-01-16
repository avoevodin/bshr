import logging

from tenacity import retry, stop_after_attempt, before_log, after_log, wait_fixed

from app.db.session import session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.INFO),
)
def init() -> None:
    """
    Gets init DB and execute simple query.

    Returns:
        None
    """
    try:
        db = session
        db.execute("SELECT 1")
    except Exception as e:
        logger.exception(e)


def main() -> None:
    """
    Main test pre-start method.

    Returns:
        None
    """


if __name__ == "__main__":
    main()
