from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Animes, Usuario
import os
from django.core.paginator import Paginator
from django.conf import settings
from .forms import CambiarInformacionForm

User = get_user_model()

def webapp(request):
    messages.get_messages(request)  # Obtener mensajes almacenados
    all_animes = Animes.objects.all()
    paginator = Paginator(all_animes, 9)  # Mostrar 9 animes por página

    page_number = request.GET.get('page')
    animes = paginator.get_page(page_number)

    return render(request, 'webapp/index.html', {'animes': animes})


def anime_detail(request, nombre_anime):
    anime = get_object_or_404(Animes, nombre_anime=nombre_anime)
    return render(request, 'webapp/anime_detail.html', {'anime': anime})

@login_required
def cuenta(request):
    user = request.user
    if request.method == 'POST':
        field_name = request.POST.get('field_name')
        new_value = request.POST.get('new_value')
        
        if field_name == 'username':
            user.username = new_value
        elif field_name == 'correo':
            user.email = new_value
        elif field_name == 'nombre':
            user.first_name = new_value
        elif field_name == 'apellido':
            user.last_name = new_value
        
        user.save()
        messages.success(request, 'La información de usuario ha sido actualizada exitosamente.')
        return redirect('cuenta')
    else:
        form = CambiarInformacionForm(instance=user)

    return render(request, 'webapp/cuenta.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)  # Verificar si el usuario es un administrador
@login_required  # Requiere que el usuario esté autenticado
def agregar_anime(request):
    if request.method == 'POST':
        id_anime = request.POST['id_anime']
        nombre_anime = request.POST['nombre_anime']
        descripcion_anime = request.POST['descripcion_anime']
        imagen_archivo = request.FILES['imagen_anime']
        portada_archivo = request.FILES['portada_anime']
        imagen_nombre = request.POST['nombre_imagen_anime']
        portada_nombre = request.POST['nombre_portada_anime']

        # Guardar las imágenes en tu directorio local
        imagen_path = os.path.join(settings.BASE_DIR, 'webapp', 'static', 'images', imagen_nombre)
        portada_path = os.path.join(settings.BASE_DIR, 'webapp', 'static', 'images', portada_nombre)

        with open(imagen_path, 'wb') as f:
            f.write(imagen_archivo.read())

        with open(portada_path, 'wb') as f:
            f.write(portada_archivo.read())

        # Crear el objeto Animes con los campos y nombres de imágenes
        anime = Animes(
            id_anime=id_anime,
            nombre_anime=nombre_anime,
            descripcion_anime=descripcion_anime,
            imagen_anime=os.path.join('images', imagen_nombre),
            portada_anime=os.path.join('images', portada_nombre)
        )
        anime.save()

    animes = Animes.objects.all()

    return render(request, 'webapp/agregar_anime.html', {'animes': animes})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None and check_password(password, user.password):
            login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')
            return redirect('webapp')  # Cambia 'webapp' con la URL de tu página principal
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
            return redirect('login')  # Cambia 'login' con la URL de tu página de inicio de sesión

    return render(request, 'webapp/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password1']
        nombre = request.POST['nombre']
        apellido = request.POST['apellido']
        email = request.POST['email']

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe. Por favor, elige otro nombre de usuario.')
        else:
            # Realizar las acciones necesarias para registrar al usuario
            # Crea una instancia de Usuarios y guarda los datos
            user = Usuario(username=username, first_name=nombre, last_name=apellido, email=email)
            user.set_password(password)  # Establecer la contraseña utilizando set_password()
            user.save()
            messages.success(request, 'Registro exitoso. Inicia sesión con tu nueva cuenta.')
            return redirect('login')  # Cambia 'login' con la URL de tu página de inicio de sesión

    return render(request, 'webapp/register.html')

def logout_view(request):
    logout(request)
    return redirect('webapp')  # Cambia 'webapp' con la URL de tu página principal
