import logging
import signal

from config import shutdown_state

logger = logging.getLogger("app")


def handle_shutdown(signal_number, frame):
    shutdown_state.is_shutting_down = True
    logger.info(
        "Shutdown signal received",
        extra={
            "signal": signal_number,
        },
    )


def setup_graceful_shutdown():
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)