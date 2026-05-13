import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy import select, func
from app.clickhouse_client import ch_client
from app.database import replica_sessions
from app.models import Subscription


async def update_analytics():
    if not ch_client.client:
        ch_client.connect()

    today = datetime.utcnow().date()
    yesterday = today - timedelta(days=1)

    query = """
        SELECT
            channel_id,
            toDate(created_at) as period,
            count() as messages_count,
            uniqExact(user_id) as active_users
        FROM messages_dist
        WHERE created_at >= %(start)s
        GROUP BY channel_id, toDate(created_at)
    """
    start_dt = datetime.combine(yesterday, datetime.min.time())
    result = await asyncio.to_thread(ch_client.client.query, query, {"start": start_dt})

    session_maker = random.choice(replica_sessions)
    async with session_maker() as db_session:
        sub_result = await db_session.execute(
            select(Subscription.channel_id, func.count().label("cnt")).group_by(Subscription.channel_id)
        )
        subscribers = {row.channel_id: row.cnt for row in sub_result.all()}

    rows = []
    version = int(datetime.utcnow().timestamp())
    for row in result.result_rows:
        channel_id, period, messages_count, active_users = row
        rows.append((
            int(channel_id),
            period,
            int(messages_count),
            int(active_users),
            int(subscribers.get(int(channel_id), 0)),
            version,
        ))

    if rows:
        await asyncio.to_thread(
            ch_client.client.insert,
            "analytics_dist",
            rows,
            column_names=["channel_id", "period", "messages_count", "active_users", "subscribers_count", "version"],
        )
