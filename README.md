# Links

This is the software that helps run [Cyberweekly.net](https://cyberweekly.net).  It helps accumulate links from across the internet, allows you to comment on them, and then bind them together into a newsletter that can be sent out.

The code is all based around a fairly simplistic data model, and is currently hosted on Google Cloud Run for pennies per month.

## Running and debugging

I've done everything I can to make this possible to run locally, but Google's API's are a bit of a pain for that.  The `debug.sh` and `run.sh` scripts should use docker to run the container, which can be built using `build.sh`.  

The debug script will mount the local directory over the top of the python code, so local modifications should be applied over the top of the container, but the run script doesn't do that, so if you have local modifications, you must run `build.sh` before using `run.sh` otherwise it won't have your changes.

Furthermore, debug.sh attempts to mock out the Google firestore with an in-memory, non-persistant version.  If you have an `export.json` file in the root of the local directory, it will load it on startup, so you'll have data available.

Running it locally requires you to point the code at a live Google Firestore using environment variables to provide access to `GOOGLE_APPLICATION_CREDENTIALS`, `OAUTH_CLIENTID`, `OAUTH_CLIENTSECRET`, `GOOGLE_CLOUD_PROJECT` and critically `OAUTH_CALLBACK`.

The hardest part about running it locally is Google's OAuth system, and that's the trickiest bit to debug or play with.  Google requires that you register your app with a callback URL, and their servers will send you back to the appropriate OAUTH_CALLLBACK location.  But that location must be hosted on a server that has TLS, so you'll need to setup something to front the TLS certificate to the browser.

Once you've got it running, you'll want some data.  using curl to hit http://localhost:8080/admin/admin/testdata will create a sample newsletter and 2 sample links.

Posting the `export` json file to http://localhost:8080/admin/import should import several hundred cyberweekly newsletters, and lots of local links and various things.

## Code layout

`main.py` has the main app setup, as well as the unauthenticated routes to handle the front page, and each public newsletter.
It defers to `handlers/` for all of the admin network routes, such as admin/index.

Each concept is theoretically separated, so link editing is in `handlers/links` and newsletter editing is in `handlers/newsletter`.

The specialist admin import and export functions are in `handlers/admin`.

Template rendering is handled in `templates`, with the majority of templates inheriting from `templates/base.html` for admin pages, and `templates/front/base.html` for the unauthenticated main pages.

The Data system is divided into services, repositories and the data model.

Each data object should ideally be pretty dumb, there's calculations and data fields, but no business logic in there.

For querying, creating, updating and deleting, all requests should go to the repository for the data object, so `repositories/links_repo.py`.

For business logic, such as launching a newsletter, queuing a link etc, all requests should go to the service, so `services/links_service.py`.

## Data structures and workflow

### Link

Found in /models/link.py

This is a link, currently it is workflowed through as a single data object that changes state depending on whether it's unread and draft, read and queued for a newsletter, draft and included in a newsletter or live.

Links have a primary key that is a UUID4, but are almost always looked up by URL.  That means that while technically you could create multiple links for a single URL (for example, to feature a link a second time in a compilation newsletter), in reality, the code will likely break when you try to do that.

The aim behind that was to make it really easy when using the add link bookmark to reload the current comments for a link, and then edit them.

Underneath it all, a link consists of a URL, a Title, a Quote and a Note, along with some metadata such as time added, updated and so forth.

### Newsletter

Found in /models/newsletter.py

This represents a single newsletter, which has a number of links associated with it.

The reference from link to newsletter is held in the link object, not in the newsletter. This was because the code was originally in AppEngine where queries are expensive and complex, so subselecting the links by newsletter id is quicker and more efficient. 

Now we've moved to Google's FireStore, which has subcollections, we could well refactor these.

A newsletter consists of a number (i.e. Newsletter 138), a title, an introduction (called a note originally), and some metadata.

A newsletter isn't strictly lifecycled itself, it's considered sent providing there is a sent date in the sent field.