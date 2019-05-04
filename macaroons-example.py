from pymacaroons import Macaroon, Verifier

# Keys for signing macaroons are associated with some identifier for later
# verification. This could be stored in a database, key value store,
# memory, etc.
keys = {
    'key-for-bob': 'asdfasdfas-a-very-secret-signing-key'
}

# Construct a Macaroon. The location and identifier will be visible after
# construction, and identify which service and key to use to verify it.
m = Macaroon(
    location='cool-picture-service.example.com',
    identifier='key-for-bob',
    key=keys['key-for-bob']
)

# Add a caveat for the target service
m.add_first_party_caveat('picture_id = bobs_cool_cat.jpg')

# Inspect Macaroon (useful for debugging)
print(m.inspect())
# location cool-picture-service.example.com
# identifier key-for-bob
# cid picture_id = bobs_cool_cat.jpg
# signature 83d8fa280b09938d3cffe045634f544ffaf712ff2c51ac34828ae8a42b277f8f

# Serialize for transport in a cookie, url, OAuth token, etc
serialized = m.serialize()

print(serialized)
# MDAyZWxvY2F0aW9uIGNvb2wtcGljdHVyZS1zZXJ2aWNlLmV4YW1wbGUuY29tCjAwMWJpZGVudGlmaWVyIGtleS1mb3ItYm9iCjAwMjdjaWQgcGljdHVyZV9pZCA9IGJvYnNfY29vbF9jYXQuanBnCjAwMmZzaWduYXR1cmUgg9j6KAsJk408_-BFY09UT_r3Ev8sUaw0goropCsnf48K

n = Macaroon.deserialize("MDAyZWxvY2F0aW9uIGNvb2wtcGljdHVyZS1zZXJ2aWNlLmV4YW1wbGUuY29tCjAwMWJpZGVudGlmaWVyIGtleS1mb3ItYm9iCjAwMjdjaWQgcGljdHVyZV9pZCA9IGJvYnNfY29vbF9jYXQuanBnCjAwMmZzaWduYXR1cmUgg9j6KAsJk408_-BFY09UT_r3Ev8sUaw0goropCsnf48K")

v = Verifier()

# General caveats are verified by arbitrary functions
# that return True only if the caveat is understood and met
def picture_access_validator(predicate):
    # in this case, predicate = 'picture_id = bobs_cool_cat.jpg'
    if predicate.split(' = ')[0] != 'picture_id':
        return False
    return predicate.split(' = ')[1] == 'bobs_cool_cat.jpg'

# The verifier is informed of all relevant contextual information needed
# to verify incoming macaroons
v.satisfy_general(picture_access_validator)

# Note that in this case, the picture_access_validator() is just checking
# equality. This is equivalent to a satisfy_exact call, which just checks for
# string equality
v.satisfy_exact('picture_id = bobs_cool_cat.jpg')

# Verify the macaroon using the key matching the macaroon identifier
verified = v.verify(
    n,
    keys[n.identifier]
)

# if verified is True, the macaroon was untampered (signatures matched) AND
# all caveats were met
