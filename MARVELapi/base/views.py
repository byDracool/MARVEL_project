from django.shortcuts import render
import hashlib
from django.conf import settings
import requests
import json

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


def comics_list(request):
    page = int(request.GET.get('page', 1))
    search_query = request.GET.get('search', '')
    limit = 20
    offset = (page - 1) * limit

    base_url = f'https://gateway.marvel.com/v1/public/comics?limit={limit}&offset={offset}'
    if search_query:
        base_url += f"&titleStartsWith={search_query}"

    auth_params = make_authorization()
    url = base_url + auth_params

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            comics = data['data']['results']

            # Add comic_json for each cómic
            for comic in comics:
                comic["comic_json"] = json.dumps(comic)

            total = data['data']['total']
        else:
            print(f"Request error: {response.status_code}")
            comics = []
            total = 0

    except requests.RequestException as exception:
        print(f"Request error: {exception}")
        comics = []
        total = 0

    total_pages = (total + limit - 1) // limit
    start_page = max(page - 3, 1)
    end_page = min(page + 3, total_pages)
    page_range = range(start_page, end_page + 1)

    context = {
        'comics': comics,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'search_query': search_query
    }
    # print("JSON EXAMPLE:", comics[0]["comic_json"])
    return render(request, 'base/comics.html', context)


def comic_detail(request):
    if request.method == "POST":
        comic_json = request.POST.get('comic_json')
        try:
            print("📥 JSON crudo recibido:", comic_json)
            comic = json.loads(comic_json)
        except Exception as e:
            print("❌ JSON DECODE ERROR:", e)
            comic = None
    else:
        comic = None

    return render(request, "base/comic_detail.html", {"comic": comic})

