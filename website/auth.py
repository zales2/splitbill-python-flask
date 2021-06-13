from flask import Blueprint, render_template, request, flash, redirect, url_for, redirect, session
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Trip, Messages, User_trips, Payment, Transactions
import operator

auth = Blueprint( 'auth', __name__ )

class Users:
    def __init__( self, name, debt ):
        self.name = name
        self.debt = debt

def get_index( userlist ):
    mindebt = 0

    for i in range( len( userlist ) ):
        if userlist[i].debt > 0:
           mindebt -= userlist[i].debt
    for i in range( len( userlist ) ):
        if userlist[i].debt < 0 and userlist[i].debt >= mindebt:
            mindebt = userlist[i].debt
            index = i

    return index

def adminFunc( trip_name, trip_id ):
    trip = Trip.query.filter_by( trip_admin_name = ( trip_name + current_user.nickname ) ).first()
    if trip is None:
        admin = False      
    elif trip.trip_id != trip_id:
        return False
    else:
        admin = True
    return admin

def currentTransaction():
    return Transactions.query.filter_by( trip_id = session[ 'trip_id' ] ).all()

def currentDebt():
    return User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).all()

def currentDebt_list():
    users = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).all()
    userlist = []
    for user in users:
        userlist.append( localUsers( User.query.filter_by( user_id = user.user_id ).first().nickname ) )
    return userlist

def currentTrip():
    return Trip.query.filter_by( trip_id = session[ 'trip_id' ] ).first()    

def currentTrip_users():
    users = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).all()
    user_list = []
    for user in users:
        user_list.append( User.query.filter_by( user_id = user.user_id ).first().nickname )
    return user_list

def currentTrip_usersid():
    users = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).all()
    user_list = []
    for user in users:
        user_list.append( User.query.filter_by( user_id = user.user_id ).first().user_id)
    return user_list

def localTrip_users():
    users = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).all()
    user_list = []
    for user in users:
        user_list.append( localUsers( User.query.filter_by( user_id = user.user_id ).first().nickname ) )
    return user_list

def currentPayment( id ):
    return Payment.query.filter_by( payment_id = id ).first() 

def currentPayment_users( id ): 
    users = User.query.filter( User.payments.any( payment_id = id) ).all()
    users_id = []
    for user in users:
        if user.localtrip_id:
            if user.localtrip_id == session[ 'trip_id' ]:
                users_id.append( user.user_id )
        else:
            users_id.append( user.user_id )
    print(users_id)
    return users_id

def localUsers( nickname ):
    if ' ' in nickname:
        _, nick = nickname.split()
        nick += ' (local)'
        return nick
    return nickname

@auth.route( '/login', methods=['GET', 'POST'] )
def login():
    if request.method == 'POST':
        email = request.form.get( 'email' )
        password = request.form.get( 'password' )

        user = User.query.filter_by( email = email ).first()
        if user:
            if check_password_hash( user.password, password ):
                login_user( user, remember=True )
                
                return redirect( url_for( 'views.display_home' ) )
            else:
                flash( 'Wprowadzone hasło jest nieprawidłowe. Spróbuj ponownie', category = 'error' )
        else:
            flash( 'Wprowadzony email nie jest powiązany z żadnym kontem.', category = 'error' )

    return render_template( 'login.html', user = current_user )

@auth.route( '/logout' )
@login_required
def logout():
    logout_user()
    
    return redirect( url_for( 'views.display_home' ) )

