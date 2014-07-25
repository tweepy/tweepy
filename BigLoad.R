# BigLoad.R - for loading large amounts of twitter data into R

# Unzip the files saved by tweepy (see https://github.com/Robinlovelace/tweepy)
# Save to "unzipped" (e.g. with gunzip), load these files

library(rjson) # library used to load .json files
files <- list.files(path = "testload/", full.names=T)
# i <- files[1] # uncomment to load 1
for(i in files){
tweets <- fromJSON(sprintf("[%s]", paste(readLines(i, n=10), collapse=",")))
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

# sel <- grepl("new house|new flat|moving house|move house|moving home|move home|#newhouse|#newflat|#movinghouse|#movehouse|#movinghome|#movehome", t_out$text, ignore.case = T )
sel <- grepl("a", t_out$text, ignore.case = T )

t_out$filenum <- which(files == i)
write.csv(t_out[sel, ], file = paste0("output",which(files == i),".csv"))
}
