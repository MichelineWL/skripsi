from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.program import Program


class ProgramRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        organization_id: int,
        period_id: int,
        division_id: int,
        name: str,
        description: str | None = None,
        status: str = "planned",
    ) -> Program:
        program = Program(
            organization_id=organization_id,
            period_id=period_id,
            division_id=division_id,
            name=name,
            description=description,
            status=status,
        )

        self.db.add(program)
        self.db.commit()
        self.db.refresh(program)

        return program

    def get_by_id(self, program_id: int) -> Program | None:
        statement = select(Program).where(
            Program.id == program_id
        )
        return self.db.scalar(statement)

    def get_all(
        self,
        organization_id: int | None = None,
        period_id: int | None = None,
        division_id: int | None = None,
    ) -> list[Program]:
        statement = select(Program).order_by(Program.id)

        if organization_id is not None:
            statement = statement.where(
                Program.organization_id == organization_id
            )

        if period_id is not None:
            statement = statement.where(
                Program.period_id == period_id
            )

        if division_id is not None:
            statement = statement.where(
                Program.division_id == division_id
            )

        return list(self.db.scalars(statement).all())

    def update(
        self,
        program_id: int,
        name: str,
        description: str | None,
        status: str,
    ) -> Program | None:
        program = self.get_by_id(program_id)

        if program is None:
            return None

        program.name = name
        program.description = description
        program.status = status

        self.db.commit()
        self.db.refresh(program)

        return program

    def delete(self, program_id: int) -> bool:
        program = self.get_by_id(program_id)

        if program is None:
            return False

        self.db.delete(program)
        self.db.commit()

        return True