import asyncio
import clickhouse_connect
from app.config import settings


class ClickHouseClient:
    def __init__(self):
        self.client = None

    def connect(self):
        self.client = clickhouse_connect.get_client(
            host=settings.clickhouse_url.replace("http://", "").split(":")[0],
            port=8123,
        )

    async def insert_messages(self, messages: list[dict]):
        if not messages:
            return
        rows = [
            (m["message_id"], m["channel_id"], m["tag_id"], m["user_id"], m["created_at"])
            for m in messages
        ]
        await asyncio.to_thread(
            self.client.insert,
            table="messages_dist",
            data=rows,
            column_names=["message_id", "channel_id", "tag_id", "user_id", "created_at"],
        )

    async def get_analytics(self, channel_id: int, period: str, days: int = 30) -> list[dict]:
        if period == "day":
            query = """
                SELECT
                    period as date,
                    messages_count,
                    active_users,
                    subscribers_count
                FROM analytics_dist FINAL
                WHERE channel_id = %(channel_id)s
                  AND period >= today() - INTERVAL %(days)s DAY
                ORDER BY period
            """
        else:
            query = """
                SELECT
                    toStartOfMonth(period) as date,
                    sum(messages_count) as messages_count,
                    sum(active_users) as active_users,
                    sum(subscribers_count) as subscribers_count
                FROM analytics_dist FINAL
                WHERE channel_id = %(channel_id)s
                  AND period >= today() - INTERVAL %(days)s DAY
                GROUP BY toStartOfMonth(period)
                ORDER BY date
            """
        result = await asyncio.to_thread(
            self.client.query, query, {"channel_id": channel_id, "days": days}
        )
        return [
            {"date": str(row[0]), "messages_count": row[1], "active_users": row[2], "subscribers_count": row[3]}
            for row in result.result_rows
        ]


ch_client = ClickHouseClient()
