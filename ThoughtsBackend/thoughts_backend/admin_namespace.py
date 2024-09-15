
import http.client

from flask_restx import Namespace, Resource

from .db import db
from .models import ThoughtModel

admin_namespace = Namespace("admin", description="Admin operations")

@admin_namespace.route("/thoughts/<int:thought_id>/")
class ThoughtsDelete(Resource):

    @admin_namespace.doc("delete_thought",
                         responses={http.client.NO_CONTENT: "No content"})
    def delete(self, thought_id):
        thought = ThoughtModel.query.get(thought_id)
        if not thought:
            return "", http.client.NO_CONTENT

        db.session.delete(thought)
        db.session.commit()

        return "", http.client.NO_CONTENT
