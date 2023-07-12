from django.db import models
class Adress(models.Model):

    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    uf = models.CharField(max_length=255)
    cep = models.CharField(max_length=255)
    logradouro = models.CharField(max_length=255)
    complement = models.CharField(max_length=255)

class Person(models.Model):
    nome = models.CharField(max_length=255)
    idade = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11)
    