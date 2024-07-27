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
    __tablename__ = 'racetrack'
    racetrackID = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50), nullable=False)
    circuitLength = db.Column(db.Float, nullable=False)
    numberOfLaps = db.Column(db.Integer, nullable=False)
    lapRecord = db.Column(db.String(20), nullable=False)
    firstGrandPrix = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<RaceTrack {self.racetrackID}>'

class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    driversChampionID = db.Column(db.Integer, nullable=False)
    constructorsChampionID = db.Column(db.Integer, nullable=False)

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

@app.route('/season')
def season():
    return render_template('season.html')

@app.route('/api/season', methods=['GET'])
def get_seasons():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM season")
    seasons = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify(seasons), 200

@app.route('/api/season/<int:id>', methods=['GET'])
def get_season(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM season WHERE SeasonID = %s", (id,))
    season = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if season:
        return jsonify(season), 200
    else:
        return jsonify({"error": "Season not found"}), 404
 
@app.route('/api/season', methods=['POST'])
def add_season():
    data = request.get_json()

    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("INSERT INTO season (SeasonID, Year, DriversChampionID, ConstructorChampionID) VALUES (%s, %s, %s, %s)",
                       (data['seasonID'], data['year'], data['driversChampionID'], data['constructorsChampionID']))
        connection.commit()
        return jsonify({"message": "Season added successfully!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/api/season/<int:id>', methods=['PUT'])
def update_season(id):
    data = request.get_json()
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE season SET Year = %s, DriversChampionID = %s, ConstructorChampionID = %s WHERE SeasonID = %s",
            (data['year'], data['driversChampionID'], data['constructorsChampionID'], id))
        #cursor.fetchall()
        connection.commit()
        return jsonify({'message': 'Season updated successfully'}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()

@app.route('/api/season/<int:id>', methods=['DELETE'])
def delete_season(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM season WHERE SeasonID = %s", (id,))
        connection.commit()
        return jsonify({"message": "Season deleted successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/racetracks')
def racetracks():
    return render_template('racetracks.html')  # Assuming you have a template called racetracks.html

@app.route('/api/racetracks', methods=['GET'])
def get_racetracks():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM racetrack")
    racetracks = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify(racetracks), 200

@app.route('/api/racetracks/<int:id>', methods=['GET'])
def get_racetrack(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM racetrack WHERE racetrackID = %s", (id,))
    racetrack = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if racetrack:
        return jsonify(racetrack), 200
    else:
        return jsonify({"error": "Race track not found"}), 404

@app.route('/api/racetracks', methods=['POST'])
def add_racetrack():
    data = request.get_json()

    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute("""INSERT INTO racetrack (racetrackID, country, circuitLength, numberOfLaps, lapRecord, firstGrandPrix) VALUES (%s, %s, %s, %s, %s, %s)""",
            (data['racetrackID'], data['country'], data['circuitLength'], data['numberOfLaps'], data['lapRecord'], data['firstGrandPrix']))
        connection.commit()
        return jsonify({'message': 'Race track added successfully'}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/api/racetracks/<int:id>', methods=['PUT'])
def update_racetrack(id):
    data = request.get_json()
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor()
    try: 
        cursor.execute("UPDATE racetrack SET Country = %s, CircuitLength = %s, NumberOfLaps = %s, LapRecord = %s, FirstGrandPrix = %s WHERE RaceTrackID = %s",
            (data['country'], data['circuitLength'], data['numberOfLaps'], data['lapRecord'], data['firstGrandPrix'], id))
        connection.commit()
        return jsonify({'message': 'Race track updated successfully'}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/api/racetracks/<int:id>', methods=['DELETE'])
def delete_racetrack(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor()
    try:
        # Set the foreign key to NULL
        cursor.execute("UPDATE race SET RaceTrackID = NULL WHERE RaceTrackID = %s", (id,))
        connection.commit()

        # Delete the racetrack row
        cursor.execute("DELETE FROM racetrack WHERE racetrackID = %s", (id,))
        connection.commit()
        return jsonify({"message": "Race track deleted successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/teams')
def team():
    return render_template('team.html')  # Assuming you have a template called drivers.html

@app.route('/api/teams', methods=['GET'])
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

@app.route('/api/teams', methods=['POST'])
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

@app.route('/api/teams/<int:id>', methods=['PUT'])
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

@app.route('/api/teams/<int:id>', methods=['DELETE'])
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

@app.route('/api/teams/<int:id>', methods=['GET'])
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
    
@app.route('/drivers')
def drivers():
    return render_template('drivers.html')  # Assuming you have a template called drivers.html

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM driver")
    drivers_ = cursor.fetchall()
    cursor.close()
    close_connection(connection)
    return jsonify(drivers_), 200

@app.route('/api/drivers/<int:id>', methods=['GET'])
def get_driver(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM driver WHERE DriverID = %s", (id,))
    driver = cursor.fetchone()
    cursor.close()
    close_connection(connection)
    if driver:
        return jsonify(driver), 200
    else:
        return jsonify({"error": "Driver not found"}), 404

@app.route('/api/drivers', methods=['POST'])
def add_driver():
    data = request.get_json()

    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor()
    try:
        cursor.execute("""INSERT INTO driver (DriverID, TeamID, Country, Podiums, Points, GrandsPrixEntered, WorldChampionships, HighestRaceFinish, HighestGridPosition, DOB, POB, Name) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", 
        (data['driver_id'], data['team_id'], data['country'], data['podiums'], data['points'], data['grands_prix_entered'], data['world_championships'], data['highest_race_finish'], data['highest_grid_position'], data['dob'], data['pob'], data['name']))
        connection.commit()
        return jsonify({'message': 'Driver added successfully'}), 201
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

@app.route('/api/drivers/<int:id>', methods=['PUT'])
def update_driver(id):
    data = request.get_json()
    connection = create_connection()

    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500
    
    cursor = connection.cursor()

    print(data)
    try: 
        cursor.execute("""
            UPDATE driver 
            SET Name = %s, TeamID = %s, Country = %s, Podiums = %s, Points = %s, GrandsPrixEntered = %s, WorldChampionships = %s, HighestRaceFinish = %s, HighestGridPosition = %s, DOB = %s, POB = %s 
            WHERE DriverID = %s
        """, (data['name'], data['team_id'], data['country'], data['podiums'], data['points'], data['grands_prix_entered'], data['world_championships'], data['highest_race_finish'], data['highest_grid_position'], data['dob'], data['pob'], id))
        connection.commit()
        return jsonify({'message': 'Driver updated successfully'}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)


@app.route('/api/drivers/<int:id>', methods=['DELETE'])
def delete_driver(id):
    connection = create_connection()
    if connection is None:
        return jsonify({"error": "Failed to connect to the database"}), 500

    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM driver WHERE DriverID = %s", (id,))
        connection.commit()
        return jsonify({"message": "Driver deleted successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        close_connection(connection)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/teams')
def teams():
    return render_template('teams.html')  # Assuming you have a template called teams.html

@app.route('/races')
def races():
    return render_template('races.html')  # Assuming you have a template called races.html

@app.route('/constructors')
def constructors():
    return render_template('constructors.html')  # Assuming you have a template called constructors.html

@app.route('/results')
def results():
    return render_template('results.html')  # Assuming you have a template called results.html


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', threaded=True, debug=True)
