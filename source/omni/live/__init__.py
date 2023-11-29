import jwt
from .live_edit_session import LiveEditSession
from .nucleus_client_error import NucleusClientError
from .live_cube import LiveCube

def getUserNameFromToken(token: str):
    unvalidated = jwt.decode(token, options={"verify_signature": False})
    email = unvalidated["profile"]["email"]
    if email is None or email == '':
        return "$omni-api-token"

    return email
