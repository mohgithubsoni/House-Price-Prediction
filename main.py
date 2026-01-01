from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Permission dene ke liye
from pydantic import BaseModel
import pickle
import json
import numpy as np

app = FastAPI()

# --- CORS SETUP ---
# Isse hamari website ko server se baat karne ki permission milegi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Sabhi sites ko allow kar rahe hain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = None
data_columns = None

def load_saved_artifacts():
    global model
    global data_columns
    with open("bangalore_home_prices_model.pickle", "rb") as f:
        model = pickle.load(f)
    with open("columns.json", "r") as f:
        data_columns = json.loads(f.read())['data_columns']

load_saved_artifacts()

class HouseData(BaseModel):
    location: str
    total_sqft: float # Make sure ye naam app.js se match kare
    bhk: int
    bath: int

# --- NEW ENDPOINT: Locations ki list dene ke liye ---
@app.get("/get_location_names")
def get_location_names():
    # Hum pehle 3 columns (sqft, bath, bhk) ko chhod kar baki sab locations bhej rahe hain
    locations = data_columns[3:]
    return {"locations": locations}

@app.post("/predict_home_price")
def predict_home_price(data: HouseData):
    try:
        loc_index = data_columns.index(data.location.lower())
    except:
        loc_index = -1

    x = np.zeros(len(data_columns))
    x[0] = data.total_sqft
    x[1] = data.bath
    x[2] = data.bhk
    
    if loc_index >= 0:
        x[loc_index] = 1

    prediction = model.predict([x])[0]
    return {"estimated_price": round(prediction, 2)}

@app.get("/")
def home():
    return {"message": "API is Live!"}