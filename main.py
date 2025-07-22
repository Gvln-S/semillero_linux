import subprocess

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

