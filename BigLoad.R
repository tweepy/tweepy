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

# sel <- grepl("a", t_out$text, ignore.case = T ) # test selection

t_out$filenum <- which(files == i)
write.csv(t_out[sel, ], file = paste0("data/output",which(files == i),".csv"))
print(paste0(which(files == i) / length(files) * 100, "% done"))
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
write.csv(output, "output.csv")
