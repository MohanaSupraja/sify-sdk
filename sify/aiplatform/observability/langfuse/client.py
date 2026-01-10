# import os
# from typing import Optional
# from langfuse import Langfuse
# from .config import get_langfuse_config

# _langfuse_client: Optional[Langfuse] = None


# def get_langfuse_client() -> Optional[Langfuse]:
#     global _langfuse_client
#     cfg = get_langfuse_config()

#     if not cfg.enabled:
#         return None

#     if _langfuse_client:
#         return _langfuse_client

#     if cfg.host:
#         os.environ["LANGFUSE_HOST"] = cfg.host
#     if cfg.public_key:
#         os.environ["LANGFUSE_PUBLIC_KEY"] = cfg.public_key
#     if cfg.secret_key:
#         os.environ["LANGFUSE_SECRET_KEY"] = cfg.secret_key

#     _langfuse_client = Langfuse()
#     return _langfuse_client
from typing import Optional
from langfuse import Langfuse
from .config import get_langfuse_config

_client: Optional[Langfuse] = None


def get_langfuse_client() -> Optional[Langfuse]:
    global _client
    cfg = get_langfuse_config()

    if not cfg.enabled:
        return None

    if _client:
        return _client

    _client = Langfuse(
        host=cfg.host,
        public_key=cfg.public_key,
        secret_key=cfg.secret_key,
    )
    return _client

