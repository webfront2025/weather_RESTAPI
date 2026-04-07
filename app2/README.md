# Weather REST API

## Projekt
API for vejr- og miljødata fra DMI og egne instrumenter.  
Alle endpoints returnerer JSON.

Dette projekt bruger database fra:
https://github.com/NervousPapaya/Specialisterne-Case---ETL-Pipeline

---

## Installation

### 1. Klon ETL-pipeline (database)

`git clone https://github.com/NervousPapaya/Specialisterne-Case---ETL-Pipeline.git`
cd Specialisterne-Case---ETL-Pipeline

### 2. Start database (Docker)
`docker-compose up` 
`docker-compose up`

### 3. Gå til API projekt
cd Weather_RestAPI/weather-api
`uvicorn app2.main:app --reload`

### 4. Installer dependencies
`pip install -r requirements.txt`

### 5. Swagger:
`http://127.0.0.1:8000/docs`


## Tips
- PostgreSQL tabelnavne er case-sensitive. Brug korrekt navn (fx `DMI` ikke `dmi`)
- `/filter` og `/compare` fungerer.

## Frontend
- `app2/frontend/index.html` – Dropdown, datotjek, table visning
- Åbn i browser eller servér lokalt



### Kør projektet

* Terminal 1 – Backend (API, FastAPI)
  python -m uvicorn app2.main:app --reload

* API kører her:

  http://127.0.0.1:8000

* Swagger dokumentation:

  http://127.0.0.1:8000/docs

* Terminal 2 – Frontend (HTML Server)
  cd app2/frontend
  python -m http.server 5500

* Frontend:

 http://localhost:5500



## Endpoints
- `/` – Root
- `/test-db` – Test DB
- `/tables` – Liste over tabeller
- `/columns/{table_name}` – Kolonner
- `/data/{table_name}?limit=` – Hent data
- `/stations` – Liste over stationer
- `/stations/{station}?from_date=&to_date=` – Station data
- `/latest` – Seneste pr. station
- `/latest/{table_name}` – Seneste måling
- `/filter/{table_name}?from_date=&to_date=` – Filtreret data
- `/compare?stations=DMI,BME280` – Sammenlign stationer