@auth.route( '/sign-up', methods=[ 'GET', 'POST' ] )
def sign_up():
    if request.method == 'POST':
        email = request.form.get( 'email' )
        nickname = request.form.get( 'nickname' )
        password1 = request.form.get( 'password1' )
        password2 = request.form.get( 'password2' )

        user = User.query.filter_by( email = email ).first()
        existing_nickname = User.query.filter_by( nickname = nickname ).first()
        
        if user:
            flash( 'Podany email już istnieje.', category = 'error' )
        elif len( email ) < 5:
            flash( 'Wprowadzony email jest nieprawidłowy. Spróbuj ponownie.', category = 'error')
        elif existing_nickname:
            flash( 'Ten pseudonim jest już zajęty', category ='error' )
        elif len( nickname ) < 2:
            flash( 'Pseudonim musi posiadać więcej niż jeden znak', category ='error' )
        elif len( nickname ) > 12:
            flash( 'Pseudonim nie moze miec wiecej niz 12 znakow', category ='error' )
        elif ' ' in nickname:
            flash( 'Pseudonim nie moze zawierać spacji', category ='error' )
        elif password1 != password2:
            flash( 'Wprowadzone hasła nie są takie same.', category = 'error' )
        elif len( password1 ) < 6:
            flash( 'Hasło musi mieć conajmniej 6 znaków', category = 'error' )
        else:
            new_user = User( email = email, nickname = nickname, password = generate_password_hash( password1, method = 'sha256' ) )
            db.session.add( new_user )
            db.session.commit()
            login_user( new_user, remember = True )
            flash( 'Konto zostało utworzone!', category='success' )
            return redirect( url_for( 'views.display_home' ) )

    return render_template( 'sign_up.html', user = current_user )

@auth.route( '/trip/<int:trip_id>', methods=['GET', 'POST'] )
def trip( trip_id ):
    trip_name = Trip.query.filter_by( trip_id = trip_id ).first().trip_name
    session[ 'trip_id' ] = trip_id
    session[ 'admin_id' ] = Trip.query.filter_by( trip_id = trip_id ).first().admin_id

    if request.method == 'POST':
        get_payment = request.form.get( 'payment' )
        if get_payment:
            return redirect( url_for( 'auth.payment' ) )
        
        nick = request.form.get( 'user_nick' )
        
        trip = Trip.query.filter_by( trip_admin_name = ( trip_name + current_user.nickname ) ).first()
        user = User.query.filter_by( nickname = nick ).first()
        if nick:
            if nick == current_user.nickname:
                flash( 'Nie możesz wysłać zaproszenia do samego siebie', category = 'error' )
            elif user:
                recipient = User.query.filter_by( nickname = nick ).first()
                existing_message = Messages.query.filter_by( addressee_id = current_user.user_id ).filter_by( recipient_id = recipient.user_id ).first()
                if existing_message:
                    flash( 'Zaproszenie do tego użytkownika już zostało wysłane', category = 'error' )
                else:
                    send_message = Messages( addressee_id = current_user.user_id, recipient_id = recipient.user_id, 
                        trip_id = trip.trip_id, message = ( current_user.nickname + ' zaprasza cię do rachunku - ' + trip.trip_name ) )

                    db.session.add( send_message ) 
                    db.session.commit()
                    flash( 'Zaproszenie zostało wysłane', category = 'success' )
            else:
                flash( 'Podany nick nie pasuje do żadnego użytkownika', category = 'error' )
        
        local_nick = request.form.get( 'user_local_nick' )
        if local_nick:
            if ' ' in local_nick:
                flash( 'Pseudonim nie może zawierać spacji', category = 'error' )
            else:
                if local_nick:
                    local_full_nick = str( current_user.user_id ) + str( session[ 'trip_id' ] ) + ' ' + local_nick
                    existing_local = User.query.filter_by( nickname = local_full_nick ).first()
                    if existing_local:
                        flash( 'Ten pseudonim lokalny jest już zajęty', category ='error' )
                    else:    
                        new_user = User( nickname = local_full_nick, localtrip_id = session[ 'trip_id' ] )
                        db.session.add( new_user )
                        db.session.commit()

                        local_asso = User_trips( user_id = User.query.filter_by( nickname = local_full_nick ).first().user_id, 
                            trip_id = session[ 'trip_id' ], user_debt = 0 ) 
                        db.session.add( local_asso )    
                        db.session.commit()

        del_trip = request.form.get( 'deltrip' )
        if del_trip and del_trip != 'false':
            db.session.query( Trip ).filter( Trip.trip_id == session[ 'trip_id' ] ).delete()
            db.session.commit()

            db.session.query( User_trips ).filter( User_trips.trip_id == session[ 'trip_id' ] ).delete()
            db.session.commit()

            db.session.query( Messages ).filter( Messages.trip_id == session[ 'trip_id' ] ).delete()
            db.session.commit()

            db.session.query( Payment ).filter( Payment.trip_id == session[ 'trip_id' ] ).delete()
            db.session.commit()

            db.session.query( Transactions ).filter( Transactions.trip_id == session[ 'trip_id' ] ).delete()
            db.session.commit()

            db.session.query( User ).filter( User.localtrip_id == session[ 'trip_id' ] ).delete()
            db.session.commit()

            return redirect( url_for( 'views.display_home' ) )

    return render_template( 'trip.html', user = current_user, page_name = trip_name, admin = adminFunc( trip_name, trip_id ), 
        payments = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).all(), transactions = currentTransaction(), debt = currentDebt(), uslist = currentDebt_list() )

