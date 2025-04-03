from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response, flash
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
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
import requests
from sqlalchemy import text

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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # À changer en production
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)  # Session de 31 jours
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'

# Configuration de la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///calendars.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    calendars = db.relationship('Calendar', backref='user', lazy=True)

    def __init__(self, email, name, google_id):
        self.email = email
        self.name = name
        self.google_id = google_id
        self.calendar_token = secrets.token_urlsafe(48)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

class CalendarSource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'google', 'icloud', 'ics'
    credentials = db.Column(db.Text)  # Pour stocker les informations d'identification encodées
    url = db.Column(db.Text)  # Pour les sources ICS ou les URLs CalDAV
    last_sync = db.Column(db.DateTime)
    is_connected = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    calendars = db.relationship('Calendar', backref='calendar_source', lazy=True)

    def __repr__(self):
        return f'<CalendarSource {self.name} ({self.type})>'

class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    calendar_id = db.Column(db.String(500), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('calendar_source.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    color = db.Column(db.String(9), nullable=False, default='#FF9500FF')  # Format: #RRGGBBAA
    order = db.Column(db.Integer, default=0)  # Pour stocker calendar-order
    description = db.Column(db.Text)  # Pour stocker calendar-description
    last_modified = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    @property
    def display_color(self):
        """Retourne la couleur au format RGB pour l'affichage."""
        return rgba_to_rgb(self.color)

    def __repr__(self):
        return f'<Calendar {self.name}>'

# Création de la base de données si elle n'existe pas
with app.app_context():
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
    app.logger.info(f"Accès à l'index - Utilisateur authentifié: {current_user.is_authenticated}")
    app.logger.info(f"Email de l'utilisateur: {current_user.email if current_user.is_authenticated else 'Non connecté'}")
    calendars = Calendar.query.filter_by(user_id=current_user.id).all()
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
        app.logger.info("Début de oauth2callback")
        if 'state' not in session:
            app.logger.error("Pas d'état dans la session")
            flash('Session invalide. Veuillez réessayer.', 'error')
            return redirect(url_for('login'))

        state = session['state']
        app.logger.info(f"État de la session récupéré: {state}")
        
        if request.args.get('state', '') != state:
            app.logger.error(f"État non correspondant: {request.args.get('state', '')} vs {state}")
            flash('État de session invalide. Veuillez réessayer.', 'error')
            return redirect(url_for('login'))
            
        if 'code' not in request.args:
            app.logger.error("Pas de code dans les arguments")
            flash('Aucun code d\'autorisation reçu.', 'error')
            return redirect(url_for('login'))

        app.logger.info("Code d'autorisation reçu")
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
        app.logger.info(f"Utilisateur connecté: {user.email}")
        app.logger.info(f"Authentifié: {current_user.is_authenticated}")
        
        # Stockage des informations d'identification
        creds_info = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': os.getenv("GOOGLE_CLIENT_ID"),
            'client_secret': os.getenv("GOOGLE_CLIENT_SECRET"),
            'scopes': credentials.scopes
        }
        
        # Créer ou mettre à jour la source Google
        google_source = CalendarSource.query.filter_by(
            user_id=user.id,
            type='google'
        ).first()
        
        if not google_source:
            google_source = CalendarSource(
                name='Google Calendar',
                type='google',
                user_id=user.id,
                credentials=json.dumps(creds_info),
                is_connected=True,
                last_sync=datetime.now(timezone.utc)
            )
            db.session.add(google_source)
            db.session.flush()  # Pour obtenir l'ID de la source
        else:
            google_source.credentials = json.dumps(creds_info)
            google_source.is_connected = True
            google_source.last_sync = datetime.now(timezone.utc)
        
        # Récupérer les calendriers Google
        calendar_service = build('calendar', 'v3', credentials=credentials)
        calendar_list = calendar_service.calendarList().list().execute()
        
        for calendar in calendar_list.get('items', []):
            # Vérifier si le calendrier existe déjà pour cet utilisateur
            existing_calendar = Calendar.query.filter_by(
                calendar_id=calendar['id'],
                user_id=user.id
            ).first()
            
            if not existing_calendar:
                new_calendar = Calendar(
                    name=calendar['summary'],
                    source_id=google_source.id,
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
        if not calendar.credentials:
            app.logger.error(f"Pas d'informations d'identification pour le calendrier {calendar.name}")
            return []

        creds_info = json.loads(calendar.credentials)
        # Vérifier que toutes les informations nécessaires sont présentes
        required_fields = ['token', 'refresh_token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        if not all(field in creds_info for field in required_fields):
            app.logger.error(f"Informations d'identification incomplètes pour le calendrier {calendar.name}")
            return []
            
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
    except json.JSONDecodeError:
        app.logger.error(f"Erreur de décodage JSON pour le calendrier {calendar.name}")
        return []
    except Exception as e:
        app.logger.error(f"Erreur lors de la récupération des événements pour {calendar.name}: {str(e)}")
        return []

@app.route('/add_icloud_calendar', methods=['GET', 'POST'])
@login_required
def add_icloud_calendar():
    """Ajoute un calendrier iCloud via CalDAV."""
    if request.method == 'GET':
        return render_template('add_icloud.html')
        
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            
            app.logger.info(f"Tentative de connexion iCloud pour l'utilisateur: {username}")
            
            # Connexion au serveur CalDAV d'iCloud
            caldav_url = os.getenv('ICLOUD_CALDAV_URL', 'https://caldav.icloud.com')
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
            
            # Créer ou mettre à jour la source iCloud
            icloud_source = CalendarSource.query.filter_by(
                user_id=current_user.id,
                type='icloud'
            ).first()
            
            if not icloud_source:
                icloud_source = CalendarSource(
                    name='iCloud Calendar',
                    type='icloud',
                    user_id=current_user.id,
                    credentials=credentials,
                    url=caldav_url,
                    is_connected=True,
                    last_sync=datetime.now(timezone.utc)
                )
                db.session.add(icloud_source)
                db.session.flush()
            else:
                icloud_source.credentials = credentials
                icloud_source.url = caldav_url
                icloud_source.is_connected = True
                icloud_source.last_sync = datetime.now(timezone.utc)
                Calendar.query.filter_by(source_id=icloud_source.id).update({'active': True})
            
            for cal in calendars:
                app.logger.info(f"Traitement du calendrier: {cal.url.path}")
                existing_calendar = Calendar.query.filter_by(
                    calendar_id=cal.url.path,
                    user_id=current_user.id
                ).first()
                
                if not existing_calendar:
                    try:
                        app.logger.info(f"Débug - Examen des propriétés pour le calendrier: {cal.url.path}")
                        
                        # Préparer la requête PROPFIND
                        headers = {
                            'Depth': '0',
                            'Content-Type': 'application/xml; charset=utf-8',
                            'Authorization': f'Basic {base64.b64encode(f"{username}:{password}".encode()).decode()}'
                        }
                        
                        body = """<?xml version="1.0" encoding="utf-8" ?>
                            <D:propfind xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:I="http://apple.com/ns/ical/">
                                <D:prop>
                                    <D:displayname/>
                                    <C:calendar-description/>
                                    <I:calendar-color/>
                                    <I:calendar-order/>
                                </D:prop>
                            </D:propfind>"""
                        
                        response = requests.request(
                            'PROPFIND',
                            f"{caldav_url}{cal.url.path}",
                            headers=headers,
                            data=body.encode('utf-8')
                        )
                        
                        app.logger.info(f"Réponse PROPFIND: {response.status_code}")
                        app.logger.debug(f"Contenu de la réponse: {response.text}")
                        
                        display_name = None
                        calendar_color = '#FF9500FF'  # Couleur par défaut avec alpha
                        calendar_order = 0
                        calendar_description = None
                        
                        if response.status_code == 207:  # Multi-Status
                            from xml.etree import ElementTree
                            root = ElementTree.fromstring(response.content)
                            
                            # Recherche des propriétés dans la réponse XML
                            for propstat in root.findall('.//{DAV:}propstat'):
                                status = propstat.find('{DAV:}status')
                                if status is not None and '200 OK' in status.text:
                                    prop = propstat.find('{DAV:}prop')
                                    if prop is not None:
                                        # Nom du calendrier
                                        displayname_elem = prop.find('{DAV:}displayname')
                                        if displayname_elem is not None and displayname_elem.text:
                                            display_name = displayname_elem.text.strip()
                                            app.logger.info(f"Nom trouvé via PROPFIND: {display_name}")
                                        
                                        # Couleur du calendrier
                                        color_elem = prop.find('{http://apple.com/ns/ical/}calendar-color')
                                        if color_elem is not None and color_elem.text:
                                            calendar_color = color_elem.text.strip()
                                            app.logger.info(f"Couleur trouvée: {calendar_color}")
                                        
                                        # Ordre du calendrier
                                        order_elem = prop.find('{http://apple.com/ns/ical/}calendar-order')
                                        if order_elem is not None and order_elem.text:
                                            try:
                                                calendar_order = int(order_elem.text.strip())
                                                app.logger.info(f"Ordre trouvé: {calendar_order}")
                                            except ValueError:
                                                app.logger.warning(f"Ordre invalide: {order_elem.text}")
                                        
                                        # Description du calendrier
                                        desc_elem = prop.find('{urn:ietf:params:xml:ns:caldav}calendar-description')
                                        if desc_elem is not None and desc_elem.text:
                                            calendar_description = desc_elem.text.strip()
                                            app.logger.info(f"Description trouvée: {calendar_description}")
                            
                    except Exception as e:
                        app.logger.warning(f"Erreur lors de la récupération des propriétés via PROPFIND: {str(e)}")

                    # Si le nom n'est pas trouvé, utiliser l'ID avec mapping
                    if not display_name:
                        path = cal.url.path.rstrip('/')
                        calendar_id = path.split('/')[-1]
                        
                        # Mapping simple pour les cas spéciaux
                        name_mapping = {
                            'home': 'Calendrier',
                            'work': 'Travail',
                            'family': 'Family',
                            'personal': 'Personnel'
                        }
                        
                        display_name = name_mapping.get(calendar_id, calendar_id)
                    
                    app.logger.info(f"Nom final du calendrier: {display_name}")
                    
                    new_calendar = Calendar(
                        name=display_name,
                        source_id=icloud_source.id,
                        calendar_id=cal.url.path,
                        color=calendar_color,
                        order=calendar_order,
                        description=calendar_description,
                        user_id=current_user.id,
                        last_modified=datetime.now(timezone.utc)
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
            
        if calendar.source_id == 1:
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
                
        elif calendar.source_id == 2:
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
        calendars = Calendar.query.filter_by(user_id=user.id).all()
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
        calendars = Calendar.query.filter_by(user_id=current_user.id).all()
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
        calendar = Calendar.query.filter_by(
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
        calendar = Calendar.query.filter_by(
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
    # Clear all session data
    session.clear()
    # Logout the user
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'success')
    return redirect(url_for('login'))

@app.route('/sources')
@login_required
def manage_sources():
    """Page de gestion des sources de calendriers."""
    sources = CalendarSource.query.filter_by(user_id=current_user.id).all()
    return render_template('sources.html', sources=sources)

@app.route('/sources/<int:source_id>/refresh', methods=['POST'])
@login_required
def refresh_source(source_id):
    """Rafraîchit les calendriers d'une source."""
    try:
        source = CalendarSource.query.filter_by(
            id=source_id,
            user_id=current_user.id
        ).first_or_404()
        
        if source.type == 'google':
            # Récupérer les nouveaux calendriers Google
            creds_info = json.loads(source.credentials)
            credentials = Credentials(
                token=creds_info['token'],
                refresh_token=creds_info['refresh_token'],
                token_uri=creds_info['token_uri'],
                client_id=creds_info['client_id'],
                client_secret=creds_info['client_secret'],
                scopes=creds_info['scopes']
            )
            
            calendar_service = build('calendar', 'v3', credentials=credentials)
            calendar_list = calendar_service.calendarList().list().execute()
            
            for calendar in calendar_list.get('items', []):
                existing_calendar = Calendar.query.filter_by(
                    calendar_id=calendar['id'],
                    source_id=source.id
                ).first()
                
                if not existing_calendar:
                    new_calendar = Calendar(
                        name=calendar['summary'],
                        calendar_id=calendar['id'],
                        color=calendar.get('backgroundColor', '#4285f4'),
                        user_id=current_user.id,
                        source_id=source.id
                    )
                    db.session.add(new_calendar)
            
        elif source.type == 'icloud':
            # Récupérer les nouveaux calendriers iCloud
            credentials = base64.b64decode(source.credentials).decode()
            username, password = credentials.split(':')
            
            client = caldav.DAVClient(
                url=source.url,
                username=username,
                password=password
            )
            
            principal = client.principal()
            calendars = principal.calendars()
            
            for cal in calendars:
                existing_calendar = Calendar.query.filter_by(
                    calendar_id=cal.url.path,
                    source_id=source.id
                ).first()
                
                if not existing_calendar:
                    try:
                        display_name = str(cal.get_properties([dav.DisplayName()])[dav.DisplayName()])
                    except:
                        display_name = "Calendrier iCloud"
                    
                    new_calendar = Calendar(
                        name=display_name,
                        calendar_id=cal.url.path,
                        color='#FF9500',
                        user_id=current_user.id,
                        source_id=source.id
                    )
                    db.session.add(new_calendar)
        
        elif source.type == 'ics':
            # Vérifier que l'URL du calendrier ICS est toujours valide
            response = requests.get(source.url)
            if response.status_code == 200:
                source.is_connected = True
            else:
                source.is_connected = False
        
        source.last_sync = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        app.logger.error(f"Erreur lors du rafraîchissement de la source {source_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/sources/<int:source_id>/disconnect', methods=['POST'])
@login_required
def disconnect_source(source_id):
    """Déconnecte une source de calendriers."""
    try:
        source = CalendarSource.query.filter_by(
            id=source_id,
            user_id=current_user.id
        ).first_or_404()
        
        source.is_connected = False
        source.last_sync = None
        
        # Désactiver tous les calendriers de cette source
        Calendar.query.filter_by(source_id=source.id).update({'active': False})
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/sources/add_ics', methods=['POST'])
@login_required
def add_ics_source():
    """Ajoute une nouvelle source de calendrier ICS."""
    try:
        data = request.json
        name = data.get('name')
        url = data.get('url')
        
        if not name or not url:
            return jsonify({'success': False, 'error': 'Nom et URL requis'})
        
        # Vérifier que l'URL est valide et pointe vers un fichier ICS
        if url.startswith('webcal://'):
            url = 'https://' + url[9:]
        
        response = requests.get(url)
        if response.status_code != 200:
            return jsonify({'success': False, 'error': 'URL invalide'})
        
        # Vérifier que le contenu est bien un calendrier ICS
        try:
            Calendar.from_ical(response.content)
        except:
            return jsonify({'success': False, 'error': 'Le fichier n\'est pas un calendrier ICS valide'})
        
        # Créer la source
        source = CalendarSource(
            name=name,
            type='ics',
            url=url,
            user_id=current_user.id,
            is_connected=True,
            last_sync=datetime.now(timezone.utc)
        )
        db.session.add(source)
        
        # Créer le calendrier associé
        calendar = Calendar(
            name=name,
            calendar_id=url,
            color='#28a745',
            user_id=current_user.id,
            source_id=source.id,
            active=True
        )
        db.session.add(calendar)
        
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/sources/<int:source_id>', methods=['GET'])
@login_required
def get_source(source_id):
    """Récupère les informations d'une source."""
    source = CalendarSource.query.filter_by(
        id=source_id,
        user_id=current_user.id
    ).first_or_404()
    
    return jsonify({
        'name': source.name,
        'url': source.url
    })

@app.route('/sources/<int:source_id>/purge', methods=['POST'])
@login_required
def purge_source(source_id):
    """Purge une source et tous ses calendriers."""
    try:
        source = CalendarSource.query.filter_by(
            id=source_id,
            user_id=current_user.id
        ).first_or_404()
        
        # Supprimer tous les calendriers associés
        Calendar.query.filter_by(source_id=source.id).delete()
        
        # Supprimer la source
        db.session.delete(source)
        db.session.commit()
        
        flash('Source et calendriers associés supprimés avec succès.', 'success')
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erreur lors de la purge de la source {source_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

def migrate_to_sources():
    """Migre les calendriers existants vers le nouveau modèle de sources."""
    with app.app_context():
        try:
            # Vérifier si la migration est nécessaire
            if db.session.query(CalendarSource).first():
                print("Migration déjà effectuée")
                return

            # Vérifier la structure de la table calendar
            with db.engine.connect() as conn:
                # Obtenir les informations sur les colonnes de la table calendar
                columns = conn.execute(text("PRAGMA table_info(calendar)")).fetchall()
                column_names = [col[1] for col in columns]
                
                # Si la table n'a pas la colonne service, c'est une nouvelle installation
                if 'service' not in column_names:
                    print("Nouvelle installation - pas de migration nécessaire")
                    return

            # Récupérer tous les utilisateurs
            users = User.query.all()
            for user in users:
                # Créer une source Google si l'utilisateur a des calendriers Google
                google_calendars = db.session.execute(
                    text('SELECT * FROM calendar WHERE user_id = :user_id AND service = :service'),
                    {'user_id': user.id, 'service': 'google'}
                ).fetchall()
                
                if google_calendars:
                    google_source = CalendarSource(
                        name='Google Calendar',
                        type='google',
                        user_id=user.id,
                        credentials=google_calendars[0].credentials,
                        is_connected=True,
                        last_sync=datetime.now(timezone.utc)
                    )
                    db.session.add(google_source)
                    db.session.flush()  # Pour obtenir l'ID de la source
                    
                    # Mettre à jour les calendriers Google
                    for calendar in google_calendars:
                        db.session.execute(
                            text('UPDATE calendar SET source_id = :source_id WHERE id = :calendar_id'),
                            {'source_id': google_source.id, 'calendar_id': calendar.id}
                        )
                
                # Créer une source iCloud si l'utilisateur a des calendriers iCloud
                icloud_calendars = db.session.execute(
                    text('SELECT * FROM calendar WHERE user_id = :user_id AND service = :service'),
                    {'user_id': user.id, 'service': 'icloud'}
                ).fetchall()
                
                if icloud_calendars:
                    icloud_source = CalendarSource(
                        name='iCloud Calendar',
                        type='icloud',
                        user_id=user.id,
                        credentials=icloud_calendars[0].credentials,
                        url=icloud_calendars[0].url if hasattr(icloud_calendars[0], 'url') else None,
                        is_connected=True,
                        last_sync=datetime.now(timezone.utc)
                    )
                    db.session.add(icloud_source)
                    db.session.flush()  # Pour obtenir l'ID de la source
                    
                    # Mettre à jour les calendriers iCloud
                    for calendar in icloud_calendars:
                        db.session.execute(
                            text('UPDATE calendar SET source_id = :source_id WHERE id = :calendar_id'),
                            {'source_id': icloud_source.id, 'calendar_id': calendar.id}
                        )
            
            db.session.commit()
            
            # Recréer la table calendar sans les colonnes inutiles
            with db.engine.connect() as conn:
                # Créer une table temporaire avec la nouvelle structure
                conn.execute(text('''
                    CREATE TABLE calendar_new (
                        id INTEGER PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        source_id INTEGER NOT NULL,
                        calendar_id VARCHAR(500) NOT NULL,
                        name VARCHAR(200) NOT NULL,
                        color VARCHAR(7) DEFAULT '#4285F4',
                        active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY(user_id) REFERENCES user(id),
                        FOREIGN KEY(source_id) REFERENCES calendar_source(id)
                    )
                '''))
                
                # Copier les données
                conn.execute(text('''
                    INSERT INTO calendar_new (id, user_id, source_id, calendar_id, name, color, active, created_at, updated_at)
                    SELECT id, user_id, source_id, calendar_id, name, color, active, created_at, updated_at
                    FROM calendar
                '''))
                
                # Supprimer l'ancienne table et renommer la nouvelle
                conn.execute(text('DROP TABLE calendar'))
                conn.execute(text('ALTER TABLE calendar_new RENAME TO calendar'))
            
            print("Migration terminée avec succès")
            
        except Exception as e:
            print(f"Erreur lors de la migration : {str(e)}")
            db.session.rollback()

# Exécuter la migration lors du démarrage de l'application
with app.app_context():
    db.create_all()  # Créer les nouvelles tables
    migrate_to_sources()  # Migrer les données

def rgba_to_rgb(rgba_color):
    """Convertit une couleur RGBA en RGB."""
    if not rgba_color:
        return '#FF9500'
    
    # Si la couleur est déjà au format RGB (#RRGGBB)
    if len(rgba_color) == 7:
        return rgba_color
        
    # Si la couleur est au format RGBA (#RRGGBBAA)
    if len(rgba_color) == 9:
        return rgba_color[:7]
        
    # Format invalide, retourner la couleur par défaut
    return '#FF9500'

@app.route('/account/delete', methods=['POST'])
@login_required
def delete_account():
    """Supprime le compte de l'utilisateur et toutes ses données associées."""
    try:
        user_id = current_user.id
        
        # Supprimer tous les calendriers de l'utilisateur
        Calendar.query.filter_by(user_id=user_id).delete()
        
        # Supprimer toutes les sources de calendrier
        CalendarSource.query.filter_by(user_id=user_id).delete()
        
        # Supprimer l'utilisateur
        user = db.session.get(User, user_id)
        db.session.delete(user)
        
        # Déconnecter l'utilisateur
        logout_user()
        
        # Commit des changements
        db.session.commit()
        
        flash('Votre compte a été supprimé avec succès.', 'success')
        return redirect(url_for('login'))
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Erreur lors de la suppression du compte: {str(e)}")
        flash('Une erreur est survenue lors de la suppression du compte.', 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', 5000))
    app.run(host=host, port=port, debug=True) 