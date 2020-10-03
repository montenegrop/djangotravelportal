import math
from core.utils import get_thumbnailer_
from django.urls import reverse
import os.path

def photo_to_json(request, response ,photos, limit_1, limit_2, ):
    photos_count = photos.count()
    page_count = math.ceil(photos_count / 21)
    photos_rest = photos[limit_1:limit_2]
    photos_json = []
    appended = 0

    for photo in photos_rest:
        if not photo.image:
            continue
        photo_json = {}
        photo_json['id'] = photo.id
        photo_json['get_description'] = photo.get_description()
        photo_json['image_url'] = photo.image.url
        if photo.country_index:
            photo_json['country_index'] = photo.country_index.name
        if photo.caption_slugged():
            photo_json['photo_url'] = request.build_absolute_uri(
                reverse('photos:photo', args=[photo.pk, photo.caption_slugged()]))
        else:
            photo_json['photo_url'] = request.build_absolute_uri(reverse('photos:photo', args=[photo.pk]))
        photo_json['kudu_count'] = photo.kudu_count
        photo_json['url'] = photo_json["photo_url"]
        if photo.caption:
            photo_json['title'] = photo.caption
        else:
            if photo.user:
                photo_by = photo.user.profile.screen_name
            else:
                photo_by = photo.tour_operator.name
            photo_json['title'] = "Photo by: " + photo_by
        photo_json['thumbnail_url'] = get_thumbnailer_(
            photo.image, 'crop_200')
        if os.path.exists(photo.image.path):
            photo_json['width'] = photo.image.width
            photo_json['height'] = photo.image.height
        else:
            photo_json['width'] = 0
            photo_json['height'] = 0
        if photo.tags.all():
            photo_json['animals'] = []
            for animal in photo.animals.all():
                photo_json['animals'].append(animal.name)
        photos_json.append(photo_json)
    response['photos_json'] = photos_json
    response['photos_count'] = photos_count
    response['page_count'] = page_count
    return response
