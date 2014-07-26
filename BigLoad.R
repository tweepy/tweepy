# BigLoad.R - for loading large amounts of twitter data into R

# Unzip the files saved by tweepy (see https://github.com/Robinlovelace/tweepy)
# If the files are too large, they may need splitting up:
getwd()
x <- list.files(path = "data/unzipped/", full.names = T, pattern = "json$")
i <- x[1]
start_time <- Sys.time()
for(i in x){
  mess <- paste0("split -l 10000 ", i, " split-", i)
  system(mess)
  print(x[i])
}
(split_time <- Sys.time() - start_time)
system("mkdir data/chunked") # copy chunked pieces into one directory


# Save to "unzipped" (e.g. with gunzip), load these files
library(rjson) # library used to load .json files
files <- list.files(path = "data/chunked/", full.names=T)
# i <- files[1] # uncomment to load 1
start_time <- Sys.time()
for(i in files){
# tweets <- fromJSON(sprintf("[%s]", paste(readLines(i, n=1000), collapse=","))) # test subset
tweets <- fromJSON(sprintf("[%s]", paste(readLines(i), collapse=","))) # full dataset
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

# sel <- grepl("new house|new flat|moving house|move house|moving home|move home|#newhouse|#newflat|#movinghouse|#movehouse|#movinghome|#movehome", t_out$text, ignore.case = T ) # original selection
# sel <- grepl("a", t_out$text, ignore.case = T ) # test selection - replace "a" with anything
sel <- grepl("new house|#newhouse|old house|#oldhouse|new home|#newhome|old home|#oldhome|new flat|#newflat|old flat|#oldflat|moving house|#movinghouse|move house|#movehouse|moving home|#movinghome|move home|#movehome|packing to move|packing up everything|unpacking everything|removals van|#packingtomove|#packingupeverything|#unpackingeverything|#removalsvan|bought a house|house bought|moved house|house sold|#boughtahouse|#housebought|#movedhouse|#housesold|first rent|#firstrent|new gaff|new housing|new accommodation|new crib|new bungalow|new apartment|new semi detached|new semi-detached|new detached|new cottage|new digs|new dwelling|new residence|new pad|new homes|new home's|new houses|new house's|#newgaff|#newhousing|#newaccommodation|#newcrib|#newbungalow|#newapartment|#newsemidetached|#newdetached|#newcottage|#newdigs|#newdwelling|#newresidence|#newpad|#newhomes|#newhouses|old gaff|old housing|old accommodation|old crib|old bungalow|old apartment|old semi detached|old semi-detached|old detached|old cottage|old digs|old dwelling|old residence|old pad|old homes|old home's|old houses|old house's|#oldgaff|#oldhousing|#oldaccommodation|#oldcrib|#oldbungalow|#oldapartment|#oldsemidetached|#olddetached|#oldcottage|#olddigs|#olddwelling|#oldresidence|#oldpad|#oldhomes|#oldhouses", t_out$text, ignore.case = T)

t_out$filenum <- which(files == i)
write.csv(t_out[sel, ], file = paste0("data/output",which(files == i),".csv"))
print(paste0(which(files == i) / length(files) * 100, "% done"))
}
end_time <- Sys.time()
(time_taken <- end_time - start_time) 
