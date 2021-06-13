from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User_trips( db.Model ):
    user_id = db.Column( 'user_id', db.Integer, db.ForeignKey( 'user.user_id' ), primary_key = True )
    trip_id = db.Column( 'trip_id', db.Integer, db.ForeignKey( 'trip.trip_id' ), primary_key = True )
    user_debt = db.Column( db.Float )
    user = db.relationship( 'User', back_populates = 'trips' )
    trip = db.relationship( 'Trip', back_populates = 'users' )

user_payments = db.Table( 'user_payments',
    db.Column( 'user_id', db.Integer, db.ForeignKey( 'user.user_id' ), primary_key=True ),
    db.Column( 'payment_id', db.Integer, db.ForeignKey( 'payment.payment_id' ), primary_key=True )
)

class User( db.Model, UserMixin ):
    def get_id( self ):
        return ( self.user_id )
    user_id = db.Column( db.Integer, primary_key = True )
    email = db.Column( db.String(150), unique = True )
    nickname = db.Column( db.String(150), unique = True )
    password = db.Column( db.String(150) )
    localtrip_id = db.Column( db.Integer )
    trips = db.relationship( 'User_trips', back_populates = 'user' )
    admin_trips = db.relationship( 'Trip' )
    payers = db.relationship( 'Payment' )
    messages_addressee = db.relationship( 'Messages', backref = 'addressee', lazy = 'dynamic', 
        foreign_keys = 'Messages.addressee_id' )
    messages_recipient = db.relationship( 'Messages', backref = 'recipient', lazy = 'dynamic', 
        foreign_keys = 'Messages.recipient_id' ) 

class Trip( db.Model ):
    __tablename__ = 'trip'
    trip_id = db.Column( db.Integer, primary_key = True )
    admin_id = db.Column( db.Integer, db.ForeignKey( 'user.user_id' ) )
    users = db.relationship( 'User_trips', back_populates = 'trip' )
    trip_name = db.Column( db.String(150) )
    trip_admin_name = db.Column( db.String(150), unique = True )
    date = db.Column( db.DateTime( timezone = True ), default = func.now() )
    payments = db.relationship( 'Payment' )
    messages = db.relationship( 'Messages' )
    transactions = db.relationship( 'Transactions' )
    
class Payment( db.Model ):
    payment_id = db.Column( db.Integer, primary_key = True )
    trip_id = db.Column( db.Integer, db.ForeignKey( 'trip.trip_id' ) )
    users = db.relationship( 'User', secondary = user_payments, lazy='subquery',
        backref = db.backref( 'payments' ) )
    payer_id = db.Column( db.Integer, db.ForeignKey( 'user.user_id' ) )
    payment_name = db.Column( db.String(150) )
    date = db.Column( db.DateTime( timezone = True ), default = func.now() )
    price = db.Column( db.Float )
    
class Messages( db.Model ):
    id = db.Column( db.Integer, primary_key = True )
    addressee_id = db.Column( db.Integer, db.ForeignKey( 'user.user_id' ) )
    recipient_id = db.Column( db.Integer, db.ForeignKey( 'user.user_id' ) )
    trip_id = db.Column( db.Integer, db.ForeignKey( 'trip.trip_id' ) )
    date = db.Column( db.DateTime( timezone = True ), default = func.now() )
    message = db.Column( db.String(150) )
    answer = db.Column( db.String(150) )

class Transactions( db.Model ):
    id = db.Column( db.Integer, primary_key = True )
    trip_id = db.Column( db.Integer, db.ForeignKey( 'trip.trip_id' ) )
    message = db.Column( db.String(150) )

