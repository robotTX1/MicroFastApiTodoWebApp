import base64

import oci
from loguru import logger
from starlette.config import Config

secrets: dict[str, str] = {}

env_config = Config(".env")


def is_local_profile():
    return env_config.get("PROFILE") == "local"


config_directory = "local-config" if is_local_profile() else "config"
service_config = Config(f"{config_directory}/service.properties")


def fetch_secret(secret_name: str, secrets_client: oci.secrets.SecretsClient, vault_config: Config) -> str:
    secret_bundle = secrets_client.get_secret_bundle_by_name(secret_name, vault_config.get("vaultOcid"))
    base64_secret_content = secret_bundle.data.secret_bundle_content.content
    base64_secret_bytes = base64_secret_content.encode('ascii')
    base64_message_bytes = base64.b64decode(base64_secret_bytes)
    secret_content = base64_message_bytes.decode('ascii')
    logger.debug("Fetched secret from vault: {}", secret_name)
    return secret_content


def load_secrets():
    if is_local_profile():
        logger.debug("Loading secrets from local config")
        oauth_config = Config(f"{config_directory}/oauth.properties")
        valkey_config = Config(f"{config_directory}/valkey.properties")
        # Valkey
        secrets[service_config.get("valkeyUsernameSecretName")] = valkey_config.get("username")
        secrets[service_config.get("valkeyPasswordSecretName")] = valkey_config.get("password")
        # OAuth
        secrets[service_config.get("applicationClientSecretName")] = oauth_config.get("clientSecret")
    else:
        logger.debug("Loading secrets from vault")
        vault_config = Config(f"{config_directory}/vault.properties")
        signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
        secrets_client = oci.secrets.SecretsClient(config={}, signer=signer)
        # Valkey
        secrets[service_config.get("valkeyUsernameSecretName")] = fetch_secret(
            service_config.get("valkeyUsernameSecretName"),
            secrets_client,
            vault_config
        )
        secrets[service_config.get("valkeyPasswordSecretName")] = fetch_secret(
            service_config.get("valkeyPasswordSecretName"),
            secrets_client,
            vault_config
        )
        # OAuth
        secrets[service_config.get("applicationClientSecretName")] = fetch_secret(
            service_config.get("applicationClientSecretName"),
            secrets_client,
            vault_config
        )


load_secrets()
