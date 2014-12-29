from goose import Goose


class GooseAPI:
    def __init__(self, url):
        self.url = url
        self.goose = Goose()
        self.article = None

    def extract(self):
        self.article = self.goose.extract(url=self.url)
        return {
            'title': self.article.title,
            'summary': self.article.meta_description,
            'content': self.article.cleaned_text,
            'published_at': self.article.publish_date,
            'opengraph': self.article.opengraph,
            'authors': self.article.authors,
            'links': self.article.links,
            'image': self.images(),
            'movies': self.movies(),
            'tweets': self.article.tweets,
            'tags': list(self.article.tags),
        }

    def movies(self):
        movies = []
        for movie in self.article.movies:
            movies.append({
                'embed_type': movie.embed_type,
                'provider': movie.embed_type,
                'width': movie.width,
                'height': movie.height,
                'embed_code': movie.embed_code,
                'src': movie.src,
            })
        return movies

    def images(self):
        images = []
        if self.article.top_image:
            images.append({
                'url': self.article.top_image.src,
                'width': self.article.top_image.width,
                'height': self.article.top_image.height,
                'type': 'image'
            })
        return images
