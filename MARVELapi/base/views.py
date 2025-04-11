from django.shortcuts import render
import hashlib
from django.conf import settings
import requests
import json
import base64


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


def character_detail(request, name):
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


def creators_list(request):
    import json

    page = int(request.GET.get('page', 1))
    search_query = request.GET.get('search', '')
    limit = 20

    valid_creators = []
    total_valid = 0
    original_page = page
    tries = 0
    max_tries = 5

    while not valid_creators and tries < max_tries:
        offset = (page - 1) * limit
        base_url = f'https://gateway.marvel.com/v1/public/creators?limit={limit}&offset={offset}'
        if search_query:
            base_url += f"&nameStartsWith={search_query}"

        auth_params = make_authorization()
        url = base_url + auth_params

        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                creators = data['data']['results']
                total = data['data']['total']  # No filtered total
                filtered = [c for c in creators if c.get('fullName')]

                valid_creators = filtered
                total_valid += len(filtered)
            else:
                print(f"Request error: {response.status_code}")
                break
        except requests.RequestException as e:
            print(f"Request error: {e}")
            break

        if not valid_creators:
            page += 1
            tries += 1

    for creator in valid_creators:
        creator['creator_json'] = json.dumps(creator)

    total_pages = max(page, 1) + 2

    start_page = max(original_page - 3, 1)
    end_page = min(original_page + 3, total_pages)
    page_range = range(start_page, end_page + 1)

    context = {
        'creators': valid_creators,
        'page': original_page,
        'total_pages': total_pages,
        'page_range': page_range,
        'search_query': search_query
    }

    return render(request, 'base/creators.html', context)


def creator_detail(request):
    view_type = request.GET.get("view", "detail")  # por defecto usamos "detail"

    if request.method == "POST":
        creator_json = request.POST.get('creator_json')
        try:
            creator = json.loads(creator_json)
        except Exception as e:
            print("❌ JSON decode error:", e)
            creator = None
    else:
        creator = None

    if view_type == "detail":
        return render(request, "base/creator_detail.html", {"creator": creator})
    elif view_type == "comics":
        return render(request, "base/creator_comics.html", {"creator": creator})
    elif view_type == "series":
        return render(request, "base/creator_series.html", {"creator": creator})
    elif view_type == "stories":
        return render(request, "base/creator_stories.html", {"creator": creator})


    return render(request, "base/creator_detail.html", {"creator": creator})


def events_list(request):
    page = int(request.GET.get('page', 1))
    search_query = request.GET.get('search', '')
    limit = 20
    offset = (page - 1) * limit

    base_url = f'https://gateway.marvel.com/v1/public/events?limit={limit}&offset={offset}'
    if search_query:
        base_url += f"&nameStartsWith={search_query}"

    auth_params = make_authorization()
    url = base_url + auth_params

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            events = data['data']['results']
            total = data['data']['total']
        else:
            print(f"Request error: {response.status_code}")
            events = []
            total = 0

    except requests.RequestException as exception:
        print(f"Request error: {exception}")
        events = []
        total = 0

    total_pages = (total + limit - 1) // limit
    start_page = max(page - 3, 1)
    end_page = min(page + 3, total_pages)
    page_range = range(start_page, end_page + 1)

    context = {
        'events': events,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'search_query': search_query
    }

    return render(request, 'base/events.html', context)


def event_detail(request, title):
    base_url = f'https://gateway.marvel.com/v1/public/events?name={title}'
    auth_params = make_authorization()
    url = base_url + auth_params

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            event = data['data']['results'][0] if data['data']['results'] else None
        else:
            print(f"Request error: {response.status_code}")
            event = None
    except requests.RequestException as exception:
        print(f"Request error: {exception}")
        event = None

    context = {
        'event': event,
    }

    return render(request, "base/event_detail.html", context)


def series_list(request):
    page = int(request.GET.get('page', 1))
    search_query = request.GET.get('search', '')
    limit = 20
    offset = (page - 1) * limit

    base_url = f'https://gateway.marvel.com/v1/public/series?limit={limit}&offset={offset}'
    if search_query:
        base_url += f"&nameStartsWith={search_query}"

    auth_params = make_authorization()
    url = base_url + auth_params

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            series = data['data']['results']
            total = data['data']['total']
        else:
            print(f"Request error: {response.status_code}")
            series = []
            total = 0

    except requests.RequestException as exception:
        print(f"Request error: {exception}")
        series = []
        total = 0

    total_pages = (total + limit - 1) // limit
    start_page = max(page - 3, 1)
    end_page = min(page + 3, total_pages)
    page_range = range(start_page, end_page + 1)

    for s in series:
        s['encoded'] = base64.urlsafe_b64encode(json.dumps(s).encode()).decode()

    context = {
        'series': series,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'search_query': search_query
    }

    return render(request, 'base/series.html', context)


def serie_detail(request):
    encoded_data = request.GET.get("data")
    serie = None

    if encoded_data:
        try:
            json_data = base64.urlsafe_b64decode(encoded_data).decode()
            serie = json.loads(json_data)
        except Exception as e:
            # print(f"Decode error: {e}")
            serie = None

    context = {
        'serie': serie,
    }

    return render(request, "base/serie_detail.html", context)


def stories_list(request):
    page = int(request.GET.get('page', 1))
    search_query = request.GET.get('search', '')
    limit = 20
    offset = (page - 1) * limit

    base_url = f'https://gateway.marvel.com/v1/public/stories?limit={limit}&offset={offset}'
    if search_query:
        base_url += f"&nameStartsWith={search_query}"

    auth_params = make_authorization()
    url = base_url + auth_params

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            stories = data['data']['results']
            total = data['data']['total']
        else:
            print(f"Request error: {response.status_code}")
            stories = []
            total = 0

    except requests.RequestException as exception:
        print(f"Request error: {exception}")
        stories = []
        total = 0

    total_pages = (total + limit - 1) // limit
    start_page = max(page - 3, 1)
    end_page = min(page + 3, total_pages)
    page_range = range(start_page, end_page + 1)

    context = {
        'stories': stories,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'search_query': search_query
    }

    return render(request, 'base/stories.html', context)




