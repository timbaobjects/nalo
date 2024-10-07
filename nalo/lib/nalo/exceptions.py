"""Nalo API Response Exceptions."""


class NaloError(Exception):
    """Base error exception class."""

    code: int
    message: str

    def __init__(self, code: int = None, message: str = None) -> None:
        """Initialize self."""
        if code and message:
            self.code = code
            self.message = message

    def __repr__(self):
        """Return repr(self)."""
        return f'({self.code}, "{self.message}")'

    def __str__(self):
        """Return str(self)."""
        return f'({self.code}, "{self.message}")'


class NaloURLError(NaloError):
    """Invalid URL error.

    Raised when one of the parameters was not provided or left blank
    """

    code = 1702
    message = "Invalid URL Error"


class NaloAuthPasswordError(NaloError):
    """Invalid password authentication error.

    Raised when an invalid value was provided when authenticating with
    the API using a username and password.
    """

    code = 1703
    message = "Invalid value in username or password field"


class NaloAuthKeyError(NaloError):
    """Invalid key authentication error.

    Raised when an invalid value was provided when authenticating with
    the API using an API key.
    """

    code = 1713
    message = "Invalid auth key"


class NaloTypeError(NaloError):
    """Invalid message type error.

    Raised when the message type provided was invalid.
    """

    code = 1704
    message = 'Invalid value in "type" field'


class NaloMessageError(NaloError):
    """Invalid message error.

    Raised when the message supplied is deemed invalid.
    """

    code = 1705
    message = "Invalid Message"


class NaloDestinationError(NaloError):
    """Invalid message destination error.

    Raised when the message destination is invalid.
    """

    code = 1706
    message = "Invalid Destination"


class NaloSenderError(NaloError):
    """Invalid message sender error.

    Raised when the message sender is invalid.
    """

    code = 1707
    message = "Invalid Source (Sender)"


class NaloDLRError(NaloError):
    """Invalid delivery report parameter error.

    Raised when the provided dlr parameter is invalid.
    """

    code = 1708
    message = 'Invalid value for "dlr" field'


class NaloUserError(NaloError):
    """User validation error."""

    code = 1709
    message = "User validation failed"


class NaloInternalError(NaloError):
    """Internal error.

    Raised when there's an internal error.
    """

    code = 1710
    message = "Internal Error"


class NaloUserCreditError(NaloError):
    """Insufficient credits for a user account.

    Raised when there are insufficient credits for a user account.
    """

    code = 1025
    message = "Insufficient Credit User"


class NaloResellerCreditError(NaloError):
    """Insufficient credits for a reseller account.

    Raised when there are insufficient credits for a reseller account.
    """

    code = 1025
    message = "Insufficient Credit Reseller"


class NaloUnknownError(NaloError):
    """Unknown error.

    Raised when there's an unknown error.
    """

    code = -1
    message = "Unknown error"


REGISTRY = {cls.code: cls for cls in NaloError.__subclasses__()}
