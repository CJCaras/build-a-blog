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
import webapp2
import jinja2
import os

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

#First, set up the blog so that the new post form and the post listing are on the same page, as with AsciiChan,
# and then separate those portions into separate routes, handler classes, and templates.
#For now, when a user submits a new post, redirect them to the main blog page.


class Body(db.Model): #creates an entity that allows you to make a datatype with various properties
    subject = db.StringProperty(required = True) #String, float, integer properties
# (required = True) issues a constraint. So if someone submits to the DB without a title, it'll be an "exception".
#Constraints are good to prevent bad data.
    body = db.TextProperty(required = True)  # Can also use EmailProp.. Link... PostalAddress.. Text for longer strings.
    created = db.DateTimeProperty(auto_now_add = True) #date, time, DateTimeProperty... we chose the latter

#The /blog route displays the 5 most recent posts.
#To limit the displayed posts in this way, you'll need to filter the query results.

class MainPage(Handler):
    def render_front(self, subject="", body="", error=""):  #this function creates default text boxes
        bodies = db.GqlQuery("SELECT * FROM Body ORDER BY created DESC")
        self.render("mainblog.html", subject=subject, body=body, error=error, bodies=bodies)  #preserves user input

    def get(self):
        self.render_front()

    def post(self):
        subject = self.request.get("subject")
        body = self.request.get("body")

        if subject and body:
            p = Body(subject = subject, body = body)
            p.put()

            self.redirect("/blog")
        else:
            error = "We need both a title and body text!"
            self.render_front(subject, body, error)

class NewPost(Handler):

    def get(self):
        self.render_front()

    def post(self):
        self.redirect("/blog")

#You're able to submit a new post at the /newpost route/view.
#After submitting a new post, your app displays the main blog page.
#Note that, as with the AsciiChan example, you will likely need to refresh the main blog page to see your new post listed.

#If either title or body is left empty in the new post form, the form is rendered again,
#with a helpful error message and any previously-entered content in the same form inputs.

#form input boxes must have the names 'subject' and 'content' in order for the grading script to correctly post to them.

#To get the ID of an entity you just created: obj.key().id()

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/newpost', NewPost)
], debug=True)
