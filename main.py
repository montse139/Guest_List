import os
import jinja2
import webapp2
from google.appengine.ext import ndb


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class Comment(ndb.Model):
    comment_name = ndb.StringProperty()
    comment_email = ndb.StringProperty()
    comment_text = ndb.StringProperty()


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class Guest(object):
    def __init__(self, name, email, text):
        self.name = name
        self.email = email
        self.text = text


class MainHandler(BaseHandler):
    def get(self):
        return self.render_template("hello.html")

    def post(self):
        text = self.request.get("text")
        if len(text) < 10:
            self.render_template("hello.html")
            self.write("OOps! You forgot to type your message")
        else:
            return self.render_template("guestbook.html")


class CommentListHandler(BaseHandler):
    def post(self):
        name = self.request.get("name")
        email = self.request.get("email")
        text = self.request.get("text")

        comment = Comment(comment_name=name, comment_email=email, comment_text=text)
        comment.put()


class GuestDetailsHandler(BaseHandler):
    def get(self):
        comments = Comment.query().fetch()
        params = {"comments": comments}
        return self.render_template("guest_list.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/comment_list', CommentListHandler),
    webapp2.Route('/guest_list/<guess_id:\d+>', GuestDetailsHandler)
], debug=True)# Guest_List
