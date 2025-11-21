from loguru import logger
from redis.asyncio import Redis, RedisCluster
from starsessions.stores.redis import RedisStore

from microfastapitodowebapp.config.configuration import service_config, secrets, is_local_profile

valkey_client = None

if is_local_profile():
    logger.debug("Using standalone Valkey configuration")
    valkey_client = Redis(
        host=service_config.get("valkeyHostname"),
        port=service_config.get("valkeyPort"),
        username=secrets.get(service_config.get("valkeyUsernameSecretName")),
        password=secrets.get(service_config.get("valkeyPasswordSecretName"))
    )
else:
    logger.debug("Using cluster Valkey configuration")
    valkey_client = RedisCluster(
        host=service_config.get("valkeyHostname"),
        port=service_config.get("valkeyPort"),
        username=secrets.get(service_config.get("valkeyUsernameSecretName")),
        password=secrets.get(service_config.get("valkeyPasswordSecretName")),
        socket_timeout=2,
        require_full_coverage=False
    )

valkey_store = RedisStore(connection=valkey_client)
