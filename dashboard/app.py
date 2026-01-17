import os
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta


app = Flask(__name__)
CORS(app)

DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/latest')
def get_latest():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, timestamp, temperature, humidity, pressure,
                   wind_speed, wind_direction, weather_condition
            FROM weather_data
            ORDER BY timestamp DESC
            LIMIT 1
        """)

        data = cur.fetchone()
        cur.close()
        conn.close()

        if data:
            result = dict(data)
            result['timestamp'] = result['timestamp'].isoformat()
            result['temperature'] = float(result['temperature'])
            result['humidity'] = float(result['humidity'])
            result['pressure'] = float(result['pressure'])
            result['wind_speed'] = float(result['wind_speed'])
            return jsonify(result)
        else:
            return jsonify({'error': 'No data available'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/history')
def get_history():
    hours = int(request.args.get('hours', 24))

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT timestamp, temperature, humidity, pressure,
                   wind_speed, weather_condition
            FROM weather_data
            WHERE timestamp > NOW() - INTERVAL '%s hours'
            ORDER BY timestamp ASC
        """, (hours,))

        data = cur.fetchall()
        cur.close()
        conn.close()

        result = []
        for row in data:
            item = dict(row)
            item['timestamp'] = item['timestamp'].isoformat()
            item['temperature'] = float(item['temperature'])
            item['humidity'] = float(item['humidity'])
            item['pressure'] = float(item['pressure'])
            item['wind_speed'] = float(item['wind_speed'])
            result.append(item)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats')
def get_stats():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            SELECT
                AVG(temperature) as avg_temp,
                MIN(temperature) as min_temp,
                MAX(temperature) as max_temp,
                AVG(humidity) as avg_humidity,
                MIN(humidity) as min_humidity,
                MAX(humidity) as max_humidity,
                AVG(pressure) as avg_pressure,
                MIN(pressure) as min_pressure,
                MAX(pressure) as max_pressure,
                AVG(wind_speed) as avg_wind_speed,
                MAX(wind_speed) as max_wind_speed
            FROM weather_data
            WHERE timestamp > NOW() - INTERVAL '24 hours'
        """)

        data = cur.fetchone()
        cur.close()
        conn.close()

        if data:
            result = {
                'temperature': {
                    'avg': float(data['avg_temp']) if data['avg_temp'] else 0,
                    'min': float(data['min_temp']) if data['min_temp'] else 0,
                    'max': float(data['max_temp']) if data['max_temp'] else 0
                },
                'humidity': {
                    'avg': float(data['avg_humidity']) if data['avg_humidity'] else 0,
                    'min': float(data['min_humidity']) if data['min_humidity'] else 0,
                    'max': float(data['max_humidity']) if data['max_humidity'] else 0
                },
                'pressure': {
                    'avg': float(data['avg_pressure']) if data['avg_pressure'] else 0,
                    'min': float(data['min_pressure']) if data['min_pressure'] else 0,
                    'max': float(data['max_pressure']) if data['max_pressure'] else 0
                },
                'wind_speed': {
                    'avg': float(data['avg_wind_speed']) if data['avg_wind_speed'] else 0,
                    'max': float(data['max_wind_speed']) if data['max_wind_speed'] else 0
                }
            }
            return jsonify(result)
        else:
            return jsonify({'error': 'No data available'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
