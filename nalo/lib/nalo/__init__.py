"""Nalo API Library."""

from httpx import AsyncClient
from pydantic import SecretStr

from .exceptions import REGISTRY


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
    response.raise_for_status()
    data = response.json()
    if "status" in data and data["status"] == 1701:
        return data
    else:
        if "code" in data:
            if data["code"] in REGISTRY:
                raise REGISTRY[data["code"]]()
            else:
                raise REGISTRY[-1](data["code"], data["message"])
        else:
            raise REGISTRY[-1](message=str(data))
