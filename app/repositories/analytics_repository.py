from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.database.models.transaction import Transaction, TransactionStatus


class AnalyticsRepository:
    def __init__(self, session):
        self.session = session

    async def get_popular_products(
        self, days: int = 7, limit: int = 5
    ) -> list[Transaction]:
        since = datetime.now(UTC) - timedelta(days=days)

        stmt = (
            select(Transaction.product_id, func.count().label("total"))
            .where(
                Transaction.status == TransactionStatus.COMPLETED,
                Transaction.created_at >= since,
            )
            .group_by(Transaction.product_id)
            .order_by(func.count().desc())
            .limit(limit)
        )

        return (await self.session.execute(stmt)).all()
