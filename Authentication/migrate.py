from flask import Flask
from configuration import Configuration
from flask_migrate import Migrate, init, upgrade, migrate
from models import *
from sqlalchemy_utils import database_exists, create_database

application = Flask(__name__)
application.config.from_object(Configuration)

migrateObject = Migrate(application, database)

if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
    create_database(application.config["SQLALCHEMY_DATABASE_URI"])

database.init_app(application)

with application.app_context() as context:
    init()
    migrate(message="Production migration")
    upgrade()

    vlasnik_role    = Role(name="vlasnik")
    kurir_role      = Role(name="kurir")
    kupac_role      = Role(name="kupac")

    database.session.add(vlasnik_role)
    database.session.add(kurir_role)
    database.session.add(kupac_role)

    mcduk = User(
        email="onlymoney@gmail.com",
        password="evenmoremoney",
        forename="Scrooge",
        surname="McDuck"
    )
    database.session.add(mcduk)
    database.session.commit()

    v2 = UserRole(
        userId=mcduk.id,
        roleId=vlasnik_role.id
    )
    database.session.add(v2)
    database.session.commit()

    database.session.commit()

    vlasnik = User(
        email="vlasnik@etf.rs",
        password="vlasnik123",
        forename="Vlas",
        surname="Vlasic"
    )

    database.session.add(vlasnik)
    database.session.commit()

    veza = UserRole(
        userId = vlasnik.id,
        roleId = vlasnik_role.id
    )

    database.session.add(veza)
    database.session.commit()

