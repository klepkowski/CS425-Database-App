from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error, IntegrityError

app = Flask(__name__)

# CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///f1.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    team = db.Column(db.String(100), nullable=False)
    championships = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Driver {self.name}>'

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<Team {self.name}>'

class RaceTrack(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    length = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<RaceTrack {self.name}>'
    
def create_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="0406",
            database="formula1"
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(e)

def close_connection(connection):
    if connection.is_connected():
        connection.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/racetracks', methods=['GET'])
def get_racetracks():
    racetracks = RaceTrack.query.all()
    return jsonify([{'id': racetrack.id, 'name': racetrack.name, 'length': racetrack.length} for racetrack in racetracks])

@app.route('/racetracks/<int:id>', methods=['GET'])
def get_racetrack(id):
    racetrack = RaceTrack.query.get_or_404(id)
    return jsonify({'id': racetrack.id, 'name': racetrack.name, 'length': racetrack.length})

@app.route('/racetracks', methods=['POST'])
def add_racetrack():
    data = request.get_json()
    new_racetrack = RaceTrack(name=data['name'], length=data['length'])
    db.session.add(new_racetrack)
    db.session.commit()
    return jsonify({'message': 'Race track added successfully'}), 201

@app.route('/racetracks/<int:id>', methods=['PUT'])
def update_racetrack(id):
    data = request.get_json()
    racetrack = RaceTrack.query.get_or_404(id)
    racetrack.name = data['name']
    racetrack.length = data['length']
    db.session.commit()
    return jsonify({'message': 'Race track updated successfully'})

@app.route('/racetracks/<int:id>', methods=['DELETE'])
def delete_racetrack(id):
    racetrack = RaceTrack.query.get_or_404(id)
    db.session.delete(racetrack)
    db.session.commit()
    return jsonify({'message': 'Race track deleted successfully'})

@app.route('/teams', methods=['GET'])
def get_teams():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM team")
    teams = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify(teams), 200

@app.route('/teams', methods=['POST'])
def add_team():
    data = request.json
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO team (TeamID, Name, Location, TeamPrincipal, Chassis, PowerUnit, FirstTeamEntry, WorldChampionships, PolePositions, FastestLaps)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (data['team_id'], data['name'], data['location'], data['team_principal'], data['chassis'], data['power_unit'], data['first_team_entry'], data['world_championships'], data['pole_positions'], data['fastest_laps']))
        connection.commit()
        return jsonify({"message": "Team added successfully!"}), 201
    except IntegrityError as e:
        if e.errno == 1062:
            return jsonify({"error": "Duplicate entry"}), 409
        else:
            return jsonify({"error": str(e)}), 400
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/teams/<int:id>', methods=['PUT'])
def update_team(id):
    data = request.json
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE team
            SET Name = %s, Location = %s, TeamPrincipal = %s, Chassis = %s, PowerUnit = %s, FirstTeamEntry = %s, WorldChampionships = %s, PolePositions = %s, FastestLaps = %s
            WHERE TeamID = %s
        """, (data['name'], data['location'], data['team_principal'], data['chassis'], data['power_unit'], data['first_team_entry'], data['world_championships'], data['pole_positions'], data['fastest_laps'], id))
        connection.commit()
        return jsonify({"message": "Team updated successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/teams/<int:id>', methods=['DELETE'])
def delete_team(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM team WHERE TeamID = %s", (id,))
        connection.commit()
        return jsonify({"message": "Team deleted successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/teams/<int:id>', methods=['GET'])
def get_team(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM team WHERE TeamID = %s", (id,))
    team = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if team:
        return jsonify(team), 200
    else:
        return jsonify({"error": "Team not found"}), 404

@app.route('/drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()
    return jsonify([{'id': driver.id, 'name': driver.name, 'team': driver.team, 'championships': driver.championships} for driver in drivers])

@app.route('/drivers/<int:id>', methods=['GET'])
def get_driver(id):
    driver = Driver.query.get_or_404(id)
    return jsonify({'id': driver.id, 'name': driver.name, 'team': driver.team, 'championships': driver.championships})

@app.route('/drivers', methods=['POST'])
def add_driver():
    data = request.get_json()
    new_driver = Driver(name=data['name'], team=data['team'], championships=data['championships'])
    db.session.add(new_driver)
    db.session.commit()
    return jsonify({'message': 'Driver added successfully'}), 201

@app.route('/drivers/<int:id>', methods=['PUT'])
def update_driver(id):
    data = request.get_json()
    driver = Driver.query.get_or_404(id)
    driver.name = data['name']
    driver.team = data['team']
    driver.championships = data['championships']
    db.session.commit()
    return jsonify({'message': 'Driver updated successfully'})

@app.route('/drivers/<int:id>', methods=['DELETE'])
def delete_driver(id):
    driver = Driver.query.get_or_404(id)
    db.session.delete(driver)
    db.session.commit()
    return jsonify({'message': 'Driver deleted successfully'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', threaded=True, debug=True)
