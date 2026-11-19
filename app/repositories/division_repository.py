from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.division import Division


class DivisionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization_id: int,
        period_id: int,
        name: str,
    ) -> Division:
        division = Division(
            organization_id=organization_id,
            period_id=period_id,
            name=name,
        )

        self.db.add(division)
        self.db.commit()
        self.db.refresh(division)

        return division

    def get_by_id(self, division_id: int) -> Division | None:
        statement = select(Division).where(
            Division.id == division_id
        )
        return self.db.scalar(statement)

    def get_all(
        self,
        organization_id: int | None = None,
        period_id: int | None = None,
    ) -> list[Division]:
        statement = select(Division).order_by(Division.id)

        if organization_id is not None:
            statement = statement.where(
                Division.organization_id == organization_id
            )

        if period_id is not None:
            statement = statement.where(
                Division.period_id == period_id
            )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        division_id: int,
        name: str,
    ) -> Division | None:
        division = self.get_by_id(division_id)

        if division is None:
            return None

        division.name = name

        self.db.commit()
        self.db.refresh(division)

        return division

    def delete(self, division_id: int) -> bool:
        division = self.get_by_id(division_id)

        if division is None:
            return False

        self.db.delete(division)
        self.db.commit()

        return True