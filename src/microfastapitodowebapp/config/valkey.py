from redis.asyncio import Redis
from starsessions.stores.redis import RedisStore

from microfastapitodowebapp.config.configuration import service_config, secrets

valkey_client = Redis(
    host=service_config.get("valkeyHostname"),
    port=service_config.get("valkeyPort"),
    username=secrets.get(service_config.get("valkeyUsernameSecretName")),
    password=secrets.get(service_config.get("valkeyPasswordSecretName"))
)
valkey_store = RedisStore(connection=valkey_client)
