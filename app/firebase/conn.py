import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
import os

# Obtener la ruta del directorio donde se encuentra el script actual
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta al archivo de credenciales
cred_path = os.path.join(current_dir, "tdah-app-firebase.json")

cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    'storageBucket': 'tdah-app-7c3f4.appspot.com'  
})
