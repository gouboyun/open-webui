import logging

from typing import List
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user_account"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    fullname: Mapped[Optional[str]]
    addresses: Mapped[List["Address"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

class Address(Base):
    __tablename__ = "address"
    id: Mapped[int] = mapped_column(primary_key=True)
    email_address: Mapped[str]
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
    user: Mapped["User"] = relationship(back_populates="addresses")
    def __repr__(self) -> str:
        return f"Address(id={self.id!r}, email_address={self.email_address!r})"
    
    
def task():
    db_name = "/./the.db"
    engine = create_engine(f'sqlite://{db_name}', 
                        #    echo=True,
                           )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    with Session() as s:
        if s.query(User).count() == 0:
            user = User(name="jack", fullname="jack smith")
            s.add(user)
            s.commit()
    
        q = "jack"
        user = s.query(User).filter(User.name.like(f'%{q}%')).all()
        print("done ", user)


def main():
    fmt = '%(levelname)s-%(asctime)s %(message)s'
    logging.basicConfig(level=logging.INFO, format=fmt, force=True)
    
    try:
        task()
    except Exception as e:
        logging.error(e)


if __name__ == "__main__":
    main()