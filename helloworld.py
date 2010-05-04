import cgi
import os

import hashlib
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

class Greeting(db.Model):
    author   = db.UserProperty()
    content  = db.StringProperty(multiline=True)
    date     = db.DateTimeProperty(auto_now_add=True)
    gravatar = db.StringProperty()
    image    = db.BlobProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        greetings_query = Greeting.all().order('-date')
        greetings = greetings_query.fetch(10)

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        template_values = {
                'greetings': greetings,
                'url': url,
                'url_linktext': url_linktext,
                }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

class Guestbook(webapp.RequestHandler):
    def post(self):
        greeting = Greeting()

        if users.get_current_user():
            greeting.author = users.get_current_user()
            greeting.gravatar = 'http://www.gravatar.com/avatar/'
            greeting.gravatar += hashlib.md5(greeting.author.email().lower()).hexdigest()
        else:
            greeting.gravatar = 'http://www.gravatar.com/avatar/b48def645758b95537d4424c84d1a9ff'

        greeting.content = self.request.get('content')
        uploaded_file = self.request.get('img')
        greeting.image = db.Blob(uploaded_file)
        greeting.put()
        self.redirect('/')

class Image(webapp.RequestHandler):
    def get(self):
        greeting = db.get(self.request.get("img_id"))
        if greeting.image:
            self.response.headers['Content-Type'] = "image/png"
            self.response.out.write(greeting.image)
        else:
            self.error(404)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/img', Image),
                                      ('/sign', Guestbook)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
