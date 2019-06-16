import pyatlasobscura as ao

destination = next(ao.destinations())
print(destination)

country = destination.countries[0]

place = next(country.places)
print(place.load())

print(place.categories)

royalty = [c for c in place.categories if c.name == "royalty"]

if not royalty:
    # As the atlas obscura data set changes,the example may not always work
    royalty = place.categories[0]

royalty = ao.search()

print(f"Category: '{royalty[0].name}'")

royal_attraction = next(royalty[0].places())

print(f"Attraction name: {royal_attraction.load().title}")
