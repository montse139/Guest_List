import os
import jinja2
import webapp2
from google.appengine.ext import ndb
from google.appengine.api import users


class Comment(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    text = ndb.StringProperty()


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


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
        user = users.get_current_user()

        if user:
            logged_in = True
            logout_url = users.create_logout_url('/')

            params = {"logged_in": logged_in, "logout_url": logout_url, "user": user}
        else:
            logged_in = False
            login_url = users.create_login_url('/')

            params = {"logged_in": logged_in, "login_url": login_url, "user": user}

        return self.render_template("hello.html", params)

    def post(self):
        name = self.request.get("name")
        text = self.request.get("text")

        if len(text) <= 5:
            self.write("OOps! You forgot to type your message")
            self.render_template("hello.html")
            return

        user = users.get_current_user()
        email = user.email()
        comment = Comment(name=name, email=email, text=text)
        comment.put()
        comments = Comment.query().fetch()
        params = {"comments": comments}
        return self.render_template("guest_list.html", params=params)


class CommentListHandler(BaseHandler):
    def get(self):
        comments = Comment.query().fetch()
        params = {"comments": comments}
        return self.render_template("guestbook.html", params=params)


class GuestDetailsHandler(BaseHandler):
    def get(self):
        comments = Comment.query().fetch()
        params = {"comments": comments}
        return self.render_template("guest_list.html", params=params)


class EditCommentHandler(BaseHandler):
    def get(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        params = {"comment": comment}
        return self.render_template("comment_edit.html", params=params)

    def post(self, comment_id):
        new_name = self.request.get("name")
        new_email = self.request.get("email")
        new_text = self.request.get("text")
        comment = Comment.get_by_id(int(comment_id))
        comment.text = new_text
        comment.put()
        return self.redirect_to("guest_list.html")


class DeleteCommentHandler(BaseHandler):
    def get(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        params = {"comment": comment}
        return self.render_template("comment_delete.html", params=params)

    def post(self, comment_id):
        comment = Comment.get_by_id(int(comment_id))
        comment.key.delete()
        return self.redirect_to("list")

app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler),
    webapp2.Route('/comment_list', CommentListHandler),
    webapp2.Route('/guest_list', GuestDetailsHandler, name="list"),
    webapp2.Route('/guest_list/<comment_id:\d+>/edit', EditCommentHandler),
    webapp2.Route('/guest_list/<comment_id:\d+>/delete', DeleteCommentHandler)
], debug=True)# Guest_List
