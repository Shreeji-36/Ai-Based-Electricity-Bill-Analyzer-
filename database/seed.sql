INSERT INTO industries VALUES
 ('pharmacy','Pharmacy',8.5),('dairy','Dairy',8.0),
 ('steel','Steel',7.2),('coldstorage','Cold Storage',8.2)
ON CONFLICT DO NOTHING;

INSERT INTO machines (industry_id, code, name, power_kw, efficiency) VALUES
 ('pharmacy','hvac','HVAC System',45,78),
 ('pharmacy','compressor','Air Compressor',37,72),
 ('pharmacy','fbd','Fluid Bed Dryer',22,81),
 ('pharmacy','tablet','Tablet Compression Machine',15,85),
 ('pharmacy','chiller','Chiller Plant',60,76),
 ('steel','eaf','Electric Arc Furnace',500,70),
 ('steel','rolling','Rolling Mill',250,75)
ON CONFLICT DO NOTHING;