# BigLoad.R - for loading large amounts of twitter data into R

# Unzip the files saved by tweepy (see https://github.com/Robinlovelace/tweepy)
# Save to "unzipped" (e.g. with gunzip), load these files

library(rjson) # library used to load .json files
files <- list.files(path = "testload/", full.names=T)
for(i in files){
tweets <- fromJSON(sprintf("[%s]", paste(readLines(i, n=10), collapse=",")))
coords <- sapply(tweets, function(x) x$coordinates$coordinates )
nuls <- sapply(coords, function(x) is.null(x)) # identify out the problematic NULL values
coords[nuls] <- lapply(coords[nuls], function(x) x <- c(0, 0)) # convert to zeros to keep with unlist
coords <- matrix(unlist(coords, recursive = T), ncol = 2, byrow = T)
text <- sapply(tweets, function(x) x$text )
created <- sapply(tweets, function(x) x$created_at)
created <- strptime(created, "%a %b %d %H:%M:%S +0000 %Y") 

t_out <- data.frame(text, lat = coords[,2], lon = coords[,1], created)

# sel <- grepl("new house|new flat|moving house|move house|moving home|move home|#newhouse|#newflat|#movinghouse|#movehouse|#movinghome|#movehome", t_out$text, ignore.case = T )
sel <- grepl("a", t_out$text, ignore.case = T )

t_out$filenum <- which(files == i)
write.csv(t_out[sel, ], file = paste0("output",which(files == i),".csv"))
}
