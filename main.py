#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2, jinja2, os, cgi, re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

#value of the blog's parent, giving a key for an element that doesn't exist
def blog_key(name = 'default'):
    return db.Key.from_path('blogs', name)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Body(db.Model): #creates an entity that allows you to make a datatype with various properties
    subject = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True) #date, time, DateTimeProperty... we chose the latter
#Other allowed properties: Float, Boolean, Integer, Email, Link, PostalAddress
# (required = True) issues a constraint. So if someone submits to the DB without a title, it'll be an "exception".
#Constraints are good to prevent bad data.

#The following function was in Udacity solution, but did not make
#one iota of difference in my blog:
    #def render(self):
        #self._render_text = self.content.replace('\n', '<br>')
        #return render_str("post.html", p = self)

class MainPage(Handler):

    def render_front(self):
        bodies = db.GqlQuery("SELECT * FROM Body ORDER BY created DESC").fetch(limit = 5)
        self.render("mainblog.html", bodies = bodies)

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            p = Body(parent = blog_key(), subject = subject, body = content)
            p.put()
            blog_id = p.key().id()
            self.redirect("/blog")
            #self.redirect("/blog/%s" % str(blog_id))
        else:
            error = "We need both a title and body text!"
            self.render("newpost.html", subject=subject, content=content, error=error)

class CreatePost(Handler):
    def render_front(self, subject="", content="", error=""):  #this function creates default text boxes
        self.render("newpost.html", subject=subject, content=content, error=error)  #preserves user input

    def get(self):
        self.render_front()

class PermaHandler(Handler):
    def get(self, blog_id):
        key = db.Key.from_path('Body', int(blog_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.render("no_blog.html")
            return

        self.render("blogpost.html", post = post)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', CreatePost),
    #(r'/blog/(\d+)', PermaHandler)#, #A regex, anything in the parenthesis
    #will be passed as a parameter for the get or post function for PermaHandler
    webapp2.Route(r'/blog/<blog_id:\d+>', PermaHandler)
], debug=True)
