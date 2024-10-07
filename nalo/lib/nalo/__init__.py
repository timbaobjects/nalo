"""Nalo API Library."""

from httpx import AsyncClient
from loguru import logger
from pydantic import SecretStr

from .exceptions import REGISTRY


@logger.catch
async def send_sms(client: AsyncClient, recipient: str, message: str, sender: str, api_key: SecretStr) -> dict:
    """Sends and SMS through the Nalo SMS API."""
    payload = {
        "key": api_key.get_secret_value(),
        "msisdn": recipient,
        "message": message,
        "sender_id": sender,
    }
    request = client.build_request(
        "POST", "https://sms.nalosolutions.com/smsbackend/clientapi/Resl_Nalo/send-message/", json=payload
    )
    response = await client.send(request)
    logger.debug(f"{response.status_code} {response.content.decode('utf-8')}")
    data = response.json()
    if "status" in data and int(data["status"]) == 1701:
        return data
    else:
        if "code" in data:
            code = int(data["code"])
            if code in REGISTRY:
                raise REGISTRY[code]()
            else:
                raise REGISTRY[-1](code, data["message"])
        else:
            raise REGISTRY[-1](message=str(data))
