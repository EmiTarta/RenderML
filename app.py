from flask import Flask, request, render_template
import datetime
import io
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import json
import base64
from io import BytesIO

app = Flask(__name__)

# Cargar el modelo
model = joblib.load("titanic_model.joblib")

conexion = "postgresql://postgres:myinstance@35.241.183.250:5432/predictions"
engine = create_engine(conexion)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint que recibe datos en formato JSON, realiza una predicción y guarda los datos en la base de datos.
    """
    # 1. Extraer los datos de entrada del HTLM
    pclass = int(request.form.get('feature1'))
    sex = int(request.form.get('feature2'))
    age = int(request.form.get('feature3'))

    # Se podria hacer asi (en conjunto): inputs = [int(x) for x in request.form.values()]
    # AHORA IRIA LA NORMALIZACION, SI NORMALICE
    # Realizar predicción con el modelo
    prediction = model.predict([[pclass, sex, age]])
    # Guardar en la base de datos
    timestamp = datetime.datetime.now().isoformat()
    logs = pd.DataFrame({"pclass": [pclass],
                                    "sex": [sex],
                                    "age":[age],
                                    "prediction": [int(prediction[0])],
                                    "timestamp": [timestamp[0:19]]})

    # Subir la prediccion
    logs.to_sql("predictions", con=engine, if_exists='append', index=False)

    ### Generamos la gráfica
    read_predictions = pd.read_sql("SELECT * FROM predictions", con=engine)
    fig = plt.figure()
    read_predictions.prediction.value_counts().plot(kind="bar")
    plt.title("Predicciones totales")
    
        # Guardar la gráfica en un buffer en memoria
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Devolver el resultado y la imagen (grafica) como respuesta
    return render_template("result.html", prediction=int(prediction[0]), grafica=img_base64)



@app.route('/records', methods=['GET'])
def records():
    """
    Endpoint que devuelve todos los registros guardados en la base de datos.
    """
    read_predictions = pd.read_sql("'''SELECT * FROM predictions'''", con=engine)
    return json.loads(read_predictions.to_json(orient="records"))

if __name__ == "__main__":
    app.run()
