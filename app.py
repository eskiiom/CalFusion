from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import json
from flask_sqlalchemy import SQLAlchemy
from icalendar import Calendar as ICalendar, Event
from dateutil import parser
import pytz
import caldav
from caldav.elements import dav, cdav
import vobject
import base64
import re
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import secrets

load_dotenv()

# Configuration pour autoriser HTTP en développement local
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Définition des chemins et URLs
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')
CALENDAR_FILE = os.path.join(STATIC_DIR, 'combined_calendar.ics')
APP_BASE_URL = os.getenv('APP_BASE_URL', 'http://localhost:5000')

# Création du dossier static s'il n'existe pas
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendars.db'
db = SQLAlchemy(app)

# Configuration de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    google_id = db.Column(db.String(100), unique=True)
    calendar_token = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    calendars = db.relationship('CalendarModel', backref='user', lazy=True)

    def __init__(self, email, name, google_id):
        self.email = email
        self.name = name
        self.google_id = google_id
        self.calendar_token = secrets.token_urlsafe(48)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class CalendarModel(db.Model):
    __tablename__ = 'calendar'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'google' ou 'icloud'
    credentials = db.Column(db.Text)
    calendar_id = db.Column(db.String(100))
    color = db.Column(db.String(7))
    active = db.Column(db.Boolean, default=True)
    url = db.Column(db.Text)  # Pour stocker l'URL CalDAV pour iCloud
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Supprime et recrée la base de données
with app.app_context():
    db.drop_all()
    db.create_all()

SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/calendar.readonly'
]

@app.route('/')
@login_required
def index():
    calendars = CalendarModel.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', calendars=calendars)

