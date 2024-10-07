"""Apollo SMS Gateway API."""

from httpx import URL, AsyncClient
from loguru import logger
from pydantic import SecretStr


@logger.catch
async def inject_sms(client: AsyncClient, endpoint: URL, sender: str, message: str, secret: SecretStr) -> str:
    """Injects an SMS into the Apollo SMS pipeline."""
    args = {
        "sender": sender,
        "text": message,
        "secret": secret.get_secret_value(),
    }
    request = client.build_request("GET", endpoint, params=args)
    response = await client.send(request)
    logger.debug(response.status_code, response.content)
    response.raise_for_status()
    return response.text
