from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class Paper(Base):
	__tablename__ = 'Paper'

	id = Column(String, primary_key=True)
	local_link = Column(String, nullable=False)
	embedding = Column(Vector(768), nullable=False)


class PostgresConnector:

	def __init__(self, configs):
		self.configs = configs
		engine = create_engine(
			f'postgresql+psycopg2://{configs["user"]}:{configs["password"]}@localhost/{configs["database"]}',
			future=True)
		with engine.connect() as conn:
			conn.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))
			conn.commit()

		Base.metadata.drop_all(engine)
		Base.metadata.create_all(engine)
		self.engine = engine

	def populate_db(self, papers):
		session = Session(self.engine)
		session.bulk_insert_mappings(Paper, papers)
		session.commit()
		session.close()
