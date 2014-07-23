# BigLoad.R - for loading large amounts of twitter data into R
library(rjson)
tweets <- fromJSON(sprintf("[%s]", paste(readLines("data/tweets-large1.json"),collapse=",")))
coords <- sapply(tweets, function(x) x$coordinates$coordinates )
nuls <- sapply(coords, function(x) is.null(x)) # identify out the problematic NULL values
coords[nuls] <- lapply(coords[nuls], function(x) x <- c(0, 0))
coords <- matrix(unlist(coords, recursive = T), ncol = 2, byrow = T)
text <- sapply(tweets, function(x) x$text )
created <- strptime(sapply(tweets, function(x) x$created_at)
created <- strptime(created, "%a %b %d %H:%M:%S +0000 %Y") 
class(created)
plot(created, coords[,1])

t_out <- data.frame(text, lat = coords[,1], lon = coords[,2], created)

sel <- grepl("new house|new flat|moving house|move house|moving home|move home|#newhouse|#newflat|#movinghouse|#movehouse|#movinghome|#movehome", t.out$text, ignore.case = T )

write.csv(t_out[sel, ], "house_tweets.csv")
