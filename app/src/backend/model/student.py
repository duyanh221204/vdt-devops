from sqlalchemy import Integer, Column, String

from configuration.database import Base


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    year_of_birth = Column(Integer, nullable=False)
