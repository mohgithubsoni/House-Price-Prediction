import pandas as pd

# Data load karo
df = pd.read_csv('Bengaluru_House_Data.csv')

# Pehli 5 rows dekhne ke liye
print("--- Data ki Pehli 5 Rows ---")
print(df.head())

# Ye check karne ke liye ki kitne rows aur columns hain
print("\n--- Dataset Shape ---")
print(df.shape)

# 1. Ye check karo ki har column mein kis tarah ka data hai
print(df.info())

# 2. Ye check karo ki 'location' ya 'size' mein kitne gharon ka data missing hai
print(df.isnull().sum())


#Data Cleaning
# Step 1: Faaltu columns ko drop karo
# Axis=1 ka matlab hai hum "Columns" hata rahe hain
df2 = df.drop(['area_type', 'society', 'balcony', 'availability'], axis='columns')
print(df2.head())

# Step 2: Check karo ki ab kitni missing values bachi hain
print("--- Naye DataFrame mein Missing Values ---")
print(df2.isnull().sum())

# Step 3: Jo thodi bahut missing values hain (jaise bath mein 73), unhe hata do
df3 = df2.dropna()
print("\n--- Cleaning ke baad Final Shape ---")
print(df3.shape)

#checking null values
print(df3.isnull().sum())


#Now changing total sq in numbef
def is_float(x):
    try:
        float(x)
    except:
        return False
    return True

# Ab wo rows dekhte hain jahan total_sqft number NAHI hai (~ symbol ka matlab hai 'NOT')
print(df3[~df3['total_sqft'].apply(is_float)].head(10))

def convert_sqft_to_num(x):
    tokens = x.split('-')
    if len(tokens) == 2:
        # Agar range hai (e.g. 2100 - 2850), toh average lo
        return (float(tokens[0]) + float(tokens[1])) / 2
    try:
        # Agar simple number hai, toh float mein badlo
        return float(x)
    except:
        # Agar 'Sq. Meter' jaisa kuch hai, toh None return karo
        return None

# Ab is function ko column par apply karte hain
df4 = df3.copy()
df4['total_sqft'] = df4['total_sqft'].apply(convert_sqft_to_num)

# Jo 'None' (Units wale) the, unhe hata dete hain
df4 = df4.dropna()

# Check karte hain ki kya ab 'total_sqft' number ban gaya?
print(df4.head())
print("\n--- 'total_sqft' ka type check ---")
print(df4['total_sqft'].dtype)

# Hum ek naya column banayenge 'bhk'
# x.split(' ') karne se '2 BHK' ban jayega ['2', 'BHK']
# Phir hum [0] se '2' uthayenge aur use int() mein badal denge
df5 = df4.copy()
df5['bhk'] = df5['size'].apply(lambda x: int(x.split(' ')[0]))

# Ab hum 'size' column ko drop kar sakte hain kyunki uska kaam khatam ho gaya
df5 = df5.drop('size', axis='columns')

print(df5.head())

#now next step is finfing outliers
# Price lakh mein hai, toh pehle use 100,000 se multiply karenge
# Phir use total_sqft se divide kar denge
df5['price_per_sqft'] = (df5['price'] * 100000) / df5['total_sqft']

print("\n--- Price Per Sqft ke saath Data ---")
print(df5.head())

print(len(df5.location.unique()))

# Har location kitni baar repeat hui hai?
location_stats = df5.groupby('location')['location'].agg('count').sort_values(ascending=False)
print(location_stats)

# Dekhte hain kitni locations aisi hain jinke 10 se kam records hain
print(f"\nTotal Locations: {len(location_stats)}")
print(f"Locations with <= 10 data points: {len(location_stats[location_stats <= 10])}")

#ab hm 10 se kmm wali location ka nam change krke other krdenge taaki hmara coulms kmm ho jae
# 1. Pehle count nikalte hain har location ka
location_stats = df5.groupby('location')['location'].agg('count')

# 2. Wo locations dhoondte hain jinme 10 se kam records hain
locations_less_than_10 = location_stats[location_stats <= 10]

# 3. Ab ek function jo har row ko check karega
def handle_location(x):
    if x in locations_less_than_10:
        return 'other'
    else:
        return x

# 4. Is function ko 'location' column par apply kar do
df5['location'] = df5['location'].apply(handle_location)

#to check total number of locations
print(len(df5.location.unique()))

#Phase 3: Outlier Removal (Galtiyan Saaf Karna)
#Real estate mein ek thumb rule hota hai ki ek bedroom (BHK) ke liye kam se kam 300 sqft jagah honi chahiye.
# total_sqft ko bhk se divide karke dekhte hain ki per room kitni jagah hai
# Agar wo 300 se kam hai, toh wo outliers hain
print(df5[df5.total_sqft / df5.bhk < 300].head())

