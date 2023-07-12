from bson import ObjectId
from django.shortcuts import render
from rest_framework.views import APIView
from pymongo import MongoClient as Connection
from rest_framework.response import Response
import requests
import xmltodict


def db_connection(parameters=None, method=None):
    """database connection function

    Args:
        parameters (dict or str, optional): parameters.
        method (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    databaseName = "local"
    connection = Connection()

    db = connection[databaseName]
    collection_name = db['teste_python']
    
    if method == "insert":
        collection_name.insert_one(parameters)
    elif method == "delete":
        collection_name.delete_one({"_id": parameters})
    elif method == "update":
        update_id = parameters["id"]
        parameters.pop("id")
        collection_name.update_one({"_id": update_id},{"$set": parameters})
    elif method == "get":
        return collection_name.find_one(parameters)
    else:
        return collection_name.find() 
    

def insert_address(cep):
    address = requests.get(url=f'https://viacep.com.br/ws/{cep}/xml/')
            
    address_json = xmltodict.parse(address.text)["xmlcep"]
    
    if "erro" in address_json:
        return "Erro"
    
    insert_cep = {
        "Bairro": address_json["bairro"],
        "Cidade": address_json["localidade"],
        "UF": address_json["uf"],
        "CEP": address_json["cep"],
        "Logradouro": address_json["logradouro"],
        "Complemento": address_json["complemento"],
    }
    
    db_connection(insert_cep, "insert")
    
    data = {
        "sucesso" : True,
        "endereco" : {
            "cep" : address_json["cep"],
            "logr" : address_json["logradouro"],
            "compl" : address_json["complemento"],
            "bairro" : address_json["bairro"],
            "cidade" : address_json["localidade"],
            "uf": address_json["uf"]
        }
    }
    
    return data
    
    
class Address(APIView):
    def get(self, request):
        try:
            cep = request.query_params["cep"].replace(".", "").replace("-", "")
            result = insert_address(cep)
            if "Erro" in result:
                return Response(data="Cep inválido", status=200)            
            return Response(data=result, status=200)
        except:
            data = {}
            i = 0
            for item in  db_connection():
            # This does not give a very readable output
                try:
                    data[i] = {
                        "endereco" : {
                            "cep" : item["CEP"],
                            "logradouro" : item["Logradouro"],
                            "complemento" : item["Complemento"],
                            "bairro" : item["Bairro"],
                            "cidade" : item["Cidade"],
                            "uf": item["UF"]
                        }
                    }
                    i += 1
                except:
                    pass
            return Response(data=data, status=200)


class Person(APIView):
    
    def get(self, request):
        # params = request.query_params
        params_get = {}
        params = dict(request.query_params.lists())

        for item in params:
            if item.upper() == "CPF":
                params_get["CPF"] = params[item][0]
            else:
                params_get[item.capitalize()] = params[item][0]
        
        person = db_connection(
            params_get, 
            "get"
        )
        if person is None:
            return Response(data="Not found", status=404)
        
        person["id"] = str(person["_id"])
        
        person.pop("_id")
        
        endereco = db_connection(
            {"_id": ObjectId(person["Endereco"])}, 
            "get"
        )
        
        endereco.pop("_id")
        
        person["Endereco"] = endereco
        
        return Response(data=person, status=200)
    
    
    def delete(self, request, id):
        db_connection(
            ObjectId(id), 
            "delete"
        )

        return Response(status=200)
    
    
    def post(self, request):
        person_exists = db_connection(
            {
                "Nome": request.data["nome"],
                "Idade": request.data["idade"],
                "CPF": request.data["cpf"]
            }, 
            "get"
        )
        
        if person_exists is not None:
            return Response(data="User already exists", status=409)
        
        
        address = db_connection(
            {"CEP": request.data["cep"]}, 
            "get"
        )
        if address is None:
            cep = request.data["cep"]
            address = insert_address(cep)
            if "Erro" in address:
                return Response(data="Cep inválido", status=400)
        else:
            if "Erro" in address:
                return Response(data="Cep inválido", status=400)

        
        insert_person = {
            "Nome": request.data["nome"],
            "Idade": request.data["idade"],
            "CPF": request.data["cpf"],
            "Endereco": address["_id"]
        }
            
        db_connection(insert_person, "insert")
    
        return Response(status=200)
    
    
    def put(self, request, id):
        params_get = {}
        params_get["id"] = ObjectId(id)
        # params = dict(request.data.lists())

        
        for item in request.data:
            if item.upper() == "CPF":
                params_get["CPF"] = request.data[item]
            else:
                params_get[item.capitalize()] = request.data[item]
        
            
        db_connection(params_get, "update")
        
        return Response(status=200)
    
    