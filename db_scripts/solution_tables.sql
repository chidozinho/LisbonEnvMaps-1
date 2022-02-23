SET search_path TO us;

/*
    The `env_variables` table records the variables
    temperature, humidity, noise, address of each sensor and the fraguesia where is located each sensor
    The index on date helps to speed up the query operations
*/

DROP TABLE IF EXISTS env_variables;
CREATE TABLE env_variables (
    id serial PRIMARY KEY,
    id_sensor varchar(4),
    date date,
    temp_value float(6),
    noise_value float(6),
    hum_value float(6),
    freguesia varchar(100),
    address varchar(100)
    
    CREATE INDEX ON us.env_variables(date)
    );
