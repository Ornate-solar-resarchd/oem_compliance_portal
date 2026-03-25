from app.core.config import settings

broker_url = settings.REDIS_URL
result_backend = settings.REDIS_URL
task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "Asia/Kolkata"
enable_utc = True
task_routes = {
    "generate_document": {"queue": "documents"},
    "run_ai_extraction": {"queue": "ai"},
}
