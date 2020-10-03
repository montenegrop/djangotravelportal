import blurhash

hash = blurhash.encode('bin/image.jpg', x_components=4, y_components=3)
print(hash)
