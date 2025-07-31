import subprocess
import shlex
import spacy

nlp = spacy.load("es_core_news_sm")

def execute_command(command):
    try: 
        arguments = shlex.split(command) #convierte el texto del comando en una lista 
        result = subprocess.run(arguments, capture_output=True, text=True, check=True)  # Ejecuta el comando y captura la salida
        #capture_output=True -> captura la salida estandar y los erroes
        #text=True -> devuelve la salida como texto en lugar de bytes
        #check=True -> si el comando falla, lanza una excepcion
        return result.stdout
        #stdout -> salida estandar del comando
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar el comando: {e.stderr}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"
    

def is_safe_command(command):
    # Lista de comandos permitidos
    allowed_commands = ['ls', 'dir', 'pwd', 'mkdir', 'rm', 'cat', 'df', 'du', 'top', 'grep', 'find',
                        'chmod', 'chown', 'ufw', 'cd', 'mv', 'cp', 'clear']

    # Comandos peligrosos completos (por patrón exacto)
    exact_blocked = ['rm -rf /', ':(){ :|:& };:', 'mkfs', 'dd', 'bash']

    # Palabras clave peligrosas si se usan con parámetros peligrosos
    risky_patterns = {
        'rm': ['-rf', '--no-preserve-root', '/'],
        'chmod': ['777', '--recursive'],
        'chown': ['--recursive'],
        'mv': [' /'],  # mover al root
        'wget': ['http'],  # evitar descargas
        'curl': ['http'],
        'sudo': []
    }

    if not command or not command.strip():
        return False

    # Validar por coincidencia exacta
    for blocked in exact_blocked:
        if blocked in command:
            return False

    # Obtener el nombre base del comando
    cmd_name = command.split()[0]

    # Validar si es un comando permitido
    if cmd_name not in allowed_commands:
        return False

    # Verificar patrones peligrosos por comando
    for key, values in risky_patterns.items():
        if key in command:
            for risky_arg in values:
                if risky_arg in command:
                    return False

    return True



def parse_input(user_input):
    doc = nlp(user_input.lower().strip())  # convierte la frase a minusculas, quita espacios al incio y final

    # Extrae lemas de los verbos (forma base) y nombres
    verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
    #lemma -> forma base del verbo
    #token.pos == 'VERB' -> selecciona unicamente verbos
    nouns = [token.text for token in doc if token.pos_ in ("NOUN", "PROPN")]
    #token.pos in ("NOUN", "PROPN")' -> selecciona sustantivos comunes y propios

    #lu
    # Crear carpeta
    if "crear" in verbs:
        for i, token in enumerate(doc):
            if token.lemma_ == "crear" and i + 1 < len(doc):
                next_token = doc[i + 1]
                if next_token.text in ["carpeta", "directorio"]:
                    for t in doc[i+2:]:
                        if t.pos_ in ("PROPN", "NOUN"):
                            return f"mkdir {t.text}"

    # Eliminar archivo o carpeta
    if "eliminar" in verbs or "borrar" in verbs:
        for t in doc:
            if t.pos_ in ("PROPN", "NOUN"):
                return f"rm {t.text}"
    
    #################################################
    #gavilan
    return None




subprocess.run(["ls", "-aF"])

subprocess.run(
        ["ls -aF | grep main"],
        shell=True
        )

try:
    subprocess.run(["sleep", "5"], timeout=2)
except subprocess.TimeoutExpired:
    print("El proceso tardó demasiado")

capture = subprocess.run(
        ["ls -aF"],
        shell=True,
        text=True,
        capture_output=True
        )
print(capture.stdout)

try:
    subprocess.run(["ls", "archivo_inexistente.txt"], check=True)
except subprocess.CalledProcessError as e:
    print("Hubo un error:", e)

