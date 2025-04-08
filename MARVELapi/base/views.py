from django.shortcuts import render
import hashlib
from django.conf import settings
import requests


def compute_md5_hash(my_string):
    m = hashlib.md5()
    m.update(my_string.encode('utf-8'))
    return m.hexdigest()


def make_authorization():
    publickey = settings.PUBLIC_KEY
    privatekey = settings.PRIVATE_KEY
    ts = 1
    md5_hash = compute_md5_hash(f'{ts}{privatekey}{publickey}')
    query_params = f'&ts={ts}&apikey={publickey}&hash={md5_hash}'
    return query_params


def home(request):
    return render(request, "base/home.html")


def characters(request):
    page = int(request.GET.get('page', 1))
    search_query = request.GET.get('search', '')
    limit = 20
    offset = (page - 1) * limit

    base_url = f'https://gateway.marvel.com/v1/public/characters?limit={limit}&offset={offset}'
    if search_query:
        base_url += f"&nameStartsWith={search_query}"

    auth_params = make_authorization()
    url = base_url + auth_params

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            characters = data['data']['results']
            total = data['data']['total']
        else:
            print(f"Request error: {response.status_code}")
            characters = []
            total = 0

    except requests.RequestException as exception:
        print(f"Request error: {exception}")
        characters = []
        total = 0

    total_pages = (total + limit - 1) // limit
    start_page = max(page - 3, 1)
    end_page = min(page + 3, total_pages)
    page_range = range(start_page, end_page + 1)

    context = {
        'characters': characters,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'search_query': search_query
    }

    return render(request, 'base/characters.html', context)


def character_detail(request, name):  # <- recibe el nombre desde la URL
    base_url = f'https://gateway.marvel.com/v1/public/characters?name={name}'
    auth_params = make_authorization()
    url = base_url + auth_params

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            character = data['data']['results'][0] if data['data']['results'] else None
        else:
            print(f"Request error: {response.status_code}")
            character = None
    except requests.RequestException as exception:
        print(f"Request error: {exception}")
        character = None

    context = {
        'character': character,
    }

    return render(request, "base/character_detail.html", context)




