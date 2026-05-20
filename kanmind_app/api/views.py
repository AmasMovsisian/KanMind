from django.shortcuts import render
from django.http import JsonResponse

def startKanmind(request):
    return JsonResponse({
        "message" : "kanmind hat funktioniert"
    })