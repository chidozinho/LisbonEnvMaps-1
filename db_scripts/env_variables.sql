/*
    The purpose of the trigger is to insert into the env_variables table rides every time a new record is inserted
    in originaldata table. Also, using postgis spatial function of intersection the env_variables table gets the address of the sensor and the fraguesia's name.
*/
CREATE FUNCTION ods.insert_data()
RETURNS TRIGGER AS
$$
BEGIN
	INSERT INTO us.env_variables(id_sensor, temp_value, noise_value, date, hum_value, freguesia, address)
	VALUES (new.id_sensor, 
			new.temp_value, 
            new.noise_value, 
			new.date, 
			new.hum_value,
                      
            (select f."NOME" from ods.fraguesias f, ods.sensors_points sp
            where ST_Intersects(f.geometry, sp.geometry) and sp.id_sensor=new.id_sensor),
            (select sp.address from ods.sensors_points sp
            where sp.id_sensor=new.id_sensor)
           );
	RETURN new;
END;
$$
LANGUAGE 'plpgsql';

CREATE TRIGGER insert_data
AFTER INSERT ON ods.originaldata
FOR EACH ROW
EXECUTE PROCEDURE ods.insert_data();
