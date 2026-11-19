from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Division(Base):
    __tablename__ = "divisions"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
    )
    period_id: Mapped[int] = mapped_column(
        ForeignKey("periods.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)