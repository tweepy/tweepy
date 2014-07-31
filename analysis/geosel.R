# geographical selection - creation of geosel
# download.file(url = "http://hiking.waymarkedtrails.org/en/routebrowser/63872/gpx", "pennine.gpx")
library(rgdal)
ogrListLayers("pennine.gpx")
pw <- readOGR("pennine.gpx", layer = "tracks")
pw <- spTransform(pw, CRS("+init=epsg:27700")) # transform CRS to OSGB
library(rgeos)
geosel <- gBuffer(pw, width = 5000) # create buffer
plot(geosel) # plot to test dimensions make sense
geosel <- spTransform(geosel, CRS("+init=epsg:4326"))