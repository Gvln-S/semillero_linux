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
                        'chmod', 'chown', 'ufw', 'cd', 'mv', 'cp', 'clear', 'ps']

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

    # Crear carpeta "nombre"
    if "crear" in verbs:
        for i, tok in enumerate(doc):
            #determina si el verbo es crear
            if tok.lemma_ == "crear" and i+1 < len(doc):
                nxt = doc[i+1].lemma_
                #determina si el siguiente token es un nombre
                if nxt in ("carpeta", "directorio"):
                    if i+2 < len(doc):
                        #el ultimo token lo toma como el nombre de la carpeta o directorio
                        name = doc[i+2].text
                        return f"mkdir {name}"

    target = None
    is_dir = False
    force = False

    # Eliminar archivo o carpeta
    if any(v in verbs for v in ("eliminar", "borrar")):
        #determina si la palabra forzar esta en la frase
        for i, tok in enumerate(doc):
            if tok.text in ("forzar", "forzado"):
                #si si pone en true el force
                force = True
            #determina el objeto de la oración
            if tok.pos_ in ("PROPN","NOUN"):
                prev = doc[i-1].lemma_ if i>0 else ""
                #si es carpeta o directorio is_dir se vuelve true
                if prev in ("carpeta","directorio"):
                    is_dir = True
                target = tok.text
    if target:
        #crea una lista a al que le va añadiendo las partes del comando necesarias
        flags = []
        if is_dir: flags.append("-r")
        if force:  flags.append("-f")
        #va formando el string del comando
        flag_str = (" " + " ".join(flags)) if flags else "" 
        #devuelve el comando con la lista y el target 
        return f"rm{flag_str} {target}"

    #ps
    if any(v in verbs for v in ("listar", "mostrar")) and "procesos" in nouns:
        if any(n in nouns for n in ("todos",)):
            return "ps -e"
        elif any(n in nouns for n in("completos",)):
            return "ps -f"
        elif any(n in nouns for n in("forma","larga","formato")):
            return "ps -l"

    #listar archivos
    elif any(v in verbs for v in ("listar","mostrar")):
        #verifica el verbo de la oración
        if any(n in nouns for n in ("todos","archivos","ocultos")):
            #luego busca el sustantivo de la oración y si es alguno de estos devuelve el comando
            return "ls -aF"
        else:
            #si no devuelve el comando de listar
            return "ls"

    #mostrar directorio actual
    if any(v in verbs for v in ("mostrar","ver")) and "directorio" in nouns:
        #si mostrar y directorio estan en la misma oración, entonces devuelve el comando
        return "pwd"

    #buscar texto
    if "grep" in user_input:
        # si el usuario ya ha escrito grep, retornamos directamente
        return user_input.strip()

    if any(v in verbs for v in ("buscar","encontrar")) and "texto" in nouns:
        # asume: "buscar texto X en archivo Y"
        words = [tok.text for tok in doc]
        try:
            idx_txt = words.index("texto")
            pattern = words[idx_txt+1]
            idx_en = words.index("en")
            target = words[idx_en+1]
            # caso recursivo
            rec = "-r " if "recursivo" in nouns else ""
            ignore = "-i " if "mayúsculas" in nouns or "case" in user_input else ""
            return f"grep {ignore}{rec}'{pattern}' {target}"
        except ValueError:
            pass

    #buscar archivos o directorios
    if "find" in user_input:
        return user_input.strip()

    if any(v in verbs for v in ("buscar","encontrar")) and any(n in nouns for n in ("archivo","directorio")):
        # modificados recientemente
        if "modificados" in nouns or "modificado" in nouns:
            return "find . -mtime -1"
        # búsqueda por nombre
        for tok in doc:
            if tok.pos_ in ("PROPN","NOUN") and tok.text not in ("archivo","directorio"):
                return f"find . -name \"{tok.text}\""
        return "find ."

    if "buscar" in verbs or "encontrar" in verbs:
        for t in doc:
            if t.pos_ in ("PROPN", "NOUN"):
                return f"find -name {t.text}"

#################################################
#Gavilán

art = """
              .................................
              ................x................
              ............,ooOMldl.............
              ............':XMMMk;.............
              ..........oXXo;,c':kWO;..........
              .........KMk'd;:k.lo;WMc.........
              ........oMM..o:lX'o:.oMN.........
              ........dMM..dk;o;0:.cMM.........
              ........,MMl'Kc,d.kO.KMO.........
              .........;XMx,.lK'.,0Wx..........
              ...........;dkl;;cdxc............
              ......'cxxc....0M:...,oko;.......
              .........;OWk,.OM:.lXNo..........
              ...........,OMk0MoNNo............
              ..............:XMd,..............
              ...............kM'...............
               ..............dM'..............
                 .............l.............
                    .....................
                              .
"""

def main(): 
    print(art)
    print("Asistente de Linux por Luisa y Santiago")
    while True:
        user_input = input("> ")
        if user_input.lower() == "salir":
            print("¡Nos vemos!")
            break

        command = parse_input(user_input)
        if not command:
            print("Lo siento, no entendí la instrucción")
            continue

        if not is_safe_command(command):
            print("Comando no permitido o potencialmente peligroso.")
            continue
        
        output = execute_command(command)
        print(output)

if __name__ == "__main__":
    main()
