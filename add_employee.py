from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Employee, Base, Company, User

engine = create_engine('sqlite:///company.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="mandar", email="waghemandar1712@gmail.com",
             picture="/static/mandar1.jpg")
session.add(User1)
session.commit()

User2 = User(name="Arun", email="arunpal@gmail.com",
             picture="/static/blank_user.gif")
session.add(User2)
session.commit()

# Menu for UrbanBurger
company1 = Company(user_id=1, name="Mahindra Motors",\
 picture="/static/Mahindra-logo.png")

session.add(company1)
session.commit()

company2 = Company(user_id=1, name="Sweetlime ventures", \
picture="/static/sweetlime.png")

session.add(company2)
session.commit()


employee1 = Employee(user_id=1, name="Mandar Waghe", \
                     dob="17/12/1994",\
                     email="waghemandar1712@gmail.com", \
                     contact="8007528271", address="Thane",\
                     picture="/static/mandar1.jpg"\
                     ,company=company1)

session.add(employee1)
session.commit()


employee2 = Employee(user_id=1, name="Vijay Nath", dob="02/02/1994",\
                     email="Vijaynath@gmail.com", contact="9856432312", \
                     address="Thane",\
                     picture="/static/blank_user.gif"\
                     ,company=company1)

session.add(employee2)
session.commit()

employee3 = Employee(user_id=1, name="Mandar Waghe", dob="17/12/1994",\
                     email="waghemandar1712@gmail.com", contact="8007528271",\
                      address="Thane",picture="/static/mandar1.jpg",\
                       company=company2)

session.add(employee3)
session.commit()

employee4 = Employee(user_id=1, name="akshata waghe", dob="02/02/1994",\
                     email="wagheakshu@gmail.com", contact="9856432312",\
                      address="Thane",picture="/static/blank_user.gif"\
                     ,company=company2)

session.add(employee4)
session.commit()





print "added menu items!"
