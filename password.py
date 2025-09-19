import random

caracteres = "+-/*!&$#?=@abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
tamano = int(input('ingresa la longitud de tu contrasena'))
contrasena = ""

for i in range(tamano):
    contrasena += random.choice(caracteres)

print("tu contrasena desde ahora sera:", contrasena)
