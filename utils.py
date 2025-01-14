# Funciones 
import google.generativeai as genai
def get_prompt(inputs, outputs):
    mapa = {0: "no sobrevive", 1: "sobrevive"}
    pclass, sex, age = inputs
    prediction = mapa[outputs]
    prompt = f"""Hola gemini! estoy haciendo una API de prediccion de supervivencia o no con el dataset del titanic.
    He usado 3 features: Pclass, Age y Sex. Lo que necesito es pasarte los iputs y la prediccion del modelo,
    y que me generes un texto especuladno, a traves de los inputs dados y la prediccion del modelo,los motivos por los cuales el modelo ha hecho esa prediccion
    y si tiene sentido o no la misma, dado el contexto. Quiero que lo escribas dando las condolencias y el más sentido pésame, si no ha sobrevivido, de una forma muy sentida; 
    si ha sobrevivido, felicítale con "bombos y platillas", con "corona de laureles" dile lo bonito que es estar vivo.  
    Pero quero un texto conciso, entre 100 y 500 palabras maximo.
    Se creativo, mojate.
    Importante 1: el formato de salida ha de ser UNICA Y EXCLUSIVAMENTE el texto narrado. No me des saludos, metadatos, ni nada,
    a parte del breve texto.
    Importante 2: Ademas, omite todo tipo de formato enriquecido (markdown, HTML, etc...). Dame solo texto plano.
    Importante 3: Para que el texto no resulte muy horizontal, incluye numerosos saltos de linea
    EL CONTEXTO ES EL SIGUIENTE: 
    inputs:
    Pclass = {inputs[0]}
    Sex = {inputs[1]} (siendo 0 Male y 1 Female)
    Age = {inputs[2]} (edad en años)
    Prediccion = {mapa[outputs]}
    Tu respuesta aqui: 
    """
    return prompt

def generar_texto(model, prompt, top_k=40, stop_sequences=None, temperature=0.7, top_p=1.0, max_output_tokens=512):

   response = model.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            top_p=top_p,
            top_k=top_k,
            stop_sequences = stop_sequences))
   return response.text