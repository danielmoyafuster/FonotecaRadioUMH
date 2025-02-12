import sqlite3
import requests
from tqdm import tqdm  # 📊 Barra de progreso
import base64

# ⚡ Tu Client ID y Client Secret de Spotify (debes generarlos en https://developer.spotify.com)

CLIENT_ID = "f539334f19094e47ae8df45cc373cce9"
CLIENT_SECRET = "62f90ff98a2d4602968a488129aeae31"

# Codificar credenciales en Base64
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
credentials_b64 = base64.b64encode(credentials.encode()).decode()

# Realizar solicitud para obtener el token
url = "https://accounts.spotify.com/api/token"
headers = {
    "Authorization": f"Basic {credentials_b64}",
    "Content-Type": "application/x-www-form-urlencoded"
}
data = {"grant_type": "client_credentials"}

response = requests.post(url, headers=headers, data=data)

# Mostrar resultado
print(response.status_code, response.text)