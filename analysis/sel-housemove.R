# Extract text strings
sel <- grepl("new house|new flat|moving house|move house|moving home|move home|#newhouse|#newflat|#movinghouse|#movehouse|#movinghome|#movehome", t.out$text, ignore.case = T )
summary(sel)
t.out[sel,]
