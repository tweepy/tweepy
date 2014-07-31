library(rjson)
?fromJSON
timeline <- fromJSON(file="~/allLeeds.json" )
timeline[[2]]
timeline$retweeted

timelist=unlist(timeline)

tweets=timelist[names(timelist)=="text"]
names=timelist[names(timelist)=="user.screen_name"]
times=timelist[names(timelist)=="created_at"]

tweet.frame=data.frame(tweets,names,times) # only loaded 1 tweet!

# do it with RJsonLite
library(jsonlite)
timeline <- fromJSON("allLeeds2.json") # same issue: is it due to blank lines?
timeline

timeline <- fromJSON("allLeeds2NBRs.json") 


