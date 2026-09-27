# app.py - Asesor Nutricional Personal (Flask + API de Groq)
from flask import Flask, render_template, request, jsonify
import os
import re
from dotenv import load_dotenv
from groq import Groq

# Cargar variables de entorno (.env). override=True hace que el .env tenga prioridad
# sobre variables de entorno del sistema con el mismo nombre
load_dotenv(override=True)

app = Flask(__name__)

# Inicializar el cliente de Groq
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Modelo a utilizar (se puede cambiar en el .env si el modelo pasa a "deprecated")
MODELO = os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')

# Edades seleccionables
edades = list(range(14, 91))

# Niveles de actividad
niveles_actividad = [
    ('sedentario', 'Sedentario (Poco o ningún ejercicio)'),
    ('poco_activo', 'Poco Activo (1-3 días/semana)'),
    ('moderadamente_activo', 'Moderadamente Activo (3-5 días/semana)'),
    ('muy_activo', 'Muy Activo (6-7 días/semana)'),
    ('super_activo', 'Super Activo (Atleta profesional/2x entrenamientos)')
]


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', edades=edades, niveles_actividad=niveles_actividad)


@app.route('/plan', methods=['POST'])
def plan():
    # Obtener datos del formulario
    edad = request.form.get('edad', '').strip()
    nivel = request.form.get('nivel_actividad', '').strip()
    comidas_favoritas = request.form.get('comidas_favoritas', '').strip()
    restricciones = request.form.get('restricciones', '').strip() or 'Ninguna'

    # Validación básica
    niveles = dict(niveles_actividad)
    if not edad.isdigit() or int(edad) not in edades:
        return jsonify({'success': False, 'error': 'Selecciona una edad válida.'})
    if nivel not in niveles:
        return jsonify({'success': False, 'error': 'Selecciona un nivel de actividad válido.'})
    if not comidas_favoritas:
        return jsonify({'success': False, 'error': 'Indica al menos una comida favorita.'})

    nivel_actividad = niveles[nivel]

    # Construir el prompt
    prompt = f"""Como nutricionista profesional, crea un plan de nutrición personalizado para alguien con el siguiente perfil:

Edad: {edad} años
Nivel de Actividad: {nivel_actividad}
Comidas Favoritas: {comidas_favoritas}
Restricciones Dietéticas/Alergias: {restricciones}

Por favor, proporciona:
1. Estimación de necesidades calóricas diarias
2. Distribución recomendada de macronutrientes
3. Un plan de comidas diario de ejemplo incorporando sus comidas favoritas cuando sea posible
4. Consideraciones nutricionales específicas para su grupo de edad
5. Recomendaciones basadas en su nivel de actividad
6. Alternativas seguras para cualquier alimento restringido
7. 2-3 sugerencias de snacks saludables

Formatea la respuesta claramente con encabezados y puntos para facilitar la lectura.
Ten en cuenta la salud y la seguridad, especialmente con respecto a las restricciones mencionadas."""

    print("Prompt que vamos a enviar a Groq:")
    print("-----------------------------")
    print(prompt)
    print("-----------------------------")

    try:
        completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Eres un nutricionista profesional. Respondes siempre en español, "
                               "usando formato Markdown con encabezados y listas."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model=MODELO,
            temperature=0.7,
            max_tokens=2500,
        )

        respuesta = completion.choices[0].message.content
        # Algunos modelos de razonamiento incluyen su "pensamiento" entre etiquetas <think>
        respuesta = re.sub(r'<think>.*?</think>', '', respuesta, flags=re.DOTALL).strip()
        return jsonify({'success': True, 'plan': respuesta})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    app.run(debug=True)
