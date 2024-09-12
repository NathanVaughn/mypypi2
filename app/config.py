from http import HTTPStatus
from typing import Literal, Self, Type

from pydantic import BaseModel, HttpUrl, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    JsonConfigSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
    YamlConfigSettingsSource,
)


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
    uri: str


class StorageLocalConfig(BaseModel):
    directory: str


class StorageS3Config(BaseModel):
    endpoint_url: HttpUrl
    access_key_id: str
    secret_access_key: str
    bucket_name: str
    public_url_prefix: str
    region_name: str | None = None
    bucket_prefix: str = ""
    redirect_code: int = HTTPStatus.PERMANENT_REDIRECT


class StorageConfig(BaseModel):
    driver: Literal["s3", "local"]
    s3: StorageS3Config | None = None
    local: StorageLocalConfig | None = None

    @model_validator(mode="after")
    def must_contain_driver_config(self) -> Self:
        if self.driver == "s3" and self.s3 is None:
            raise ValueError("s3 config must be provided when using s3 driver")
        if self.driver == "local" and self.local is None:
            raise ValueError("local config must be provided when using local driver")
        return self


class CacheFilesystemConfig(BaseModel):
    directory: str


class CacheRedisConfig(BaseModel):
    host: str
    port: int = 6379
    db: int = 0


class CacheConfig(BaseModel):
    driver: Literal["memory", "filesystem", "redis"]
    filesystem: CacheFilesystemConfig | None = None
    redis: CacheRedisConfig | None = None

    @model_validator(mode="after")
    def must_contain_driver_config(self) -> Self:
        if self.driver == "filesystem" and self.filesystem is None:
            raise ValueError("filesystem config must be provided when using filesystem driver")
        return self


class _Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MYPYPI_",
        env_nested_delimiter="__",
        toml_file="config.toml",
        json_file="config.json",
        yaml_file="config.yaml",
    )

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
            TomlConfigSettingsSource(settings_cls),
            JsonConfigSettingsSource(settings_cls),
            YamlConfigSettingsSource(settings_cls),
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


Config = _Config()  # type: ignore