def split_algorithm( names ):
    userlist = []
    for name in names:
        member = User.query.filter_by( nickname = name ).first()
        debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first()
        userlist.append( Users( localUsers( name ), debt.user_debt ) )

    transactions = []
    while(True):
        userlist = sorted( userlist, key = operator.attrgetter('debt') ) 
        
        index = get_index( userlist )
        for i in range( len( userlist ) ):
            if userlist[ len( userlist ) - 1 - i ].debt >= ( userlist[ index ].debt * -1 ):
                transactions.append( userlist[ index ].name + ' przelewa: ' + str((userlist[ index ].debt * -1 )) + ' do ' + userlist[ len(userlist ) - 1 - i ].name )
                userlist[ len( userlist ) - 1 - i ].debt += userlist[ index ].debt
                userlist[ len( userlist ) - 1 - i ].debt = round( userlist[ len(userlist ) - 1 - i].debt, 2 )
                userlist[ index ].debt = 0
            
                break
            else:
                transactions.append( userlist[ index ].name + ' przelewa: ' + str( userlist[ len( userlist ) - 1 - i ].debt) + ' do ' + userlist[ len(userlist ) - 1 - i ].name )
                userlist[ index ].debt += userlist[ len( userlist ) - 1 - i].debt
                userlist[ index ].debt = round( userlist[ index ].debt, 2 )
                userlist[ len(userlist ) - 1 - i].debt = 0

        for i in range( len(userlist ) ):
            try:
                if userlist[i].debt == 0:
                    del userlist[i]
                    i -= 1
            except IndexError:
                break
        
        if index == 0:
            break
    
    db.session.query( Transactions ).filter( Transactions.trip_id == session[ 'trip_id' ] ).delete()
    db.session.commit()

    for transaction in transactions:
        add_transaction = Transactions( trip_id = session[ 'trip_id' ], message = transaction)
        
        db.session.add( add_transaction )
        db.session.commit()

