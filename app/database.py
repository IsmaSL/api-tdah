# Configuración de la base de datos y sesión SQLAlchemy.
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuraciones de la base de datos
DATABASE_URL = "mysql+pymysql://root:holamundo.1@localhost/tdah_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()