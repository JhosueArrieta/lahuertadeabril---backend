from django.db import models

# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=120)
    encrypted_password = models.CharField(max_length=120)
    birthdate = models.DateField(auto_now_add=False)
    token = models.CharField(unique=True, null=True, max_length=50)

    def to_jsonAccount(self):
        return {
            "correo": self.email
        }

class Supermercado1Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

class Supermercado2Producto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.URLField()

class FavSupermercado1(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Supermercado1Producto, on_delete=models.CASCADE)

class FavSupermercado2(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    producto = models.ForeignKey(Supermercado2Producto, on_delete=models.CASCADE)
