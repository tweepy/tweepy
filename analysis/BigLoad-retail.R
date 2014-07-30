# retail tweets - people who visit stores

# source("analysis/geosel.R")
library(rgdal)
pw <- readOGR("data/", "study-area")
pw <- spTransform(pw, CRS("+init=epsg:27700")) # transform CRS to OSGB
library(rgeos)
geosel <- spTransform(pw, CRS("+init=epsg:4326"))

# Setup
library(rjson) # library used to load .json files
files <- list.files(path = "data/chunked/", full.names=T)
# i <- files[1] # uncomment to load 1
start_time <- Sys.time()
nlines <- 0

for(i in files){
# tweets <- fromJSON(sprintf("[%s]", paste(readLines(i, n=1000), collapse=","))) # test subset
  tryCatch({
    tweets <- fromJSON(sprintf("[%s]", paste(readLines(i), collapse=","))) # full dataset
  }, error=function(e){paste0("Error ", which(i == files))})
  
coords <- sapply(tweets, function(x) x$coordinates$coordinates )
nuls <- sapply(coords, function(x) is.null(x)) # identify out the problematic NULL values
coords[nuls] <- lapply(coords[nuls], function(x) x <- c(0, 0)) # convert to zeros to keep with unlist
coords <- matrix(unlist(coords, recursive = T), ncol = 2, byrow = T)
text <- sapply(tweets, function(x) x$text )
created <- sapply(tweets, function(x) x$created_at)
created <- strptime(created, "%a %b %d %H:%M:%S +0000 %Y")
language <- sapply(tweets, function(x) x$lang )
n_followers <- sapply(tweets, function(x) x$lang )
user_created <- sapply(tweets, function(x) x$user$created_at)
n_tweets <- sapply(tweets, function(x) x$user$statuses_count)
n_followers <- sapply(tweets, function(x) x$user$followers_count)
n_following <- sapply(tweets, function(x) x$user$friends_count)
user_location <- sapply(tweets, function(x) x$user$location)
user_description <- sapply(tweets, function(x) x$user$description)
user_id <- sapply(tweets, function(x) x$user$id)
user_idstr <- sapply(tweets, function(x) x$user$id_str)
user_name <- sapply(tweets, function(x) x$user$name)
user_screen_name <- sapply(tweets, function(x) x$user$screen_name)

t_out <- data.frame(text, lat = coords[,2], lon = coords[,1], created,
  language, n_followers, user_created, n_tweets, n_followers, n_following,
  user_location)

### geo selection part
geoT <- SpatialPointsDataFrame(coords= matrix(c(t_out$lon, t_out$lat), ncol=2), data=t_out)
proj4string(geoT) <- CRS("+init=epsg:4326")
t_out <- geoT[geosel, ]@data
sel <- grepl("shop|buy|bought|expensive|cheap|bargain|store|visit", geoT$text, ignore.case = T ) # selection

t_sel <- t_out[sel, ])

t_out$filenum <- which(files == i)
write.csv(t_sel, file = paste0("data/output",which(files == i),".csv"))
print(paste0(which(files == i) / length(files) * 100, "% done"))
nlines <- nlines + nrow(t_out)
}

end_time <- Sys.time()
(time_taken <- end_time - start_time) 

outs <- list.files(path = "data/", pattern=".csv", full.names=T)
output <- read.csv(outs[1])
for(j in outs[-1]){
  tryCatch({
  output <- rbind(output, read.csv(j))
  }, error=function(e){paste0("Error ", which(outs == j))})
  num <- which(outs == j)
}
summary(output)
write.csv(output, "output-pennine.csv")
