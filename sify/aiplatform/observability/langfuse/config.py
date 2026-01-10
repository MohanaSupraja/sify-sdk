# # sify/aiplatform/observability/config.py

# import os
# from typing import Optional


# class LangfuseConfig:
#     def __init__(
#         self,
#         enabled: bool,
#         host: Optional[str] = None,
#         public_key: Optional[str] = None,
#         secret_key: Optional[str] = None,
#         environment: str = "production",
#     ):
#         self.enabled = enabled
#         self.host = host
#         self.public_key = public_key
#         self.secret_key = secret_key
#         self.environment = environment


# _langfuse_config: Optional[LangfuseConfig] = None


# def configure_langfuse(
#     enabled: bool,
#     host: Optional[str] = None,
#     public_key: Optional[str] = None,
#     secret_key: Optional[str] = None,
#     environment: Optional[str] = None,
# ):
#     """
#     Global Langfuse configuration.
#     Called ONCE by user.
#     """
#     global _langfuse_config

#     _langfuse_config = LangfuseConfig(
#         enabled=enabled,
#         host=host or os.getenv("LANGFUSE_HOST"),
#         public_key=public_key or os.getenv("LANGFUSE_PUBLIC_KEY"),
#         secret_key=secret_key or os.getenv("LANGFUSE_SECRET_KEY"),
#         environment=environment or os.getenv("LANGFUSE_ENV", "production"),
#     )


# def get_langfuse_config() -> Optional[LangfuseConfig]:
#     return _langfuse_config
from dataclasses import dataclass

@dataclass
class LangfuseConfig:
    enabled: bool = False
    host: str | None = None
    public_key: str | None = None
    secret_key: str | None = None


_cfg = LangfuseConfig()


def configure_langfuse(*, enabled: bool, host=None, public_key=None, secret_key=None):
    _cfg.enabled = enabled
    _cfg.host = host
    _cfg.public_key = public_key
    _cfg.secret_key = secret_key


def get_langfuse_config() -> LangfuseConfig:
    return _cfg
