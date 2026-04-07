#from fastapi import FastAPI
#from app2.database import get_connection

#app = FastAPI()

 
#def root():
#   return {"message": "API is running "}

#connect to database , can see :{"result":[1]}    in:  http://127.0.0.1:8000/testDb
"""
@app.get("/testDb")
def testDb():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1;")
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return {"result": result}
"""
"""

# Find tales name  in Database

@app.get("/tables")
def get_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
     
        #SELECT table_name
        #FROM information_schema.tables
        #WHERE table_schema='public'
    
    #""")

    #tables = cursor.fetchall()

    #cursor.close()
    #conn.close()

    #return {"tables": tables}
   #"""
   
# in browser can see :
#   {"tables":[["DMI"],["BME280"],["DS18B20"],["SCD41"],["humidity_data"],["pressure_data"],["temperature_data"]]}
   
   
# First EndPoint : temperature_data

    #   /columns/temperature   
"""   
@app.get("/columns/temperature")
def get_columns():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        #SELECT column_name
        #FROM information_schema.columns
        #WHERE table_name = 'temperature_data'
 #   """)
"""
    columns = [col[0] for col in cursor.fetchall()]

    cursor.close()
    conn.close()

    return {"columns": columns}
#in http://127.0.0.1:8000/columns/temperature
#               can see temperature_data columns name : 
#{"columns":["temperature","observed_at","pulled_at","source","location"]}
#---------------------
"""

#   ------------------    Clean Code    ------------------
from fastapi import FastAPI, Query, HTTPException, Depends
from app2.database import get_connection, get_all_tables, get_columns
from fastapi.middleware.cors import CORSMiddleware

#app = FastAPI()
app = FastAPI(title="Weather REST API")


# Optional API key
API_KEY = "12345"
def verify_api_key(x_api_key: str = Query(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Allow frontend calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)




def normalize_table_name(input_name):
    tables = get_all_tables()
    for t in tables:
        if t.lower() == input_name.lower():
            return t
    return None


#  Root endpoint
@app.get("/")
def root():
    return {"message": "Weather API is running "}


#  Test DB connection
@app.get("/test-db")
def test_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1;")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return {"result": result}


#  Get all tables
@app.get("/tables")
def tables():
    return {"tables": get_all_tables()}


#  Get columns of a table
@app.get("/columns/{table_name}")
def columns(table_name: str):
    
    #       in PostgreSQL   => "DMI"  != "dmi"
    #       Then use => normalize_table_name() 
    real_name = normalize_table_name(table_name)
    if not real_name:
        return {"error": "Invalid table name"}

    return {"columns": get_columns(real_name)}


#  Get data from any table (clean JSON)
@app.get("/data/{table_name}")
def get_data(
    table_name: str,
    limit: int = Query(10, le=100)
):
    # Normalize table name (case insensitive)
    real_name = normalize_table_name(table_name)
    if not real_name:
        return {"error": "Invalid table name"}

    conn = get_connection()
    cursor = conn.cursor()

    columns = get_columns(real_name)

    # Use quotes for PostgreSQL table name
    cursor.execute(f'SELECT * FROM "{real_name}" LIMIT %s;', (limit,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    # Convert to clean JSON
    data = []
    for row in rows:
        item = {columns[i]: row[i] for i in range(len(columns))}
        data.append(item)

    return {
        "table": real_name,
        "count": len(data),
        "data": data
    }
    ####            ----------   Stations  ------------------
#@app.get("/stations", dependencies=[Depends(verify_api_key)])
@app.get("/stations")
def get_stations():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT source FROM temperature_data WHERE source IS NOT NULL
    """)

    stations = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()

    return {"stations": stations}
####            ---------Station  ?  Filter  -----------
from fastapi import HTTPException
@app.get("/stations/{station}")
#@app.get("/stations/{station}", dependencies=[Depends(verify_api_key)])
def get_station_data(
    station: str,
    from_date: str = Query(None),
    to_date: str = Query(None)
):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM temperature_data
        WHERE source = %s
    """
    params = [station]

    if from_date:
        query += " AND observed_at >= %s"
        params.append(from_date)

    if to_date:
        query += " AND observed_at <= %s"
        params.append(to_date)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    if not rows:
        raise HTTPException(status_code=404, detail="No data found")

    return {"station": station, "data": rows}
    
    
    ####            ----------   Latest   ---------------
    ####            ----------   Latest for all Stations  ---------------
@app.get("/latest")
def get_latest_all():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT DISTINCT ON (source) *
        FROM temperature_data
        ORDER BY source, observed_at DESC
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {"latest": rows}

    #                   ------     latest measurement    -----
@app.get("/latest/{table_name}")
def get_latest(table_name: str):
    real_name = normalize_table_name(table_name)

    if not real_name:
        return {"error": "Invalid table name"}

    conn = get_connection()
    cursor = conn.cursor()

    columns = get_columns(real_name)

    cursor.execute(f"""
        SELECT * FROM "{real_name}"
        ORDER BY observed_at DESC
        LIMIT 1;
    """)

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return {"data": None}

    data = {columns[i]: row[i] for i in range(len(columns))}

    return {"table": real_name, "latest": data}


#               -----------Query Params with Filtering  ------------

@app.get("/filter/{table_name}")
def filter_data(
    table_name: str,
    from_date: str = Query(None),
    to_date: str = Query(None)
):
    real_name = normalize_table_name(table_name)

    if not real_name:
        return {"error": "Invalid table name"}

    conn = get_connection()
    cursor = conn.cursor()

    columns = get_columns(real_name)

    # 
    query = f'SELECT * FROM "{real_name}" WHERE 1=1'
    params = []

    if from_date:
        query += " AND observed_at >= %s"
        params.append(from_date)

    if to_date:
        query += " AND observed_at <= %s"
        params.append(to_date)

    query += " LIMIT 50"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    data = []
    for row in rows:
        item = {columns[i]: row[i] for i in range(len(columns))}
        data.append(item)

    return {"table": real_name, "data": data}

######              ---------  Compare   -----------
@app.get("/compare")
# @app.get("/compare", dependencies=[Depends(verify_api_key)])
def compare(stations: str = Query(...)):
    station_list = stations.split(",")

    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM temperature_data
        WHERE source = ANY(%s)
    """

    cursor.execute(query, (station_list,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return {"data": rows}