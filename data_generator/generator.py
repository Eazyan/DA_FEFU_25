import os
import time
import random
import math
from datetime import datetime
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor


class WeatherDataGenerator:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.interval = int(os.getenv('GENERATION_INTERVAL', '5'))
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.previous_pressure = 1013.25

    def connect_to_database(self, max_retries=10, retry_delay=5):
        for attempt in range(max_retries):
            try:
                self.conn = psycopg2.connect(self.database_url)
                print(f"Successfully connected to database")
                return True
            except psycopg2.OperationalError as e:
                print(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print("Failed to connect to database after maximum retries")
                    return False
        return False

    def generate_temperature(self) -> float:
        hour = datetime.now().hour
        base_temp = 15 + 10 * math.sin(2 * math.pi * (hour - 6) / 24)
        variation = random.uniform(-3, 3)
        temperature = base_temp + variation
        return round(max(-50, min(50, temperature)), 2)

    def generate_humidity(self, temperature: float) -> float:
        base_humidity = 80 - (temperature * 1.5)
        variation = random.uniform(-10, 10)
        humidity = base_humidity + variation
        return round(max(0, min(100, humidity)), 2)

    def generate_pressure(self) -> float:
        change = random.uniform(-2, 2)
        self.previous_pressure += change
        self.previous_pressure = max(950, min(1050, self.previous_pressure))
        return round(self.previous_pressure, 2)

    def generate_wind_speed(self) -> float:
        speed = abs(random.gauss(10, 5))
        return round(max(0, min(50, speed)), 2)

    def generate_wind_direction(self) -> int:
        return random.randint(0, 360)

    def determine_weather_condition(self, temperature: float, humidity: float) -> str:
        if humidity > 80 and temperature < 5:
            return 'snowy'
        elif humidity > 70:
            return 'rainy'
        elif humidity < 40:
            return 'sunny'
        elif humidity < 60:
            return random.choice(['sunny', 'partly_cloudy'])
        else:
            return random.choice(['cloudy', 'partly_cloudy'])

    def generate_weather_data(self) -> dict:
        temperature = self.generate_temperature()
        humidity = self.generate_humidity(temperature)
        pressure = self.generate_pressure()
        wind_speed = self.generate_wind_speed()
        wind_direction = self.generate_wind_direction()
        weather_condition = self.determine_weather_condition(temperature, humidity)

        return {
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure,
            'wind_speed': wind_speed,
            'wind_direction': wind_direction,
            'weather_condition': weather_condition
        }

    def insert_data(self, data: dict) -> bool:
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO weather_data
                    (temperature, humidity, pressure, wind_speed, wind_direction, weather_condition)
                    VALUES (%(temperature)s, %(humidity)s, %(pressure)s, %(wind_speed)s, %(wind_direction)s, %(weather_condition)s)
                """, data)
                self.conn.commit()
                return True
        except Exception as e:
            print(f"Error inserting data: {e}")
            self.conn.rollback()
            return False

    def run(self):
        print("Weather Data Generator starting...")
        print(f"Generation interval: {self.interval} seconds")

        if not self.connect_to_database():
            return

        print("Starting data generation...")

        try:
            while True:
                data = self.generate_weather_data()

                if self.insert_data(data):
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"[{timestamp}] Generated: {data['temperature']}°C, {data['humidity']}%, "
                          f"{data['pressure']} hPa, {data['wind_speed']} m/s, {data['weather_condition']}")
                else:
                    print("Failed to insert data, attempting to reconnect...")
                    if not self.connect_to_database():
                        break

                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nStopping data generation...")
        finally:
            if self.conn:
                self.conn.close()
                print("Database connection closed")


if __name__ == '__main__':
    generator = WeatherDataGenerator()
    generator.run()