@app.route('/add_google_calendar')
def add_google_calendar():
    redirect_uri = os.getenv("REDIRECT_URI")
    if not redirect_uri:
        return "Error: REDIRECT_URI not configured", 500
        
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    try:
        # Vérifier si l'état est présent dans la session
        if 'state' not in session:
            flash('Session invalide. Veuillez réessayer.', 'error')
            return redirect(url_for('login'))

        # Récupérer l'état de la session
        state = session['state']
        
        # Vérifier si le state correspond
        if request.args.get('state', '') != state:
            flash('État de session invalide. Veuillez réessayer.', 'error')
            return redirect(url_for('login'))
            
        # Vérifier si le code est présent
        if 'code' not in request.args:
            flash('Aucun code d\'autorisation reçu.', 'error')
            return redirect(url_for('login'))

        redirect_uri = os.getenv("REDIRECT_URI")
        if not redirect_uri:
            flash('URI de redirection non configurée.', 'error')
            return redirect(url_for('login'))
            
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                    "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri]
                }
            },
            scopes=SCOPES,
            state=state,
            redirect_uri=redirect_uri
        )
        
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials

        # Récupérer les informations de l'utilisateur
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()

        # Chercher l'utilisateur ou en créer un nouveau
        user = User.query.filter_by(google_id=user_info['id']).first()
        if not user:
            user = User(
                email=user_info['email'],
                name=user_info.get('name', user_info['email']),
                google_id=user_info['id']
            )
            db.session.add(user)
            db.session.commit()
            flash('Compte créé avec succès !', 'success')
        
        # Connecter l'utilisateur
        login_user(user)
        
        # Stockage des informations d'identification communes
        creds_info = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': os.getenv("GOOGLE_CLIENT_ID"),
            'client_secret': os.getenv("GOOGLE_CLIENT_SECRET"),
            'scopes': credentials.scopes
        }
        
        # Récupérer les calendriers Google
        calendar_service = build('calendar', 'v3', credentials=credentials)
        calendar_list = calendar_service.calendarList().list().execute()
        
        for calendar in calendar_list.get('items', []):
            # Vérifier si le calendrier existe déjà pour cet utilisateur
            existing_calendar = CalendarModel.query.filter_by(
                calendar_id=calendar['id'],
                user_id=user.id
            ).first()
            
            if not existing_calendar:
                # Créer une copie des credentials pour chaque calendrier
                calendar_creds = creds_info.copy()
                
                new_calendar = CalendarModel(
                    name=calendar['summary'],
                    type='google',
                    credentials=json.dumps(calendar_creds),
                    calendar_id=calendar['id'],
                    color=calendar.get('backgroundColor', '#4285f4'),
                    user_id=user.id
                )
                db.session.add(new_calendar)
        
        db.session.commit()
        flash('Calendriers Google ajoutés avec succès!', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        app.logger.error(f"Erreur dans oauth2callback: {str(e)}")
        flash(f'Erreur lors de l\'authentification: {str(e)}', 'error')
        return redirect(url_for('login'))

def get_google_calendar_events(calendar, start_date=None, end_date=None):
    """Récupère les événements d'un calendrier Google."""
    if not start_date:
        start_date = datetime.now(pytz.UTC)
    if not end_date:
        end_date = start_date + timedelta(days=30)
    
    try:
        creds_info = json.loads(calendar.credentials)
        # Vérifier que toutes les informations nécessaires sont présentes
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        if not all(field in creds_info for field in required_fields):
            raise ValueError("Informations d'identification incomplètes")
            
        credentials = Credentials(
            token=creds_info['token'],
            refresh_token=creds_info['refresh_token'],
            token_uri=creds_info['token_uri'],
            client_id=creds_info['client_id'],
            client_secret=creds_info['client_secret'],
            scopes=creds_info['scopes']
        )
        
        service = build('calendar', 'v3', credentials=credentials)
        events_result = service.events().list(
            calendarId=calendar.calendar_id,
            timeMin=start_date.isoformat(),
            timeMax=end_date.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        return events_result.get('items', [])
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des événements: {str(e)}")
        return []

@app.route('/add_icloud_calendar', methods=['GET', 'POST'])
@login_required
def add_icloud_calendar():
    """Ajoute un calendrier iCloud via CalDAV."""
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            app.logger.info(f"Tentative de connexion iCloud pour l'utilisateur: {username}")
            
            # Connexion au serveur CalDAV d'iCloud
            caldav_url = os.getenv('ICLOUD_CALDAV_URL')
            app.logger.info(f"Connexion à l'URL CalDAV: {caldav_url}")
            
            client = caldav.DAVClient(
                url=caldav_url,
                username=username,
                password=password
            )
            app.logger.info("Client CalDAV créé avec succès")
            
            # Récupération des calendriers
            app.logger.info("Tentative de récupération du principal...")
            principal = client.principal()
            app.logger.info("Principal récupéré, recherche des calendriers...")
            calendars = principal.calendars()
            app.logger.info(f"Nombre de calendriers trouvés: {len(calendars)}")
            
            # Stockage des informations d'identification encodées
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            
            for cal in calendars:
                app.logger.info(f"Traitement du calendrier: {cal.url.path}")
                # Vérifier si le calendrier existe déjà pour cet utilisateur
                existing_calendar = CalendarModel.query.filter_by(
                    calendar_id=cal.url.path,
                    user_id=current_user.id
                ).first()
                
                if not existing_calendar:
                    try:
                        display_name = str(cal.get_properties([dav.DisplayName()])[dav.DisplayName()])
                        app.logger.info(f"Nom du calendrier: {display_name}")
                    except Exception as e:
                        app.logger.warning(f"Impossible de récupérer le nom du calendrier: {str(e)}")
                        display_name = "Calendrier iCloud"
                    
                    new_calendar = CalendarModel(
                        name=display_name,
                        type='icloud',
                        credentials=credentials,
                        calendar_id=cal.url.path,
                        color='#FF9500',
                        url=str(cal.url),
                        user_id=current_user.id
                    )
                    db.session.add(new_calendar)
                    app.logger.info(f"Calendrier ajouté à la base de données: {display_name}")
            
            db.session.commit()
            app.logger.info("Tous les calendriers ont été enregistrés avec succès")
            flash('Calendriers iCloud ajoutés avec succès!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            app.logger.error(f"Erreur lors de l'ajout des calendriers iCloud: {str(e)}", exc_info=True)
            flash(f'Erreur lors de l\'ajout des calendriers iCloud: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    return render_template('add_icloud.html')

def get_icloud_calendar_events(calendar, start_date=None, end_date=None):
    """Récupère les événements d'un calendrier iCloud."""
    try:
        if not start_date:
            start_date = datetime.now(pytz.UTC)
        if not end_date:
            end_date = start_date + timedelta(days=30)
        
        # Décodage des informations d'identification
        credentials = base64.b64decode(calendar.credentials).decode()
        username, password = credentials.split(':')
        
        # Connexion au calendrier
        client = caldav.DAVClient(
            url=calendar.url,
            username=username,
            password=password
        )
        cal = client.calendar(url=calendar.url)
        
        # Récupération des événements
        events = cal.date_search(
            start=start_date,
            end=end_date
        )
        
        return events
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des événements iCloud: {str(e)}")
        return []

def create_combined_calendar(calendars, start_date=None, end_date=None):
    """Crée un calendrier iCal combiné à partir de plusieurs calendriers."""
    combined_cal = ICalendar()
    combined_cal.add('prodid', '-//Calfusion//Combined Calendar//EN')
    combined_cal.add('version', '2.0')
    
    for calendar in calendars:
        if not calendar.active:
            continue
            
        if calendar.type == 'google':
            events = get_google_calendar_events(calendar, start_date, end_date)
            for event in events:
                cal_event = Event()
                cal_event.add('summary', f"[{calendar.name}] {event.get('summary', 'No Title')}")
                cal_event.add('description', event.get('description', ''))
                
                start = event['start'].get('dateTime', event['start'].get('date'))
                if isinstance(start, str):
                    start = parser.parse(start)
                cal_event.add('dtstart', start)
                
                end = event['end'].get('dateTime', event['end'].get('date'))
                if isinstance(end, str):
                    end = parser.parse(end)
                cal_event.add('dtend', end)
                
                cal_event.add('color', calendar.color)
                combined_cal.add_component(cal_event)
                
        elif calendar.type == 'icloud':
            events = get_icloud_calendar_events(calendar, start_date, end_date)
            for event in events:
                vevent = event.vobject_instance.vevent
                cal_event = Event()
                
                # Copie des propriétés de l'événement
                cal_event.add('summary', f"[{calendar.name}] {str(vevent.summary.value)}")
                if hasattr(vevent, 'description'):
                    cal_event.add('description', str(vevent.description.value))
                
                cal_event.add('dtstart', vevent.dtstart.value)
                cal_event.add('dtend', vevent.dtend.value)
                cal_event.add('color', calendar.color)
                
                combined_cal.add_component(cal_event)
    
    return combined_cal

@app.route('/calendar/<token>/combined.ics')
def get_combined_calendar(token):
    """Fournit le calendrier combiné au format iCal."""
    try:
        # Trouver l'utilisateur par son token
        user = User.query.filter_by(calendar_token=token).first_or_404()
        
        # Récupérer uniquement les calendriers de cet utilisateur
        calendars = CalendarModel.query.filter_by(user_id=user.id).all()
        if not calendars:
            return jsonify({"status": "error", "message": "Aucun calendrier trouvé"}), 404
        
        combined_cal = create_combined_calendar(calendars)
        ical_data = combined_cal.to_ical()
        
        # Renvoyer avec les en-têtes appropriés pour l'abonnement au calendrier
        response = Response(ical_data, 
                          mimetype='text/calendar; charset=utf-8')
        response.headers.update({
            'Content-Type': 'text/calendar; charset=utf-8',
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        })
        return response
    except Exception as e:
        app.logger.error(f"Erreur lors de la génération du calendrier: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/sync_calendars')
@login_required
def sync_calendars():
    """Synchronise les calendriers de l'utilisateur courant."""
    try:
        calendars = CalendarModel.query.filter_by(user_id=current_user.id).all()
        if not calendars:
            return jsonify({"status": "error", "message": "Aucun calendrier trouvé"})
        
        # Création du calendrier combiné
        combined_cal = create_combined_calendar(calendars)
        
        return jsonify({
            "status": "success",
            "message": "Calendriers synchronisés avec succès",
            "calendar_url": url_for('get_combined_calendar', 
                                  token=current_user.calendar_token, 
                                  _external=True)
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/toggle_calendar/<int:calendar_id>', methods=['POST'])
@login_required
def toggle_calendar(calendar_id):
    """Active ou désactive un calendrier."""
    try:
        calendar = CalendarModel.query.filter_by(
            id=calendar_id, 
            user_id=current_user.id
        ).first_or_404()
        
        calendar.active = not calendar.active
        db.session.commit()

        return jsonify({"status": "success", "active": calendar.active})
    except Exception as e:
        app.logger.error(f"Erreur lors de la mise à jour du calendrier: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_calendar_color/<int:calendar_id>', methods=['POST'])
@login_required
def update_calendar_color(calendar_id):
    """Met à jour la couleur d'un calendrier."""
    try:
        calendar = CalendarModel.query.filter_by(
            id=calendar_id, 
            user_id=current_user.id
        ).first_or_404()
        
        color = request.json.get('color')
        
        if not color or not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            return jsonify({'error': 'Couleur invalide'}), 400
            
        calendar.color = color
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Couleur mise à jour avec succès'})
    except Exception as e:
        app.logger.error(f"Erreur lors de la mise à jour de la couleur: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    session.pop('_flashes', None)  # Clear flash messages
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host=host, port=port, debug=True) 