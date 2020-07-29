from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from db.database import Base, engine

class Protein(Base):
    __tablename__ = "proteins"
    
    protein_name = Column(String, index=True)
    protein_id = Column(String, primary_key=True, index=True)
    uniprot_url = Column(String, index=True)

    # bindings = relationship("BindingSite", back_populates="protein_name")


class Gene(Base):
    __tablename__ = "genes"

    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    biotype = Column(String, index=True)
    chr = Column(String, index=True)
    start = Column(Integer, index=True)
    end = Column(Integer, index=True)
    strand = Column(String, index=True)

    # tento relationship bude asi trochu tricky
    # na zacatku set up-nout DB bez nej
    # je vubec treba?

    # binding_sites = relationship("BindingSite")
    # binding_sites = relationship('BindingSite', primaryjoin='foreign(genes.symbol) == bindings_site.protein_name')


class BindingSite(Base):
    __tablename__ = "binding_sites"

    id = Column(Integer, primary_key=True, index=True)
    protein_name = Column(String, index=True)
    chr = Column(String, index=True)
    start = Column(Integer, index=True)
    end = Column(Integer, index=True)
    strand = Column(String, index=True)
    score = Column(Float, index=True)
    note = Column(String)

#TODO move to other script
# Base.metadata.create_all(bind=engine)