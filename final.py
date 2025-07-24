import subprocess
import shlex
import re

def execute_command(command):
    """Ejecuta un comando Linux y devuelve la salida o un error."""
    try:
        # Divide el comando en argumentos seguros
        args = shlex.split(command)
        # Ejecuta el comando y captura la salida
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error al ejecutar el comando: {e.stderr}"
    except Exception as e:
        return f"Error inesperado: {str(e)}"

def is_safe_command(command):
    """Verifica si el comando es seguro para ejecutar (evita comandos peligrosos)."""
    # Lista de comandos permitidos
    allowed_commands = ['ls', 'dir', 'pwd', 'mkdir', 'rm', 'cat', 'df', 'du', 'top']
    # Extrae el comando principal
    cmd_name = command.split()[0] if command else ""
    # Evita comandos peligrosos como 'rm -rf /'
    if 'rm -rf /' in command or 'sudo' in command:
        return False
    return cmd_name in allowed_commands

def parse_input(user_input):
    """Procesa la entrada en lenguaje natural y devuelve el comando Linux correspondiente."""
    user_input = user_input.lower().strip()
    
    # Reglas simples para mapear frases a comandos
    if re.match(r"^(muestra|lista|ver)\s+(archivos|carpetas|directorio)", user_input):
        return "ls -l"
    elif re.match(r"^(dime|muestra)\s+(donde estoy|directorio actual)", user_input):
        return "pwd"
    elif re.match(r"^(crea|crear)\s+(una carpeta|carpeta|directorio)\s+([\w]+)", user_input):
        match = re.match(r"^(crea|crear)\s+(una carpeta|carpeta|directorio)\s+([\w]+)", user_input)
        folder_name = match.group(3)
        return f"mkdir {folder_name}"
    elif re.match(r"^(elimina|borra|borrar)\s+(archivo|carpeta)\s+([\w]+)", user_input):
        match = re.match(r"^(elimina|borra|borrar)\s+(archivo|carpeta)\s+([\w]+)", user_input)
        file_name = match.group(3)
        return f"rm {file_name}"
    elif re.match(r"^(muestra|ver)\s+(contenido de|archivo)\s+([\w\.]+)", user_input):
        match = re.match(r"^(muestra|ver)\s+(contenido de|archivo)\s+([\w\.]+)", user_input)
        file_name = match.group(3)
        return f"cat {file_name}"
    elif re.match(r"^(muestra|ver)\s+(uso del disco|espacio en disco)", user_input):
        return "df -h"
    elif re.match(r"^(muestra|ver)\s+(procesos|actividad)", user_input):
        return "top -bn1"  # -bn1 para una sola iteración en modo batch
    else:
        return None

def main():
    print("Asistente de Linux: Escribe comandos en lenguaje natural (o 'salir' para terminar).")
    while True:
        user_input = input("> ")
        if user_input.lower() == "salir":
            print("¡Hasta luego!")
            break
        
        # Procesa la entrada del usuario
        command = parse_input(user_input)
        if not command:
            print("Lo siento, no entendí la instrucción. Intenta con algo como 'muestra los archivos' o 'crea una carpeta prueba'.")
            continue
        
        # Verifica si el comando es seguro
        if not is_safe_command(command):
            print("Comando no permitido o potencialmente peligroso.")
            continue
        
        # Ejecuta el comando
        output = execute_command(command)
        print(output)

if __name__ == "__main__":
    main()
