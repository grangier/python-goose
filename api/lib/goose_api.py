from goose import Goose


class GooseAPI:
    def __init__(self, url):
        self.url = url
        self.goose = Goose()
        self.extracted_content = None

    def extract(self):
        self.extracted_content = self.goose.extract(url = self.url)
        return {
            'title': self.extracted_content.title,
            'summary': self.extracted_content.meta_description,
            'content': self.extracted_content.content_html,
            'published_at': self.extracted_content.publish_date,
            'assets': self.images()
        }

    def images(self):
        images = []
        for image in self.extracted_content.images:
            images.append({
                'url': image.src,
                'width': image.width,
                'height': image.height,
                'type': 'image'
            })
        return images
