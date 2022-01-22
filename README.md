# Links

This is the software that helps run Cyberweekly.net.  It helps accumulate links from across the itnernet, allows you to comment on them, and then bind them together into a newsletter that can be sent out.

The code is all based around a fairly simplistic data model, and is currently hosted on Google Cloud Run for pennies per month.



## Data structures and workflow

### Link

This is a link, currently it is workflowed through as a single data object that changes state depending on whether it's unread and draft, read and queued for a newsletter, draft and included in a newsletter or live.

Links have a primary key that is a UUID4, but are almost always looked up by URL.  That means that while technically you could create multiple links for a single URL (for example, to feature a link a second time in a compilation newsletter), in reality, the code will likely break when you try to do it.

The aim behind that was to make it really easy when using the add link bookmark to reload the current comments for a link, and then edit them.

Underneath it all, a link consists of a URL, a Title, a Quote and a Note, along with some metadata such as time added, updated and so forth.

### Newsletter

This represents a single newsletter, which has a number of links associated with it.
The reference from link to newsletter is held in the link object, not in the newsletter. This was because the code was originally in AppEngine where queries are expensive and complex, so subselecting the links by newsletter id is quicker and more efficient. 
Now we've moved to Google's FireStore, which has subcollections, we could well refactor these.

A newsletter consists of a number (i.e. Newsletter 138), a title, an introduction (called a note originally), and some metadata.

A newsletter isn't strictly lifecycled itself, it's considered sent providing there is a sent date in the sent field.

## Running and debugging

Originally this ran locally really easily, but switching to using Google Auth for login has made things a bit more complex.

If you run this using gunicorn, then it will skip the main.py main section.  If you run python main.py, then the main section will disable authentication and then the code will run against an in-memory mock.

If you want to run it in a more integration manner, you can set the OAUTH_CLIENTID, OAUTH_CLIENTSECRET, GOOGLE_CLOUD_PROJECT and GOOGLE_APPLICATION_CREDENTIALS to whatever values you need, and then initialse a Google Firestore database, and it will run against that.  For login however, you'll need to work out how to present localhost over HTTPS, using something like Traefik and letsencrypt or similar.

To build the software, just run the build.sh, which should run the docker built command and create a tagged container called `links`.  Then you can run the software with debug.sh to run it locally.

Once you've got it running, you'll want some data.  using curl to hit http://localhost:8080/admin/admin/testdata will create a sample newsletter and 2 sample links.

Posting the `export` json file to http://localhost:8080/admin/import should import several hundred cyberweekly newsletters, and lots of local links and various things.

## Code layout

`main.py` has the main app setup, as well as the unauthenticated routes to handle the front page, and each public newsletter.
It defers to `handlers/` for all of the admin network routes, such as admin/index.

Each concept is theoretically separated, so link editing is in `handlers/links` and newsletter editing is in `handlers/newsletter`.

The specialist admin import and export functions are in `handlers/admin`.

Tempalte rendering is handled in `templates`, with the majority of templates inheriting from `templates/base.html` for admin pages, and `templates/front/base.html` for the unauthenticated main pages.