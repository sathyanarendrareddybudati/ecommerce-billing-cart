from sqlalchemy import Column, Integer, String, Float, ForeignKey
from config.database import Base
from sqlalchemy.orm import relationship


class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True)
    sku = Column(String, unique=True, index=True)
    price = Column(Float)

    combos = relationship('Combo', back_populates='product')

class Combo(Base):
    __tablename__ = 'combos'

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer)
    price = Column(Float)

    product = relationship('Product', back_populates='combos')