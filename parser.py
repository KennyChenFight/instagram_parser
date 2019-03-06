import requests
import json
from pyquery import PyQuery as pq
from user import User
from post import Post
from datetime import datetime


def get_user_html(username):
    user_url = default_url + username + '/'
    response = requests.get(user_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        print('請求網頁失敗，網頁錯誤碼：', response.status_code)


def get_user_json_data(html):
    doc = pq(html)
    items = doc('script[type="text/javascript"]').items()

    json_data = {}
    for item in items:
        if item.text().strip().startswith('window._sharedData'):
            json_data = json.loads(item.text()[21:-1], encoding='utf-8')
            break
    return json_data
    # print(json.dumps(json_data, sort_keys=True, indent=4))


def get_user(json_data):
    profile_page = json_data['entry_data']['ProfilePage']
    user_data = profile_page[0]['graphql']['user']
    user_id = user_data['id']
    name = user_data['full_name']
    username = user_data['username']
    url = default_url + username + '/'
    is_private = int(user_data['is_private'])
    is_verified = int(user_data['is_verified'])
    picture = user_data['profile_pic_url_hd']
    biography = user_data['biography']
    followed_by_count = user_data['edge_followed_by']['count']
    follows_count = user_data['edge_follow']['count']
    media_count = user_data['edge_owner_to_timeline_media']['count']
    user = User(user_id, name, username, url, is_private, is_verified,
                picture, biography, followed_by_count,
                follows_count, media_count)

    posts = []
    edges = user_data['edge_owner_to_timeline_media']['edges']
    for edge in edges:
        node = edge['node']
        post_id = node['id']
        code = node['shortcode']
        url = default_url + 'p' + '/' + code + '/'
        caption = node['edge_media_to_caption']['edges'][0]['node']['text']
        has_location = node['location']
        location_id = None
        location_name = None
        if has_location is not None:
            location_id = node['location']['id']
            location_name = node['location']['name']
        time = node['taken_at_timestamp']
        time = datetime.utcfromtimestamp(time).strftime('%Y-%m-%d %H:%M:%S')
        display_src = node['display_url']
        thumbnail_src = node['thumbnail_src']
        comments = node['edge_media_to_comment']['count']
        likes = node['edge_media_preview_like']['count']
        is_video = node['is_video']
        video_views = None
        if is_video:
            video_views = node['video_view_count']
        owner_id = user_id

        post = Post(post_id, code, url, caption, location_id,
                    location_name, time, display_src,
                    thumbnail_src, comments, likes,
                    is_video, video_views, owner_id)
        posts.append(post)

    user.posts = posts
    has_next_page = user_data['edge_owner_to_timeline_media']['page_info']['has_next_page']
    return user, has_next_page

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/68.0.3440.106 Safari/537.36',
    'cookie': 'csrftoken=8cFvSiN8T85qMV0U6HKffJBOcrOUQEGj; ds_user_id=7183481074; fbm_124024574287414=base_domain=.instagram.com; fbsr_124024574287414=Cz-aJglbaAlEAZeubXrZtatwe_sR6CkrDCu5xNTnOhA.eyJjb2RlIjoiQVFCMGxzd0t2QkppNENaaTJEeGNoTkt6c0Zicmx5d0RDNVNSUFplWEhXMnROODB1LW5xLV8zSjBiQjRZR3otY2h6clhnTVVlcThiVjA1b0djN0pGSERnZFpIdDJ0TEFES0RScEJlUWc5dXNUY1JXVGQtM3JXSlBwVFY0cHRGWGt5cEI1WmNxXzNEZ1NXTldKUEZmVXdCWEM1LXlqLUt2XzhxdmstYnJsXzhraTFiTFNiT3NkVVRrTUh5NjNRR01wUzV5ekpvVlhDZVVsRzN5LXJOUEFBNkR4djV0enRxLXVXMG12OGg4UDBTaU5jbjVsVzEwWTR3NHhSV3o1bVNpWmMta01DNVFwbk1zLUhSbFc0MHROdS1scFd2dlo4M0pHQlRGZnRhZmx5N2NiTmFnbHFlc3hIc08zY1NOUzZ4R3NBZWVEUlZnVUs2cmM4dzQwdUxOZUdxVEkiLCJ1c2VyX2lkIjoiMTAwMDAzOTYzNTYyODQ5IiwiYWxnb3JpdGhtIjoiSE1BQy1TSEEyNTYiLCJpc3N1ZWRfYXQiOjE1NTE4NjAyNzh9; mid=XH8vBgAEAAGbodglGZDTGglydirv; rur=FTW; sessionid=7183481074%3A9BpYQvkvpXPJ7o%3A25; shbid=16206; shbts=1551844661.6233888; urlgen="{\"60.250.120.123\": 3462}:1h1RnN:11ixi9jUEMkFp-3pXuSThZYzB_A"'
}

default_url = 'https://www.instagram.com/'
username = input('please input username:')

user_html = get_user_html(username)
user_raw_json_data = get_user_json_data(user_html)
user, has_next_page = get_user(user_raw_json_data)

# test = requests.get('https://www.instagram.com/graphql/query/?query_hash=f2405b236d85e8296cf30347c9f08c2a&variables=%7B%22id%22%3A%22296074766%22%2C%22first%22%3A24%2C%22after%22%3A%22QVFBYWZPMDZnQlFybk5wbnIwUkNZSDdzME41R29SYVNCeWNKbHJkQUJueUEwOU16T0c2QUpDMWdYVHA3Z0puT040QnVIUThDaENGNGFqUEg1MHRNWVl3UQ%3D%3D%22%7D', headers=headers)
# print(test.text)


