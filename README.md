# Asesor Nutricional Personal (Flask + Groq)

Aplicación web que genera un plan nutricional personalizado a partir de la edad, el nivel de actividad, las comidas favoritas y las restricciones dietéticas del usuario, usando un LLM a través del API de Groq.

## Estructura

- `app.py`: controlador Flask. `GET /` muestra el formulario y `POST /plan` construye el prompt, llama a Groq y devuelve la respuesta en JSON.
- `templates/index.html`: vista (formulario + JavaScript que llama a `/plan` y muestra el resultado en Markdown).

## Instalación

```
py.exe -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Crear un fichero `.env` con la API key de https://console.groq.com/keys:

```
GROQ_API_KEY=XXXXX
# Opcional: cambiar el modelo si el de por defecto está "deprecated"
# GROQ_MODEL=openai/gpt-oss-20b
```

## Ejecución

```
py.exe app.py
```

Abrir http://localhost:5000 en el navegador.
