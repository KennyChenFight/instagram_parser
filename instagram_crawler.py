import requests
import json
from pyquery import PyQuery as pq
from user import User
from post import Post
from message import Message
from datetime import datetime
import time
import random


class InstagramCrawler:
    user_agents = [
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
        'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'
    ]

    headers = {
        'user-agent': ''
    }
    default_url = 'https://www.instagram.com/'
    default_post_url = 'https://www.instagram.com/graphql/query/?query_hash=f2405b236d85e8296cf30347c9f08c2a&'
    default_message_url = 'https://www.instagram.com/graphql/query/?query_hash=477b65a610463740ccdb83135b2014db&variables=%7B%22shortcode%22%3A%22'

    def __init__(self, username, cookie):
        self.username = username
        self.cookie = cookie
        self.headers['cookie'] = cookie

    def parse_user(self):
        response = self.get_user_html()
        if response is not None:
            json_data = self.get_user_json_data(response)
            user = self.get_user(json_data)
            return user
        else:
            return None

    def parse_posts(self, user):
        edges = user.edges
        posts = self.get_one_loop_posts(edges, user.id)

        # 代表貼文超過12篇，每一次循環爬取12篇文
        while True:
            global has_next_page
            has_next_page = user.has_next_page
            global end_cursor
            if has_next_page:
                end_cursor = user.end_cursor
                url = self.get_next_post_url(end_cursor, user.id)
                response = self.get_next_post_json_data(url)
                if response is not None:
                    response = json.loads(response, encoding='utf-8')
                    edges = response['data']['user']['edge_owner_to_timeline_media']['edges']
                    next_posts = self.get_one_loop_posts(edges, user.id)
                    has_next_page = response['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']
                    end_cursor = response['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
                    posts.extend(next_posts)
                    time.sleep(random.randint(0, 5))
                else:
                    break
            else:
                break
        user.posts = posts
        print('貼文全部爬取完畢,共爬取了', len(user.posts), '篇文')
        return user

    def get_user_html(self):
        user_url = self.default_url + self.username + '/'
        response = requests.get(user_url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            print('請求網頁失敗，網頁錯誤碼：', response.status_code)
            return None

    def get_user_json_data(self, response):
        doc = pq(response)
        items = doc('script[type="text/javascript"]').items()

        json_data = {}
        for item in items:
            if item.text().strip().startswith('window._sharedData'):
                json_data = json.loads(item.text()[21:-1], encoding='utf-8')
                break
        return json_data

    def get_user(self, json_data):
        profile_page = json_data['entry_data']['ProfilePage']
        user_data = profile_page[0]['graphql']['user']
        user_id = user_data['id']
        name = user_data['full_name']
        username = user_data['username']
        url = self.default_url + username + '/'
        is_private = int(user_data['is_private'])
        is_verified = int(user_data['is_verified'])
        picture = user_data['profile_pic_url_hd']
        biography = user_data['biography']
        followed_by_count = user_data['edge_followed_by']['count']
        follows_count = user_data['edge_follow']['count']
        media_count = user_data['edge_owner_to_timeline_media']['count']
        has_next_page = user_data['edge_owner_to_timeline_media']['page_info']['has_next_page']
        if has_next_page:
            end_cursor = user_data['edge_owner_to_timeline_media']['page_info']['end_cursor'][:-2]
        else:
            end_cursor = None
        edges = user_data['edge_owner_to_timeline_media']['edges']

        user = User(user_id, name, username, url, is_private, is_verified,
                    picture, biography, followed_by_count,
                    follows_count, media_count, has_next_page, end_cursor, edges)
        return user

    def get_next_post_url(self, end_cursor, user_id):
        id = user_id
        # 最高一次可取50篇文，預設一次取12篇文
        first = '12'
        after = end_cursor
        variebles = 'variables=%7B%22id%22%3A%22' + id + '%22%2C%22first%22%3A' + first + '%2C%22after%22%3A%22' + after + '%3D%3D%22%7D'
        url = self.default_post_url + variebles
        return url

    def get_next_post_json_data(self, url):
        try:
            self.headers['user-agent'] = random.choice(self.user_agents)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            else:
                print('請求postApi，錯誤碼：', response.status_code)
                return None
        except:
            print('Connection Error')
            return None

    def get_one_loop_posts(self, edges, user_id):
        posts = []

        # 最多12貼文
        for edge in edges:
            node = edge['node']
            post_id = node['id']
            code = node['shortcode']
            url = self.default_url + 'p' + '/' + code + '/'
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

            messages = self.get_post_message(code)
            post = Post(post_id, code, url, caption, location_id,
                        location_name, time, display_src,
                        thumbnail_src, comments, likes,
                        is_video, video_views, owner_id, messages)
            posts.append(post)
        print('已爬取', len(posts), '篇貼文')
        return posts

    def get_post_message(self, code):
        url = self.default_message_url + code + '%22%2C%22child_comment_count%22%3A3%2C%22fetch_comment_count%22%3A40%2C%22parent_comment_count%22%3A24%2C%22has_threaded_comments%22%3Afalse%7D'
        response = json.loads(self.get_message_json_data(url), encoding='utf-8')
        edges = response['data']['shortcode_media']['edge_media_to_comment']['edges']

        messages = []
        for edge in edges:
            node = edge['node']
            id = node['owner']['id']
            username = node['owner']['username']
            text = node['text']
            created_at = node['created_at']
            message = Message(id, username, text, created_at)
            messages.append(message)
        return messages

    def get_message_json_data(self, url):
        try:
            self.headers['user-agent'] = random.choice(self.user_agents)
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response.text
            else:
                print('請求MessageApi失敗，錯誤碼:' + response.status_code)
                return None
        except:
            print('Connection Error')
            return None







