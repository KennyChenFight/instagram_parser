class Post:

    def __init__(self, id, code, url, caption, location_id,
                 location_name, time, display_src,
                 thumbnail_src, comments, likes, video_views,
                 is_video, owner_id):
        self.id = id
        self.code = code
        self.url = url
        self.caption = caption
        self.location_id = location_id
        self.location_name = location_name
        self.time = time
        self.display_src = display_src
        self.thumbnail_src = thumbnail_src
        self.comments = comments
        self.likes = likes
        self.video_views = video_views
        self.is_video = is_video
        self.owner_id = owner_id
