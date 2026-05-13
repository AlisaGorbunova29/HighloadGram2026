from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_master_url: str = "postgresql+asyncpg://admin:admin@localhost:5432/messenger"
    db_replica_urls: str = "postgresql+asyncpg://admin:admin@localhost:5433/messenger"
    clickhouse_url: str = "http://localhost:8123"

    @property
    def replica_url_list(self) -> list[str]:
        return [url.strip() for url in self.db_replica_urls.split(",")]


settings = Settings()
