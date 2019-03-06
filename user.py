class User:

    def __init__(self, id, name, username, url, is_private,
                 is_verified, picture, biography,
                 followed_by_count, follows_count, media_count, posts=None):
        self.id = id
        self.name = name
        self.username = username
        self.url = url
        self.is_private = is_private
        self.is_verified = is_verified
        self.picture = picture
        self.biography = biography
        self.followed_by_count = followed_by_count
        self.follows_count = follows_count
        self.media_count = media_count
        self.posts = posts
