from django.http import JsonResponse
from .models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import secrets
import bcrypt
import base64
import requests

@csrf_exempt
def users(request):
    if request.method != 'POST':
        # Si la solicitud no es de tipo POST, devuelve un error indicando que el método HTTP no es compatible
        return JsonResponse({"error": "HTTP method not supported"}, status=405)

    try:
        # Cargamos el cuerpo de la solicitud JSON en un objeto
        body_json = json.loads(request.body)
        # Extraemos los datos del cuerpo JSON de la solicitud
        json_username = body_json['name']
        json_email = body_json['mail']
        json_password = body_json['password']
        json_birthdate = body_json['birthdate']
    except KeyError:
        # Si falta algún parámetro en el cuerpo de la solicitud devuelve un error
        return JsonResponse({"error": "Missing parameter in body"}, status=400)

    if '@' not in json_email or len(json_email) < 5:
        # Verifica si el correo electrónico no es válido y devuelve un error si no lo es
        return JsonResponse({"error": "Invalid email"}, status=400)

    try:
        # Comprueba si ya hay un usuario registrado con ese correo electronico
        repeat_user = User.objects.get(email=json_email)
    except User.DoesNotExist:
        # Si no existe uno repetido continuamos al siguiente paso
        pass
    else:
        # Si el usuario ya existe, devuelve un error indicando que el correo electrónico ya está registrado
        return JsonResponse({"error": "Email already exists"}, status=400)

    # Hashea la contraseña proporcionada utilizando bcrypt
    salted_and_hashed_pass = bcrypt.hashpw(json_password.encode('utf8'), bcrypt.gensalt()).decode('utf8')

    # Crea un objeto User con los datos proporcionados y la contraseña hasheada
    user_object = User(name=json_username, email=json_email, encrypted_password=salted_and_hashed_pass, birthdate=json_birthdate)

    # Guarda el objeto User en la base de datos
    user_object.save()

    # Devuelve una respuesta JSON indicando que el usuario ha sido registrado correctamente
    return JsonResponse({"registered": True}, status=200)