@auth.route( '/payment', methods=['GET', 'POST'] )
def payment():
    if request.method == 'POST':
        members = request.form.getlist( 'members' )
        name = request.form.get( 'payment_name' )
        payer = request.form.get( 'payer' )
        price = request.form.get( 'price' )

        if name and payer and price and members:
            
            existing_name = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( payment_name = name ).first()
            if len( members ) == 1 and payer in members:
                flash( 'Nie możesz dodać wydatku, w którym płacisz sam za siebie', category = 'error' )
            elif existing_name:
                flash( 'Nie możesz mieć dwóch tak samo nazwanych płatności', category = 'error' )
            else:
                new_payment = Payment( trip_id = session[ 'trip_id' ], payer_id = User.query.filter_by( nickname = payer ).first().user_id, payment_name = name, price = price )
                
                db.session.add( new_payment )
                db.session.commit()

                payment = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( payment_name = name ).first()
                payment_payer = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( payment_name = name ).first()
                
                payment.users.append( User.query.filter_by( nickname = payer ).first() )
                db.session.add( payment )
                db.session.commit()

                add_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = payment_payer.payer_id ).first()
                if payer in members:
                    add_debt.user_debt += round( ( float( price ) - ( float( price ) / len( members ) ) ), 2 )
                    add_debt.user_debt = round( add_debt.user_debt, 2 )
                else:
                    add_debt.user_debt += round( float( price ), 2 )
                    add_debt.user_debt = round( add_debt.user_debt, 2 ) 
                
                db.session.commit()   

                for person in members:
                    member = User.query.filter_by( nickname = person ).first()
                    
                    payment.users.append( member )
                    db.session.add( payment )
                    db.session.commit()

                    if member.user_id != User.query.filter_by( nickname = payer ).first().user_id:
                        add_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first()
                        add_debt.user_debt -= round( ( float( price ) / len( members ) ), 2 )
                        add_debt.user_debt = round( add_debt.user_debt, 2 )
                        db.session.commit()

                names = currentTrip_users()

                countdebt = 0
                for name in names:
                    member = User.query.filter_by( nickname = name ).first()
                    debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first().user_debt
                    countdebt += debt
                    countdebt = round( countdebt, 2 )
                
                if countdebt < 0:
                    fix_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = session[ 'admin_id' ] ).first() 
                    fix_debt.user_debt -= countdebt
                    fix_debt.user_debt = round( fix_debt.user_debt, 2 )
                    db.session.commit()
                
                split_algorithm( names )
                return redirect( url_for( 'auth.trip', trip_id = session[ 'trip_id' ] ) )
        else:
            flash( 'Musisz wypełnić wszytskie pola by zatwierdzić płatność', category ='error' )

    return render_template( 'payment.html', user = current_user, trip = currentTrip(), trip_users = currentTrip_users(), trip_users_local = localTrip_users() )

def getback_balance( id ):
    payer_name = Payment.query.filter_by( payment_id = id ).first().payer_id
    payer = User.query.filter_by( user_id = payer_name ).first().nickname
    
    names_id = currentPayment_users( id )
    members = []
    for name_id in names_id:
        members.append( User.query.filter_by( user_id = name_id ).first().nickname )
    
    price = Payment.query.filter_by( payment_id = id ).first().price
    name = Payment.query.filter_by( payment_id = id ).first().payment_name

    payment_payer = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( payment_name = name ).first()

    add_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = payment_payer.payer_id ).first()
    if payer in members:
        add_debt.user_debt -= round( ( float( price ) - ( float( price ) / len( members ) ) ), 2 )
        add_debt.user_debt = round( add_debt.user_debt, 2 )
    else:
        add_debt.user_debt -= round( float( price ), 2 )
        add_debt.user_debt = round( add_debt.user_debt, 2 ) 
    
    db.session.commit()   
    for person in members:
        member = User.query.filter_by( nickname = person ).first()

        if member.user_id != User.query.filter_by( nickname = payer ).first().user_id:
            add_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first()
            add_debt.user_debt += round( ( float( price ) / len( members ) ), 2 )
            add_debt.user_debt = round( add_debt.user_debt, 2 ) 
            db.session.commit()   

    names = currentTrip_users()

    countdebt = 0
    for name in names:
        member = User.query.filter_by( nickname = name ).first()
        debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first().user_debt
        countdebt += debt
        countdebt = round( countdebt, 2 )
    
    if countdebt < 0:
        fix_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = session[ 'admin_id' ] ).first() 
        fix_debt.user_debt += countdebt
        fix_debt.user_debt = round( fix_debt.user_debt, 2 )
        db.session.commit()

