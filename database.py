from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


# --------------------------------------------------
# Database connection
# --------------------------------------------------

engine = create_engine("sqlite:///traceqr.db")

Base = declarative_base()


# --------------------------------------------------
# Products Table
# --------------------------------------------------

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


# --------------------------------------------------
# Scans Table
# --------------------------------------------------

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    location = Column(String)
    device = Column(String)
    risk_score = Column(Integer, default=0)


# --------------------------------------------------
# Create tables
# --------------------------------------------------

Base.metadata.create_all(engine)


# --------------------------------------------------
# Database session
# --------------------------------------------------

Session = sessionmaker(bind=engine)


# --------------------------------------------------
# Add Product
# --------------------------------------------------

def add_product(name, product_id):

    session = Session()

    product = Product(
        product_id=product_id,
        name=name
    )

    session.add(product)
    session.commit()

    session.close()


# --------------------------------------------------
# Get all products
# --------------------------------------------------

def get_all_products():

    session = Session()

    products = session.query(Product).all()

    session.close()

    return products


# --------------------------------------------------
# Get one product
# --------------------------------------------------

def get_product(product_id):

    session = Session()

    product = (
        session.query(Product)
        .filter(Product.product_id == product_id)
        .first()
    )

    session.close()

    return product


# --------------------------------------------------
# Add Scan
# --------------------------------------------------

def add_scan(product_id, location, device):

    session = Session()

    scan = Scan(
        product_id=product_id,
        location=location,
        device=device,
        timestamp=datetime.now(),
        risk_score=0
    )

    session.add(scan)

    session.commit()

    session.close()


# --------------------------------------------------
# Get scans for one product
# --------------------------------------------------

def get_scans_for_product(product_id):

    session = Session()

    scans = (
        session.query(Scan)
        .filter(Scan.product_id == product_id)
        .order_by(Scan.timestamp.asc())
        .all()
    )

    session.close()

    return scans


# --------------------------------------------------
# Get all scans
# --------------------------------------------------

def get_all_scans():

    session = Session()

    scans = (
        session.query(Scan)
        .order_by(Scan.timestamp.desc())
        .all()
    )

    session.close()

    return scans