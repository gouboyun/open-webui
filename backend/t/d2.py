from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Create an engine that stores data in the local directory's sqlite.db file.
engine = create_engine('sqlite:///./sqlite.db')

# Create a base class for declarative class definitions
Base = declarative_base()

# Define a simple User model
class User(Base):
    __tablename__ = 'users'  # Table name

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

# Create a configured "Session" class
Session = sessionmaker(bind=engine)

# Create a Session
session = Session()

# Create the tables in the database
Base.metadata.create_all(engine)

# Example usage: Add a new user
new_user = User(name="John Doe", email="johndoe@example.com")
session.add(new_user)
session.commit()

# Query the database
users = session.query(User).all()
for user in users:
    print(f"User {user.id}: {user.name}, {user.email}")

# Close the session
session.close()