from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime

engine = create_engine("sqlite:///news.db")

metadata = MetaData()

news_table = Table(
    "news",
    metadata,
    Column('id', String, primary_key=True),
    Column("title", String),
    Column("content", String),
    Column('description', String),
    Column('author', String),
    Column('source_name', String),
    Column('url', String),
    Column('published_at', DateTime),
    Column("category", String),
    Column("created_at", DateTime),
)

metadata.create_all(engine)

def insert_news(news):
    with engine.connect() as conn:
        conn.execute(news_table.insert(), news)
