"""Main application."""

from importlib import metadata
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, Form, Query, Request, Response
from httpx import AsyncClient, Headers
from lib.apollo import inject_sms
from lib.nalo import send_sms
from loguru import logger
from pydantic import BaseModel, Field, HttpUrl, NaiveDatetime, SecretStr, StringConstraints
from pydantic.functional_validators import AfterValidator
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic_settings import BaseSettings, SettingsConfigDict

USER_AGENT = f"nalo-apollo/{metadata.version('nalo')}"
headers = Headers({"User-Agent": USER_AGENT})


class Settings(BaseSettings):
    """Application settings."""

    apollo_endpoint: HttpUrl
    apollo_secret: SecretStr
    nalo_api_key: SecretStr
    nalo_sender_id: str
    outbound_username: str
    outbound_password: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


PhoneNumber.supported_regions = ["GH"]
PhoneNumber.default_region_code = "GH"
PhoneNumber.phone_format = "E164"


class Inbound(BaseModel):
    """Inbound data format."""

    msisdn: Annotated[PhoneNumber, AfterValidator(lambda x: x.lstrip("+"))]
    shortcode: Annotated[str, StringConstraints(pattern=r"\d+")]
    network: Annotated[str, Field(min_length=1)]
    msg: Annotated[str, Field(min_length=1)]
    timestamp: NaiveDatetime


class Outbound(BaseModel):
    """Outbound data format.

    This model describes the request parameters for outbound messages.
    """

    username: Annotated[str, Field(min_length=1)]
    password: Annotated[str, Field(min_length=1)]
    sender: Annotated[str, Field(alias="from")] = None
    to: Annotated[PhoneNumber, AfterValidator(lambda x: x.lstrip("+"))]
    text: Annotated[str, Field(min_length=1)]


settings = Settings().model_dump()

app = FastAPI()


@app.middleware("http")
async def request_logger_middleware(request: Request, call_next):
    """Middleware for logging the request."""
    request_body = await request.body()
    logger.debug(f"{request.headers}\n{request_body.decode('utf-8')}")
    response = await call_next(request)
    return response


@app.post("/")
async def webhook(inbound: Annotated[Inbound, Form()], background_tasks: BackgroundTasks):
    """Webhook for processing incoming messages from Nalo."""
    client = AsyncClient(headers=headers, verify=True)
    reply = await inject_sms(
        client, str(settings["apollo_endpoint"]), inbound.msisdn, inbound.msg, settings["apollo_secret"]
    )
    background_tasks.add_task(send_sms, client, inbound.msisdn, reply, inbound.shortcode, settings["nalo_api_key"])
    return {"message": "OK"}


@app.get("/cgi-bin/sendsms")
async def outgoing(outbound: Annotated[Outbound, Query()], background_tasks: BackgroundTasks):
    """Outbound message processor."""
    client = AsyncClient(headers=headers, verify=True)
    if settings["outbound_username"] == outbound.username and settings["outbound_password"] == outbound.password:
        background_tasks.add_task(
            send_sms,
            client,
            outbound.to,
            outbound.text,
            outbound.sender or settings["nalo_sender_id"],
            settings["nalo_api_key"],
        )
        return Response(content="0: Accepted for delivery", status_code=202, media_type="text/plain")
    else:
        return Response(content="Authorization failed for sendsms", status_code=403, media_type="text/plain")
