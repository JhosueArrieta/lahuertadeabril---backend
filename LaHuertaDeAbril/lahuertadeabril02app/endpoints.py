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

@csrf_exempt    
def sessions(request):
    if request.method == 'POST': # curl -X POST -d "{"email": "arrietacordova10@gmail.com", "password": "Carmenchu10"}" http://localhost:8000/v1/sessions/
        # Sacamos los datos de la solicitud http y los guardamos en variables
        try: 
            body_json = json.loads(request.body)
            json_email = body_json['email']
            json_password = body_json['password']
        except KeyError: 
            return JsonResponse({'error': 'Request error or invalid data'}, status=400)
        # Comprobamos que el email y contraseña existan en la bbdd
        try: 
            db_user = User.objects.get(email=json_email)
        except User.DoesNotExist: 
            return JsonResponse({'error': 'User not found in database'}, status=404) 
        if bcrypt.checkpw(json_password.encode('utf8'), db_user.encrypted_password.encode('utf8')): 
            pass
        else:
            json_password!=db_user.encrypted_password 
            return JsonResponse({'error': 'Invalid credentials'}, status=401)
        # Generamos un token random y lo asignamos
        random_token = secrets.token_hex(10)
        db_user.token = random_token 
        db_user.save()  
        return JsonResponse({"sessionToken": random_token}, status=200) 
    
    elif request.method == 'DELETE': # curl -X DELETE -H "sessionToken: tu_token_de_sesion" http://localhost:8000/v1/sessions/
        # Comprobamos que haya un token en la cabecera 
        try:
            header_token = request.headers.get('sessionToken', None) 
        except AttributeError:
            return JsonResponse({'error': 'Body token missing'}, status=401)
        # Cerramos la sesión asignando NONE al campo del token de la bbdd
        session = User.objects.get(token=header_token) 
        session.token = None
        session.save() 
        return JsonResponse({'message': 'Session closed successfully'}, status=200)

@csrf_exempt    
def account(request):
    if request.method == 'GET': 
        # Recuperamos token de la cabecera
        try:
            header_token = request.headers.get('sessionToken', None) 
        except AttributeError: 
            return JsonResponse({'error': 'Falta el token del cuerpo'}, status=401)
        # Recupera la sesión del usuario correspondiente al token pasado en la bbdd
        session = User.objects.get(token=header_token) 
        json_response = session.to_jsonAccount() 
        return JsonResponse(json_response, status=200) 


