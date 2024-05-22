from django.http import JsonResponse
from .models import User, Supermercado1Producto, Supermercado2Producto
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
import secrets
import bcrypt
import base64
import requests

@csrf_exempt
def users(request):
    if request.method != 'POST': # curl -X POST -H "Content-Type: application/json" -d "{\"name\": \"Jhosue\", \"mail\": \"arrietacordova10@gmail.com\", \"password\": \"Carmenchu10\", \"birthdate\": \"2004-04-03\"}" http://localhost:8000/v1/users/
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
        # Obtener el token de sesión del encabezado
        sessionToken = request.headers.get('sessionToken')
        # Verificar si el token de sesión está presente
        if not sessionToken:
            return JsonResponse({'error': 'Header token missing'}, status=401)
        # Cerramos la sesión asignando NONE al campo del token de la bbdd
        session = User.objects.get(token=sessionToken) 
        session.token = None
        session.save() 
        return JsonResponse({'message': 'Session closed successfully'}, status=200)

@csrf_exempt    
def account(request):
    if request.method == 'GET': # curl -X GET -H "sessionToken: tu_token_de_sesion" http://localhost:8000/v1/account/
        # Obtener el token de sesión del encabezado
        sessionToken = request.headers.get('sessionToken')
        # Verificar si el token de sesión está presente
        if not sessionToken:
            return JsonResponse({'error': 'Header token missing'}, status=401)
        # Recupera la sesión del usuario correspondiente al token pasado en la bbdd
        session = User.objects.get(token=sessionToken) 

        json_response = session.to_jsonAccount() 
        return JsonResponse(json_response, status=200) 

@csrf_exempt
def password(request): 
    if request.method != 'POST': # curl -X POST -H "Content-Type: application/json" -H "sessionToken: 3cf6c274600c384522bc" -d "{\"current_password\": \"Carmenchu10\", \"new_password\": \"CCarmenchu10\"}" http://localhost:8000/v1/password/
        return JsonResponse({'error': 'HTTP method not supported'}, status=405)
    # Obtener el cuerpo de la solicitud JSON
    try:
        body_json = json.loads(request.body)
        current_password = body_json['current_password']
        new_password = body_json['new_password']
    except KeyError:
        return JsonResponse({'error': 'Missing parameter in body'}, status=400)
    # Obtener el token de sesión del encabezado
    sessionToken = request.headers.get('sessionToken')
    # Verificar si el token de sesión está presente
    if not sessionToken:
        return JsonResponse({'error': 'Header token missing'}, status=401)
    # Obtener el usuario con el token de sesión proporcionado
    try:
        user = User.objects.get(token=sessionToken)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid sessionToken'}, status=401)

    # Verificar la contraseña actual
    if not bcrypt.checkpw(current_password.encode('utf8'), user.encrypted_password.encode('utf8')):
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

    # Generar el hash para la nueva contraseña
    hashed_new_password = bcrypt.hashpw(new_password.encode('utf8'), bcrypt.gensalt()).decode('utf8')

    # Actualizar la contraseña del usuario
    user.encrypted_password = hashed_new_password
    user.save()
    return JsonResponse({'message': 'Password updated successfully'}, status=200)

@csrf_exempt
def search_product1(request): 
    if request.method != 'GET': # curl -X GET http://localhost:8000/v1/search_product1/?q=manzanas
        return JsonResponse({'error': 'HTTP method not supported'}, status=405)

    # Obtener el parámetro de búsqueda de la URL
    try:
        search_str = request.GET["q"]
    except KeyError:
        return JsonResponse({'error': 'Missing query parameter'}, status=400)

    # Buscar productos que coincidan con la cadena de búsqueda
    productos1 = Supermercado1Producto.objects.filter(nombre__icontains=search_str)

    # Crear una lista de productos en formato JSON
    productos_list1 = []
    for producto in productos1:
        productos_list1.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'origen': producto.origen,
            'imagen_url': producto.imagen_url,
        })

    return JsonResponse({'productos': productos_list1}, status=200)

@csrf_exempt
def search_product2(request):
    if request.method != 'GET': # curl -X GET http://localhost:8000/v1/search_product2/?q=manzanas
        return JsonResponse({'error': 'HTTP method not supported'}, status=405)

    # Obtener el parámetro de búsqueda de la URL
    try:
        search_str = request.GET["q"]
    except KeyError:
        return JsonResponse({'error': 'Missing query parameter'}, status=400)

    # Buscar productos que coincidan con la cadena de búsqueda
    productos2 = Supermercado2Producto.objects.filter(nombre__icontains=search_str)

    # Crear una lista de productos en formato JSON
    productos_list2 = []
    for producto in productos2:
        productos_list2.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'origen': producto.origen,
            'imagen_url': producto.imagen_url,
        })

    return JsonResponse({'productos': productos_list2}, status=200)

@csrf_exempt
def info_product1(request, product_id): 
    if request.method != 'GET': # curl -X GET http://localhost:8000/v1/info_product1/1/
        return JsonResponse({'error': 'HTTP method not supported'}, status=405)

    try:
        # Obtenemos el producto del Supermercado1 y comprobamos que exista
        producto = Supermercado1Producto.objects.get(id=product_id)
    except Supermercado1Producto.DoesNotExist:
        return JsonResponse({'error': 'Product not found in this supermarket'}, status=404)

    # Creamos la respuesta json a mostrar
    producto_info = {
        'nombre': producto.nombre,
        'precio': float(producto.precio),
        'origen': producto.origen,
        'imagen_url': producto.imagen_url,
    }

    return JsonResponse(producto_info, status=200)

@csrf_exempt
def info_product2(request, product_id): 
    if request.method != 'GET': # curl -X GET http://localhost:8000/v1/info_product2/1/
        return JsonResponse({'error': 'HTTP method not supported'}, status=405)

    try:
        # Obtenemos el producto del Supermercado2 y comprobamos que exista
        producto = Supermercado2Producto.objects.get(id=product_id)
    except Supermercado2Producto.DoesNotExist:
        return JsonResponse({'error': 'Product not found in this supermarket'}, status=404)

    # Creamos la respuesta json a mostrar
    producto_info = {
        'nombre': producto.nombre,
        'precio': float(producto.precio),
        'origen': producto.origen,
        'imagen_url': producto.imagen_url,
    }

    return JsonResponse(producto_info, status=200)