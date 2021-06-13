function ansFunc( message ) {
    var index = message.lastIndexOf( ' ' );
    var trip_name = message.slice( index,  );

    message = message.replaceAll( ' ', '_' );
    var positive_ans = message + '=tak';
    var negative_ans = message + '=nie';
    var anwers = "Czy chcesz dolączyć do rachunku:" + trip_name + "?" +
        "<form method = 'POST'>" +
        "<button name = 'mess_answer' type = 'submit' class = 'button answer-btn' value = " + positive_ans + ">Tak</button>" +
        "<button name = 'mess_answer' type = 'submit' class = 'button answer-btn' value = " + negative_ans + ">Nie</button>" +
        "</form>"
    
    document.getElementById( 'answers' ).innerHTML = anwers;
}

function disableBtn() {
    if( document.getElementById( 'add-trip' ).value === '' ) { 
        document.getElementById( 'add-trip-btn' ).disabled = true;
    } 
    else { 
        document.getElementById( 'add-trip-btn' ).disabled = false;
    }
}

function defaultTab() {
    document.getElementById( 'defaultOpen' ).click();
    document.getElementById( 'defaultOpen2' ).click();
}

function openTab( evt, id, content, links ) {
    var i, tabcontent, tablinks;
  
    tabcontent = document.getElementsByClassName( content );
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = 'none';
    }

    tablinks = document.getElementsByClassName( links );
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace( ' active', '' );
    }
  
    document.getElementById( id ).style.display = 'block';
    evt.currentTarget.className += ' active';
}

function delAlert( type ) {
    if ( confirm( 'Czy na pewno chcesz usunąć ten ' + type + '?' ) ) {}
    else {
        document.getElementById( 'del-btn' ).value = false; 
    }
}