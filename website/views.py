from flask import Blueprint, render_template, request, flash, url_for
from flask_login import login_required, current_user
from werkzeug.utils import redirect
from .models import Trip, User, User_trips, Messages
from . import db

views = Blueprint( 'views', __name__ )


def trip_list():
    
    trip_list_by_user = User_trips.query.filter_by( user_id = current_user.user_id ).all()
    trip_list = []
    for user in trip_list_by_user:
        trip_list.append( db.session.query(Trip).get( user.trip_id ) )

    return trip_list

def message_list():
    all_messages = Messages.query.filter_by( recipient_id = current_user.user_id ).all()
    message_list = []
    for message in all_messages:
        message_list.append( message )

    return message_list

@views.route( '/', methods = [ 'GET', 'POST' ] )
@login_required
def display_home():
    if current_user.is_authenticated:
        if request.method == 'POST':
            trip = request.form.get( 'trip' )
        
            if trip:
                trip_name = Trip.query.filter_by( trip_admin_name = ( trip + current_user.nickname ) ).first()
                if trip_name:
                    flash( 'Nie możesz mieć dwóch tak samo nazwanych wyjazdów', category = 'error' )
                elif len( trip ) > 20:
                    flash( 'Nazwa wyjazdu musi mieć mniej niz 20 znaków', category = 'error' )
                else:
                    new_trip = Trip( admin_id = current_user.user_id, trip_name = trip, trip_admin_name = ( trip + current_user.nickname ) )
                    db.session.add( new_trip )
                    db.session.commit()
                
                    asso = User_trips( user_id = current_user.user_id, trip_id = 
                        db.session.query( Trip ).order_by( Trip.trip_id.desc() ).first().trip_id, user_debt = 0 ) 
                    db.session.add( asso )
                    db.session.commit()

                    return redirect( url_for( 'auth.trip', trip_id = new_trip.trip_id ))
            else:
                from_js = request.form.get( 'mess_answer' ).replace('=', ' ')

                message, answer = from_js.split()
                message = message.replace('_', ' ')
                
                mess_id = Messages.query.filter_by( message = message ).first()
                if mess_id:
                    if answer == 'tak':
                        mess_asso = User_trips( user_id = current_user.user_id, trip_id = 
                            Messages.query.filter_by( message = message ).first().trip_id, user_debt = 0 ) 
                        db.session.add( mess_asso )
                        db.session.commit()
                        
                        mess_id.answer = answer
                        db.session.commit()
                        
                    elif answer == 'nie':
                        db.session.delete( mess_id )
                        db.session.commit()

                
        return render_template( 'index.html', user = current_user, trip_list = trip_list(), message_list = message_list() )
    else:
        return render_template( 'index.html', user = current_user )

