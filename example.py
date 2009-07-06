from api import API

# Create API object
api = API()

# Fetch public timeline
p_timeline = api.public_timeline()

# Print texts of statuses
for status in p_timeline:
  print status.text
