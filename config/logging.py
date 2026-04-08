import json
import logging
from datetime import datetime
from contextvars import ContextVar


request_id_context: ContextVar[str] = ContextVar("request_id", default="-")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "level": record.levelname,
            "timestamp": datetime.utcnow().isoformat(),
            "service": "coworking-booking-service",
            "message": record.getMessage(),
            "request_id": request_id_context.get(),
        }

        if hasattr(record, "path"):
            log_record["path"] = record.path

        if hasattr(record, "method"):
            log_record["method"] = record.method

        if hasattr(record, "status_code"):
            log_record["status_code"] = record.status_code

        return json.dumps(log_record, ensure_ascii=False)