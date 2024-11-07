"""Main application."""

from importlib import metadata
from typing import Annotated

from fastapi import BackgroundTasks, FastAPI, Form, Request
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
