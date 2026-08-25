import redis
import json
import hashlib
from app.config import settings

redis_client = redis.from_url(settings.redis_url, decode_responses=True)

CACHE_TTL_SECONDS = 3600  # 1 hour


def _make_cache_key(question: str) -> str:
    normalized = question.strip().lower()
    hashed = hashlib.sha256(normalized.encode()).hexdigest()
    return f"ask:{hashed}"


def get_cached_answer(question: str):
    key = _make_cache_key(question)
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None


def set_cached_answer(question: str, result: dict):
    key = _make_cache_key(question)
    redis_client.setex(key, CACHE_TTL_SECONDS, json.dumps(result))