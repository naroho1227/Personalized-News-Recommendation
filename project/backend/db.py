from sqlalchemy import create_engine, MetaData, Table, Column, String, DateTime, Integer

engine = create_engine("sqlite:///C:/Users/yhw76/project/news.db")

metadata = MetaData()

news_table = Table(
    "news",
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
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
    try:
        with engine.connect() as conn:
            conn.execute(news_table.insert(), news)
            conn.commit()
    except Exception as e:
        print(f"❌ DB 저장 중 에러 발생: {e}")
