from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    nome = Column(String)

class Entrada(Base):
    __tablename__ = 'entradas'
    id = Column(Integer, primary_key=True)
    texto = Column(Text)
    data_criacao = Column(DateTime, default=datetime.utcnow)
    entidades = relationship("Entidade", back_populates="entrada")
    sugestoes = relationship("Sugestao", back_populates="entrada")

class Entidade(Base):
    __tablename__ = 'entidades'
    id = Column(Integer, primary_key=True)
    texto = Column(String)
    tipo = Column(String)
    entrada_id = Column(Integer, ForeignKey('entradas.id'))
    entrada = relationship("Entrada", back_populates="entidades")

class Sugestao(Base):
    __tablename__ = 'sugestoes'
    id = Column(Integer, primary_key=True)
    artigo = Column(Text)
    entrada_id = Column(Integer, ForeignKey('entradas.id'))
    entrada = relationship("Entrada", back_populates="sugestoes")
