import os
from enum import Enum
from http import HTTPStatus
from typing import Literal, Self, Type

from loguru import logger
from pydantic import BaseModel, HttpUrl, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)

import app.constants


class StorageDrivers(Enum):
    FILESYSTEM = "filesystem"
    S3 = "s3"


class CacheDrivers(Enum):
    MEMORY = "memory"
    FILESYSTEM = "filesystem"
    REDIS = "redis"
    MEMCACHED = "memcached"
    DATABASE = "database"


class RepositoryConfig(BaseModel):
    slug: str
    simple_url: HttpUrl
    cache_minutes: int = 10
    timeout_seconds: int = 10

    @field_validator("slug")
    def slug_must_be_alphanumeric_lowercase(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("slug must be alphanumeric")
        return v.lower()


class DatabaseConfig(BaseModel):
    url: str

    @field_validator("url")
    def url_prefix(cls, v: str) -> str:
        """
        Database must be sqlite or postgres
        """
        if v.startswith("sqlite://"):
            logger.warning("SQLite is not recommended for production")
        elif not v.startswith("postgresql://"):
            raise ValueError("Database must be PostgreSQL or SQLite")

        return v


class StorageFilesystemConfig(BaseModel):
    directory: str


class StorageS3Config(BaseModel):
    endpoint_url: HttpUrl
    access_key_id: str
    secret_access_key: str
    bucket_name: str
    public_url_prefix: str
    region_name: str | None = None
    bucket_prefix: str = ""
    redirect_code: Literal[
        HTTPStatus.MOVED_PERMANENTLY,
        HTTPStatus.FOUND,
        HTTPStatus.TEMPORARY_REDIRECT,
        HTTPStatus.PERMANENT_REDIRECT,
    ] = HTTPStatus.PERMANENT_REDIRECT

    @field_validator("redirect_code", mode="before")
    @classmethod
    def coerce_redirect_code(cls, v: str | int | HTTPStatus) -> HTTPStatus:
        """
        When coming from an environment variable, the value will be a string.
        We need to convert it to an HTTPStatus enum.
        """
        return HTTPStatus(int(v))


class StorageConfig(BaseModel):
    driver: StorageDrivers
    s3: StorageS3Config | None = None
    filesystem: StorageFilesystemConfig | None = None

    @model_validator(mode="after")
    def must_contain_driver_config(self) -> Self:
        if self.driver == StorageDrivers.S3 and self.s3 is None:
            raise ValueError("S3 config must be provided when using S3 driver")
        if self.driver == StorageDrivers.FILESYSTEM and self.filesystem is None:
            raise ValueError("filesystem config must be provided when using filesystem driver")
        return self


class CacheFilesystemConfig(BaseModel):
    directory: str


class CacheRedisConfig(BaseModel):
    host: str
    port: int = 6379
    db: int = 0


class CacheMemcachedConfig(BaseModel):
    host: str
    port: int = 11211


class CacheConfig(BaseModel):
    driver: CacheDrivers = CacheDrivers.MEMORY
    filesystem: CacheFilesystemConfig | None = None
    redis: CacheRedisConfig | None = None
    memcached: CacheMemcachedConfig | None = None

    @model_validator(mode="after")
    def must_contain_driver_config(self) -> Self:
        if self.driver == CacheDrivers.FILESYSTEM and self.filesystem is None:
            raise ValueError("filesystem config must be provided when using filesystem driver")
        if self.driver == CacheDrivers.REDIS and self.redis is None:
            raise ValueError("Redis config must be provided when using Redis driver")
        if self.driver == CacheDrivers.MEMCACHED and self.memcached is None:
            raise ValueError("memcached config must be provided when using memcached driver")
        return self


class _Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MYPYPI_",
        env_nested_delimiter="__",
        toml_file="config.toml",
        json_file="config.json",
        yaml_file="config.yaml",
    )

    base_url: HttpUrl
    repositories: list[RepositoryConfig]
    database: DatabaseConfig
    storage: StorageConfig
    cache: CacheConfig

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            TomlConfigSettingsSource(settings_cls),
            JsonConfigSettingsSource(settings_cls),
            YamlConfigSettingsSource(settings_cls),
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


if app.constants.IS_TESTING:
    Config = _Config(
        repositories=[RepositoryConfig(slug="pypi", simple_url="https://pypi.org/simple")],  # type: ignore
        database=DatabaseConfig(url="sqlite:///:memory:"),
        storage=StorageConfig(
            driver=StorageDrivers.FILESYSTEM,
            filesystem=StorageFilesystemConfig(directory=os.path.join("tmp", "storage")),
        ),
        cache=CacheConfig(driver=CacheDrivers.MEMORY),
    )
else:
    Config = _Config()  # type: ignore
