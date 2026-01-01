from fastapi import FastAPI
from pydantic import BaseModel
import pickle
import json
import numpy as np

# 1. FastAPI ka object banayein
app = FastAPI()

# 2. Model aur Columns ko load karne wala function
model = None
data_columns = None

def load_saved_artifacts():
    global model
    global data_columns
    
    # Pickle file load karo (Model ka dimaag)
    with open("bangalore_home_prices_model.pickle", "rb") as f:
        model = pickle.load(f)
    
    # JSON file load karo (Columns ki list)
    with open("columns.json", "r") as f:
        data_columns = json.loads(f.read())['data_columns']

# Server start hote hi artifacts load ho jayenge
load_saved_artifacts()

# 3. User se aane wale data ka structure (Schema)
class HouseData(BaseModel):
    location: str
    sqft: float
    bhk: int
    bath: int

# 4. Prediction ka Main Endpoint (URL)
@app.post("/predict_home_price")
def predict_home_price(data: HouseData):
    try:
        # Location ka index dhundo
        loc_index = data_columns.index(data.location.lower())
    except:
        loc_index = -1

    # Khali array banao
    x = np.zeros(len(data_columns))
    x[0] = data.sqft
    x[1] = data.bath
    x[2] = data.bhk
    
    # Agar location mil gayi toh use 1 set karo
    if loc_index >= 0:
        x[loc_index] = 1

    # Prediction nikalo
    prediction = model.predict([x])[0]
    
    return {"estimated_price": round(prediction, 2)}

# 5. Home route (Check karne ke liye ki server chal raha hai)
@app.get("/")
def home():
    return {"message": "Bangalore House Price API is Running!"}