@auth.route( '/editpayment/<int:payment_id>', methods=['GET', 'POST'] )
def editpayment( payment_id ):
    if request.method == 'POST':
        members = request.form.getlist( 'members' )
        name = request.form.get( 'payment_name' )
        payer = request.form.get( 'payer' )
        price = request.form.get( 'price' )

        del_pay = request.form.get( 'delpayment' )
        if del_pay and del_pay != 'false':
            payments = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).all()
            if len( payments ) > 1:
                getback_balance( payment_id )

                db.session.query( Payment ).filter( Payment.payment_id == payment_id ).delete()
                db.session.commit()

                split_algorithm( currentTrip_users() )

            else:
                db.session.query( Payment ).filter( Payment.payment_id == payment_id ).delete()
                db.session.commit()

                db.session.query( Transactions ).filter( Transactions.trip_id == session[ 'trip_id' ] ).delete()
                db.session.commit()

                for person in members:
                    member = User.query.filter_by( nickname = person ).first()
                    add_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first()
                    add_debt.user_debt = 0
                    db.session.commit()

            return redirect( url_for( 'auth.trip', trip_id = session[ 'trip_id' ] ) )

        else:
            if name and payer and price and members:
                if len( members ) == 1 and payer in members:
                    flash( 'Nie możesz dodać wydatku, w którym płacisz sam za siebie', category = 'error' )
                else:
                    getback_balance( payment_id )

                    db.session.query( Payment ).filter( Payment.payment_id == payment_id ).delete()
                    db.session.commit()

                    new_payment = Payment( trip_id = session[ 'trip_id' ], payer_id = User.query.filter_by( nickname = payer ).first().user_id, payment_name = name, price = price )
                
                    db.session.add( new_payment )
                    db.session.commit()

                    payment = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( payment_name = name ).first()
                    payment_payer = Payment.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( payment_name = name ).first()
                    
                    payment.users.append( User.query.filter_by( nickname = payer ).first() )
                    db.session.add( payment )
                    db.session.commit()

                    add_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = payment_payer.payer_id ).first()
                    if payer in members:
                        add_debt.user_debt += round( ( float( price ) - ( float( price ) / len( members ) ) ), 2 )
                        add_debt.user_debt = round( add_debt.user_debt, 2 )
                    else:
                        add_debt.user_debt += round( float( price ), 2 )
                        add_debt.user_debt = round( add_debt.user_debt, 2 ) 
                    
                    db.session.commit()   

                    for person in members:
                        member = User.query.filter_by( nickname = person ).first()
                        
                        payment.users.append( member )
                        db.session.add( payment )
                        db.session.commit()

                        if member.user_id != User.query.filter_by( nickname = payer ).first().user_id:
                            add_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first()
                            add_debt.user_debt -= round( ( float( price ) / len( members ) ), 2 )
                            add_debt.user_debt = round( add_debt.user_debt, 2 )
                            db.session.commit()

                    names = currentTrip_users()

                    countdebt = 0
                    for name in names:
                        member = User.query.filter_by( nickname = name ).first()
                        debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = member.user_id ).first().user_debt
                        countdebt += debt
                        countdebt = round( countdebt, 2 )
                    
                    if countdebt < 0:
                        fix_debt = User_trips.query.filter_by( trip_id = session[ 'trip_id' ] ).filter_by( user_id = session[ 'admin_id' ] ).first() 
                        fix_debt.user_debt -= countdebt
                        fix_debt.user_debt = round( fix_debt.user_debt, 2 )
                        db.session.commit()
                    
                    split_algorithm( names )

                    return redirect( url_for( 'auth.trip', trip_id = session[ 'trip_id' ] ) )
            else:
                flash( 'Musisz wypełnić wszytskie pola by zatwierdzić płatność', category ='error' )

    return render_template( 'payment.html', user = current_user, trip = currentTrip(), trip_users = currentTrip_users(), 
        trip_usersid = currentTrip_usersid(), trip_users_local = localTrip_users(), payment = currentPayment( payment_id ), 
        payment_users = currentPayment_users( payment_id ), edit = True )