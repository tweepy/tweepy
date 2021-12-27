    '''Okay,so the API allows a maximum of 1000 items or 50 pages. That's where the issue is coming from. It's more like a limitation.
     You either have just work with what you have but if you wanna have fun coding

     I think maybe the best way around it would be to use a function
      ( that iterrates through the first 1000 items, 
      and break out of the function) 
      run the function again but iterating from the 1000th item to the 2000th. And so forth
      Maybe try the python NEXT function'''

    with open('temp_users.json', 'w') as f:
        all_data = []
        print "Searching users",
        for user in tweepy.Cursor(api.search_users,q = "ziemniaki").items():
            print ".",
            sys.stdout.flush()
            all_data.append(user._json)
        f.write(json.dumps(all_data))
        f.close()
    print ""
    return


# DONE
