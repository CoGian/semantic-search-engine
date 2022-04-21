from pgvector.sqlalchemy import Vector
from sqlalchemy import create_engine, text, Column, String, Index
from sqlalchemy.orm import declarative_base, Session

Base = declarative_base()


class Paper(Base):
	__tablename__ = 'Paper'

	id = Column(String, primary_key=True)
	title = Column(String)
	abstract = Column(String)
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

		self.engine = engine
		self.create_index()

	def create_index(self, distance='vector_ip_ops'):
		index = Index('my_index', Paper.embedding,
					  postgresql_using='ivfflat',
					  postgresql_with={'lists': 100},
					  postgresql_ops={'factors': distance}
					  )
		index.create(self.engine, checkfirst=True)

	def populate_db(self, papers):
		Base.metadata.drop_all(self.engine)
		Base.metadata.create_all(self.engine)
		session = Session(self.engine)
		session.bulk_insert_mappings(Paper, papers)
		session.commit()
		session.close()

	def get_k_results(self, query_embedding, k=5):
		session = Session(self.engine)
		papers = session.query(Paper)\
			.order_by(Paper.embedding.max_inner_product(query_embedding))\
			.limit(k)\
			.all()
		return papers
