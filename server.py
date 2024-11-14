from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)


# Настройка подключения к базе данных
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='php2023_egorius',
        database='competition'
    )


@app.route('/nearby_companies', methods=['GET'])
def nearby_companies():
    user_lat = float(request.args.get('lat'))
    user_lon = float(request.args.get('lon'))

    query = """
        SELECT id, Company_name, x_coordinate, y_coordinate, advertising, 
        (6371 * ACOS(COS(RADIANS(%s)) * COS(RADIANS(x_coordinate)) * 
        COS(RADIANS(y_coordinate) - RADIANS(%s)) + 
        SIN(RADIANS(%s)) * SIN(RADIANS(x_coordinate)))) AS distance
        FROM companies
        HAVING distance <= 1
        ORDER BY distance;
    """

    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, (user_lat, user_lon, user_lat))
        results = cursor.fetchall()
        return jsonify(results)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
