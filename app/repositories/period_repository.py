from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.period import Period


class PeriodRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization_id: int,
        name: str,
        start_date=None,
        end_date=None,
    ) -> Period:
        period = Period(
            organization_id=organization_id,
            name=name,
            start_date=start_date,
            end_date=end_date,
        )

        self.db.add(period)
        self.db.commit()
        self.db.refresh(period)

        return period

    def get_by_id(self, period_id: int) -> Period | None:
        statement = select(Period).where(Period.id == period_id)
        return self.db.scalar(statement)

    def get_all(
        self,
        organization_id: int | None = None,
    ) -> list[Period]:
        statement = select(Period).order_by(Period.id)

        if organization_id is not None:
            statement = statement.where(
                Period.organization_id == organization_id
            )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        period_id: int,
        name: str,
        start_date=None,
        end_date=None,
    ) -> Period | None:
        period = self.get_by_id(period_id)

        if period is None:
            return None

        period.name = name
        period.start_date = start_date
        period.end_date = end_date

        self.db.commit()
        self.db.refresh(period)

        return period

    def delete(self, period_id: int) -> bool:
        period = self.get_by_id(period_id)

        if period is None:
            return False

        self.db.delete(period)
        self.db.commit()

        return True