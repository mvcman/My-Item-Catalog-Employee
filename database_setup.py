from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {

            'id': self.id,
            'name': self.name,
            'email': self.email,
            'picture':self.picture,
        }

class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    picture = Column(String(250))
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)
    employee = relationship('Employee', cascade='all, delete-orphan')
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'picture':self.picture,
        }


class Employee(Base):
    __tablename__ = 'employee'


    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    dob = Column(String(250))
    email = Column(String(100))
    contact = Column(String(10))
    address = Column(String(250))
    picture = Column(String(250))
    company_id = Column(Integer, ForeignKey('company.id'))
    company = relationship(Company)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'dob': self.dob,
            'email': self.email,
            'contact': self.contact,
            'address': self.address,
        }


engine = create_engine('sqlite:///company.db')


Base.metadata.create_all(engine)
