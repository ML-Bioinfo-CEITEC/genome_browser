from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Index
from sqlalchemy.orm import relationship
from db.database import Base, engine

class Protein(Base):
    __tablename__ = "proteins"
    
    protein_name = Column(String, index=True)
    protein_id = Column(String, primary_key=True, index=True)
    uniprot_url = Column(String, index=True)


class Gene(Base):
    __tablename__ = "genes"

    id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    biotype = Column(String, index=True)
    chr = Column(String, index=True)
    start = Column(Integer, index=True)
    end = Column(Integer, index=True)
    strand = Column(String, index=True)


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

class Prejoin(Base):
    __tablename__='prejoin'
    #BS
    bs_id = Column(Integer, primary_key=True, index=True)
    protein_name = Column(String, index=True)
    chr = Column(String, index=True)
    bs_start = Column(Integer, index=True)
    bs_end = Column(Integer, index=True)
    strand = Column(String, index=True)
    score = Column(Float, index=True)
    note = Column(String)
    #GENE
    gene_id = Column(String, primary_key=True, index=True)
    symbol = Column(String, index=True)
    gene_start = Column(Integer, index=True)
    gene_end = Column(Integer, index=True)