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
from dotenv import load_dotenv
import os
import google.generativeai as genai
from utils import get_prompt, generar_texto
load_dotenv()

app = Flask(__name__)

# Cargar el modelo
model = joblib.load("titanic_model.joblib")

conexion = os.environ["CONEXION"]
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
    inputs = pclass, sex, age
    
    # Se podria hacer asi (en conjunto): inputs = [int(x) for x in request.form.values()]
    # AHORA IRIA LA NORMALIZACION, SI NORMALICE
    # Realizar predicción con el modelo
    prediction = model.predict([[pclass, sex, age]])
    output = prediction[0]
    # Guardar en la base de datos
    timestamp = datetime.datetime.now().isoformat()
    logs = pd.DataFrame({"pclass": [pclass],
                                    "sex": [sex],
                                    "age":[age],
                                    "prediction": [int(prediction[0])],
                                    "timestamp": [timestamp[0:19]]})

    # Subir la prediccion
    logs.to_sql("predictions", con=engine, if_exists='append', index=False)

    # ### Generamos la gráfica
    read_predictions = pd.read_sql("SELECT * FROM predictions", con=engine)
    fig = plt.figure()
    read_predictions.prediction.value_counts().plot(kind="bar", color="#012944")
    plt.title("Sobrevivientes (1: sobrevivió, 0: no lo ha logrado)")

    # Guardar la gráfica en un buffer en memoria
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close(fig)
    img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
    
    # Generar texto IA
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
    modelo = genai.GenerativeModel('gemini-2.0-flash-exp')
    prompt = get_prompt(inputs, output)
    generacion = generar_texto(modelo, prompt)

        # Devolver el resultado y la imagen (grafica) como respuesta
    return render_template("result.html", prediction=int(prediction[0]), grafica=img_base64, generacion=generacion)


@app.route('/records', methods=['GET'])
def records():
    """
    Endpoint que devuelve todos los registros guardados en la base de datos.
    """
    read_predictions = pd.read_sql("'''SELECT * FROM predictions'''", con=engine)
    return json.loads(read_predictions.to_json(orient="records"))

if __name__ == "__main__":
    app.run(host="0.0.0.0")
