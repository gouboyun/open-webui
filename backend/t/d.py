# coding:utf8
from sqlalchemy import Dialect, create_engine, types
from sqlalchemy import Column, BigInteger, Text, JSON
from sqlalchemy.orm import sessionmaker

from sqlalchemy.orm import declarative_base

from pydantic import BaseModel, ConfigDict
from typing import Optional

import logging

import uuid


Base = declarative_base()

class PdfFolder(Base):
    __tablename__ = "pdffolder"

    id = Column(Text, unique=True, primary_key=True)
    parent_id = Column(Text, nullable=True)
    user_id = Column(Text)

    name = Column(Text)
    description = Column(Text, nullable=True)

    data = Column(JSON, nullable=True)
    meta = Column(JSON, nullable=True)

    created_at = Column(BigInteger)
    updated_at = Column(BigInteger)


class PdfFolderModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    parent_id: Optional[str] = None
    user_id: str

    name: str
    description: Optional[str]

    data: Optional[dict] = None
    meta: Optional[dict] = None

    created_at: int  # timestamp in epoch
    updated_at: int  # timestamp in epoch


def main():
    db_name = "/./demo.db"
    engine = create_engine(f'sqlite://{db_name}', echo=True)
    
    Base.metadata.create_all(engine)
    
    # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

    logging.info("before connect")

    with Session() as s:
        # PdfFolder.metadata.create_all(s)

        p1 = PdfFolder(
            id = str(uuid.uuid4()),
            name="some thing good", user_id="123")
        s.add(p1)
        s.commit()

        p2 = s.query(PdfFolder).filter(PdfFolder.name.like("%thing%")).first()
        print("done ", p2)
        # p2 = PdfFolderModel.model_validate(p2).model_dump_json()
        # logging.info(f"query --> {p2}")

    # session = Session()

    # # Test the connection by executing a simple query
    # result = session.execute('SELECT 1')
    # print(result.fetchone())

    # # Close the session
    # session.close()



if __name__ == '__main__':
    fmt = '%(levelname)s-%(asctime)s %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt, force=True)

    main()