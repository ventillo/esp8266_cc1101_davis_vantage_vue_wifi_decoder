# Structure of InfluxDB
InfluxDB was chosen for it's simplicity and ease of management, live with it.

## influxDB SCHEMA:
Firs off, 2 databases:

    weather
    status

### DB weather

    measure wind
    ----------------
      value  | speed or direction or windgust | davis_id
      ---------------------------------------------------
      field    tag                              tag

    measure temphumi
    ----------------
      temperature | humidity | external, internal | davis_id
      ---------------------------------------------------------
      field         field      tag                  tag

    measure rain
    ----------------
      rain | rate / total / intensity | davis_id
      ---------------------------------------------
      field  tag                        tag



### DB status

    iss measure
    ----------------
      voltage | solar or capacitor
      ----------------------------------------------------------------
      field     tag

    RasPI system (only on the raspi system)
    ----------------
      usage | disk, mem, cpu, eth, wifi %
      ------------------------------------
      field | tag

## Retention policies
    -------
    weather
    -------
    create retention policy realtime on weather duration 168h replication 1 shard duration 1h
    create retention policy monthly on weather duration 720h replication 1 shard duration 24h
    create retention policy yearly on weather duration 8760h replication 1 shard duration 168h
    create retention policy infinite on weather duration 0s replication 1 shard duration 720h
    alter retention policy realtime on weather default

    ------
    status
    ------
    create retention policy realtime on status duration 168h replication 1 shard duration 1h
    create retention policy monthly on status duration 720h replication 1 shard duration 24h
    create retention policy yearly on status duration 8760h replication 1 shard duration 168h
    create retention policy infinite on status duration 0s replication 1 shard duration 720h
    alter retention policy realtime on status default

## Continuous queries
    -------------------------------------------------------------------------------
    WIND
    -------------------------------------------------------------------------------
    CREATE CONTINUOUS QUERY "cq_wind_10m" ON "weather" BEGIN
        SELECT max(value) AS wind_max, mean(value) AS wind, min(value) AS wind_min
        INTO "monthly"."wind_aggregated"
        FROM realtime.wind
        GROUP BY time(10m), type, davis_id
    END
    CREATE CONTINUOUS QUERY "cq_wind_1h" ON "weather" BEGIN
        SELECT max(value) AS wind_max, mean(value) AS wind, min(value) AS wind_min
        INTO "yearly"."wind_aggregated"
        FROM realtime.wind
        GROUP BY time(1h), type, davis_id
    END
    CREATE CONTINUOUS QUERY "cq_wind_6h" ON "weather" BEGIN
        SELECT max(value) AS wind_max, mean(value) AS wind, min(value) AS wind_min
        INTO "infinite"."wind_aggregated"
        FROM realtime.wind
        GROUP BY time(6h), type, davis_id
    END

    -------------------------------------------------------------------------------
    RAIN
    -------------------------------------------------------------------------------
    CREATE CONTINUOUS QUERY "cq_rain_10m" ON "weather" BEGIN
        SELECT max("value") AS val_max, mean(value) AS value
        INTO "monthly"."rainrate_aggregated"
        FROM realtime.rain
        GROUP BY type,time(10m), davis_id
    END
    CREATE CONTINUOUS QUERY "cq_rain_1h" ON "weather" BEGIN
        SELECT max("value") AS val_max, mean(value) AS value
        INTO "yearly"."rainrate_aggregated"
        FROM realtime.rain
        GROUP BY type,time(1h), davis_id
    END
    CREATE CONTINUOUS QUERY "cq_rain_6h" ON "weather" BEGIN
        SELECT max("value") AS val_max, mean(value) AS value
        INTO "infinite"."rainrate_aggregated"
        FROM realtime.rain
        GROUP BY type,time(6h), davis_id
    END
    -------------------------------------------------------------------------------
    TEMPHUMI
    -------------------------------------------------------------------------------
    CREATE CONTINUOUS QUERY "cq_temphumi_10m" ON "weather" BEGIN
        SELECT
            max("humidity") AS humidity_max,
            min("humidity") AS humidity_min,
            mean("humidity") AS humidity,
            max("temperature") AS temperature_max,
            min("temperature") AS temperature_min,
            mean("temperature") AS temperature
        INTO "monthly"."temphumi_aggregated"
        FROM realtime.temphumi
        GROUP BY type, time(10m), davis_id
    END

    CREATE CONTINUOUS QUERY "cq_temphumi_1h" ON "weather" BEGIN
        SELECT
            max("humidity") AS humidity_max,
            min("humidity") AS humidity_min,
            mean("humidity") AS humidity,
            max("temperature") AS temperature_max,
            min("temperature") AS temperature_min,
            mean("temperature") AS temperature
        INTO "yearly"."temphumi_aggregated"
        FROM realtime.temphumi
        GROUP BY type, time(1h), davis_id
    END

    CREATE CONTINUOUS QUERY "cq_temphumi_6h" ON "weather" BEGIN
        SELECT
            max("humidity") AS humidity_max,
            min("humidity") AS humidity_min,
            mean("humidity") AS humidity,
            max("temperature") AS temperature_max,
            min("temperature") AS temperature_min,
            mean("temperature") AS temperature
        INTO "infinite"."temphumi_aggregated"
        FROM realtime.temphumi
        GROUP BY type, time(6h), davis_id
    END

    -------------------------------------------------------------------------------
    TRAFFIC
    -------------------------------------------------------------------------------
    CREATE CONTINUOUS QUERY "cq_net_1m" ON "status" BEGIN
        SELECT NON_NEGATIVE_DERIVATIVE(max(*)) as traffic
        INTO "monthly"."net_aggregated"
        FROM realtime.net
        WHERE time > now()-1m
        GROUP BY time(30s)
    END
