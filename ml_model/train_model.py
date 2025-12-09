import pandas as pd, random, joblib
from pathlib import Path
OUT = Path(__file__).parent / "data"
OUT.mkdir(parents=True, exist_ok=True)
csv_path = OUT / "synthetic_data.csv"
headers = ["Hemoglobin","WBC","Platelets","Creatinine","SGPT","SGOT","Bilirubin","Label"]

def gen_row(normal=True):
    if normal:
        return [round(random.uniform(13,15),1), int(random.uniform(4500,8000)), int(random.uniform(200000,350000)), round(random.uniform(0.7,1.1),2), int(random.uniform(15,35)), int(random.uniform(15,35)), round(random.uniform(0.3,0.9),1), "Normal"]
    case = random.choice(["Anemia","Kidney","Liver"])
    if case=="Anemia":
        return [round(random.uniform(6,10.5),1), int(random.uniform(4500,9000)), int(random.uniform(150000,300000)), round(random.uniform(0.7,1.2),2), int(random.uniform(15,40)), int(random.uniform(15,40)), round(random.uniform(0.3,1.0),1), "Anemia_Risk"]
    if case=="Kidney":
        return [round(random.uniform(11.5,14.5),1), int(random.uniform(4500,9000)), int(random.uniform(150000,300000)), round(random.uniform(1.4,3.5),2), int(random.uniform(15,40)), int(random.uniform(15,40)), round(random.uniform(0.3,1.5),1), "Kidney_Risk"]
    return [round(random.uniform(11.5,14.5),1), int(random.uniform(4500,9000)), int(random.uniform(150000,300000)), round(random.uniform(0.7,1.2),2), int(random.uniform(80,200)), int(random.uniform(80,200)), round(random.uniform(0.3,3.0),1), "Liver_Risk"]

rows=[]
for _ in range(600):
    rows.append(gen_row(normal=True))
for _ in range(300):
    rows.append(gen_row(normal=False))

df = pd.DataFrame(rows, columns=headers)
df.to_csv(csv_path, index=False)
print("Saved synthetic dataset to", csv_path)

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    X = df.drop("Label", axis=1)
    y = df["Label"]
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2, random_state=42)
    clf = RandomForestClassifier(n_estimators=200, random_state=42)
    clf.fit(X_train, y_train)
    model_out = Path(__file__).parent.parent / "backend" / "api" / "services" / "predict_model.pkl"
    model_out.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, model_out)
    print("Model trained and saved to", model_out)
except Exception as e:
    print("Training failed:", e)
