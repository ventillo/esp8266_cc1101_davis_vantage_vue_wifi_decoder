#Structure of InfluxDB
InfluxDB was chosen for it's simplicity and ease of management, live with it.

##influxDB SCHEMA:
Firs off, 2 databases:
    weather
    status

###DB weather
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



###DB status

    iss measure
    ----------------
      voltage | solar or capacitor | state / lqi /  | battery or future_shit |
      ----------------------------------------------------------------
      field     tag                  field   tag

    RasPI system
    ----------------
      usage | disk, mem, cpu, eth, wifi %
      ------------------------------------
      field | tag
