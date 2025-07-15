from django.shortcuts import render
from django.http import JsonResponse

def recommend_game(request):
    return JsonResponse({'message': 'Recommend endpoint works!'})

def search_games(request):
    return JsonResponse({'message': 'Search endpoint works!'})

def home(request):
    return render(request, "home.html")
