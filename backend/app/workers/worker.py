"""POC background worker entrypoint.

In production this would run via Celery/RQ/Arq. For this POC, FastAPI BackgroundTasks invoke
service functions directly; this module documents and exposes callable tasks for future queue wiring.
"""

from app.workers.tasks_imports import run_import_job
from app.workers.tasks_notifications import notify_ai_review_queue

__all__ = ["run_import_job", "notify_ai_review_queue"]
