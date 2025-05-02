from sqlmodel import SQLModel, create_engine
import models # Import the tables in order to fill the tables metadata


engine = create_engine("sqlite:///../database.db")

def create_all_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_all_tables()
