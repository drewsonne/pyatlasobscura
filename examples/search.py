import pyatlasobscura as ao

nearby = ao.search(
    location=(51.5287718, -0.2416798)
).places()  # Find nearby places to London

place = next(nearby)

print(place.load())
