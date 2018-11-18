import pyatlasobscura as ao

destination = next(ao.destinations())
print(destination)

country = destination.countries[0]

place = next(country.places)
print(place)

print(place.categories)

films = [c for c in place.categories if c['name'] == 'rocks']

print(films[0])

film_attraction = next(films[0].places())

print(film_attraction.load())
