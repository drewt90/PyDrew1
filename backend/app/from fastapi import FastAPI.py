from fastapi import FastAPI

app = FastAPI(title="PyprCM Case Management API")


@app.get("/")
def health_check():
  return {"status": "online", "system": "PyprCM"}


# Temporary in-memory list to test your first client endpoint
clients_db = []


@app.post("/clients")
def create_client(full_name: str, case_number: str):
  client = {
      "id": len(clients_db) + 1,
      "full_name": full_name,
      "case_number": case_number,
  }
  clients_db.append(client)
  return client


@app.get("/clients")
def list_clients():
  return clients_dbfrom fastapi import FastAPI

app = FastAPI(title="PyprCM Case Management API")


@app.get("/")
def health_check():
  return {"status": "online", "system": "PyprCM"}


# Temporary in-memory list to test your first client endpoint
clients_db = []


@app.post("/clients")
def create_client(full_name: str, case_number: str):
  client = {
      "id": len(clients_db) + 1,
      "full_name": full_name,
      "case_number": case_number,
  }
  clients_db.append(client)
  return client


@app.get("/clients")
def list_clients():
  return clients_db