# Hum sirf wahi data rakhenge jahan sqft per bhk >= 300 hai
df6 = df5[~(df5.total_sqft / df5.bhk < 300)]

print("Original Shape:", df5.shape)
print("New Shape after removing outliers:", df6.shape)

#to check new outlier
#it will remove those entry which have diffrent price range in the same area by comparing ith mean price
import numpy as np

def remove_pps_outliers(df):
    df_out = pd.DataFrame()
    for key, subdf in df.groupby('location'):
        m = np.mean(subdf.price_per_sqft) # Average price
        st = np.std(subdf.price_per_sqft) # Standard deviation
        # Hum sirf wahi data rakhenge jo (Mean - 1*ST) aur (Mean + 1*ST) ke beech hai
        reduced_df = subdf[(subdf.price_per_sqft > (m-st)) & (subdf.price_per_sqft <= (m+st))]
        df_out = pd.concat([df_out, reduced_df], ignore_index=True)
    return df_out

df7 = remove_pps_outliers(df6)
print("Shape after Price Outlier Removal:", df7.shape)

#now removing bathroom outliers
# Pehle dekhte hain aise kaunse ghar hain jahan bathrooms bohot zyada hain
print("Ghar jahan bathrooms BHK se 2 zyada hain:")
print(df7[df7.bath > df7.bhk + 2])

# Ab sirf wahi data rakhte hain jo rule follow karta hai
df8 = df7[df7.bath < df7.bhk + 2]

print("\nFinal Shape after all cleaning:", df8.shape)


#Next Phase: Model Building (The AI Part)
#Phase 4: Model Building (One-Hot Encoding)
# Problem: Text vs Numbers
# Hamare data mein location abhi bhi text (String) hai, jaise 'Whitefield', 'Hebbal', etc. Computer is text par maths nahi kar sakta. Hume ise numbers mein badalna hoga.
print(df8.head())

# 1. Location ke liye dummies banayein
dummies = pd.get_dummies(df8.location)

# 2. In dummies ko original data (df8) ke saath jod dein
# Hum 'other' column ko drop kar dete hain (standard ML practice to avoid dummy variable trap)
df9 = pd.concat([df8, dummies.drop('other', axis='columns')], axis='columns')

# 3. Ab purani 'location' column ki zaroorat nahi hai, use hata dein
df10 = df9.drop('location', axis='columns')

# 4. 'price_per_sqft' sirf outliers hatane ke liye tha, model building mein iski zaroorat nahi
df10 = df10.drop('price_per_sqft', axis='columns')

print(df10.head())

# now real part converting into x nd y x includes every colum except price and y inclued price

# X mein saara data hoga bas 'price' ko chhod kar
X = df10.drop('price', axis='columns')

# y mein sirf 'price' hoga
y = df10.price

print("--- X ki shape (Features) ---")
print(X.shape)
print("\n--- y ki pehli 5 values (Target) ---")
print(y.head())

#Phase 5: Train-Test Split & Linear Regression

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

# 1. Data ko Train aur Test mein baantein
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=10)

# 2. Linear Regression model banayein
lr_clf = LinearRegression()

# 3. Model ko train karein (Isse hi training kehte hain!)
lr_clf.fit(X_train, y_train)

# 4. Ab check karte hain model ka score (Accuracy)
score = lr_clf.score(X_test, y_test)
print(f"Model ki accuracy score hai: {score}")

#now function to test the model
def predict_price(location, sqft, bath, bhk):    
    try:
        loc_index = np.where(X.columns == location)[0][0]
    except:
        loc_index = -1 # Agar location nahi mili

    x_input = np.zeros(len(X.columns))
    x_input[0] = sqft
    x_input[1] = bath
    x_input[2] = bhk
    
    if loc_index >= 0:
        x_input[loc_index] = 1

    return lr_clf.predict([x_input])[0]

# 1. 1st Phase JP Nagar mein 1000 sqft, 2 Bath, 2 BHK ka price?
print("JP Nagar 2BHK Price:", predict_price('1st Phase JP Nagar', 1000, 2, 2), "Lakhs")

# 2. Indira Nagar mein 1000 sqft, 2 Bath, 2 BHK ka price?
print("Indira Nagar 2BHK Price:", predict_price('Indiranagar', 1000, 2, 2), "Lakhs")

# Saving trained model

import pickle

# 1. Model ko save karo 'bangalore_home_prices_model.pickle' naam ki file mein
with open('bangalore_home_prices_model.pickle', 'wb') as f:
    pickle.dump(lr_clf, f)

# 2. Columns ki list ko bhi save karna zaroori hai (JSON format mein)
import json
columns = {
    'data_columns' : [col.lower() for col in X.columns]
}
with open("columns.json", "w") as f:
    f.write(json.dumps(columns))

print("Mubarak ho! Model aur Columns save ho gaye hain.")