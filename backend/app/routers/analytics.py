from fastapi import APIRouter, Query

from app.clickhouse_client import ch_client

router = APIRouter()


@router.get("/channel/{channel_id}")
async def get_channel_analytics(
    channel_id: int,
    period: str = Query("day", regex="^(day|month)$"),
    days: int = Query(30, ge=1, le=365),
):
    data = await ch_client.get_analytics(channel_id, period, days)
    return {
        "channel_id": channel_id,
        "period": period,
        "data": data,
    }
