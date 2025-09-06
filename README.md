# PDI-2025-GRUPO02
# Pequeño bug en tp1: Para poder ver la imagen YIQ hay que pasar el cursor por encima del campo que contiene la imagen.
# CLONAR GIT PARA TRABAJAR
Abrir terminal CMD o Bash
Posicionate en el directorio donde se va a crear automaticamente la carpeta
# Copia el siguente comando:
    git clone https://github.com/Lucas976g/PDI-2025-GRUPO02.git

# ingresa en la carpeta clonada con el comando: 
    cd PDI-2025-GRUPO02

# Crea un entorno virtual de python:
    
    🔹 En windows el comando es:
            python -m venv .venv
    
    🔹 En Mac el comando es: 
            python3 -m venv .venv
        
# Activar el entorno Virtual:
    🔹 En Windows:
            .venv\Scripts\activate

    🔹 En MacOS:
            source .venv/bin/activate

# Cuando se active, vas a ver que al inicio de tu terminal aparece:
    (.venv) C:\ruta\del\proyecto>

# En cualquier momento podés salir con:
    deactivate

# ahora hay que instalar las librerias con el siguiente comando:
    pip install -r requirements.txt

# para iniciar el sistema se utiliza el comando: 
    python main.py

# WORKFLOW PARA ACTUALIZACIONES
## Ver qué cambió
git status
## Agregar cambios
git add .
## Commit con descripción
git commit -m "Agregado TP2: filtros en imágenes"
## Subir a GitHub
git push






