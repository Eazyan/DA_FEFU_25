CREATE TABLE IF NOT EXISTS weather_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    temperature DECIMAL(5,2) NOT NULL CHECK (temperature >= -50 AND temperature <= 50),
    humidity DECIMAL(5,2) NOT NULL CHECK (humidity >= 0 AND humidity <= 100),
    pressure DECIMAL(6,2) NOT NULL CHECK (pressure >= 950 AND pressure <= 1050),
    wind_speed DECIMAL(5,2) NOT NULL CHECK (wind_speed >= 0 AND wind_speed <= 50),
    wind_direction INTEGER NOT NULL CHECK (wind_direction >= 0 AND wind_direction <= 360),
    weather_condition VARCHAR(50) NOT NULL CHECK (weather_condition IN ('sunny', 'cloudy', 'partly_cloudy', 'rainy', 'snowy', 'foggy'))
);

CREATE INDEX idx_weather_timestamp ON weather_data(timestamp DESC);
CREATE INDEX idx_weather_condition ON weather_data(weather_condition);
