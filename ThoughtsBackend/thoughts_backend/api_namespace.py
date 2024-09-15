
import http.client
from datetime import datetime, timezone

from flask import abort
from flask_restx import Namespace, Resource, fields

from . import config
from .db import db
from .models import ThoughtModel
from .token_validation import validate_token_header

api_namespace = Namespace("api", description="API operations")

def authentication_header_parser(value):
    username = validate_token_header(value, config.PUBLIC_KEY)
    if username is None:
        abort(401)
    return username

authentication_parser = api_namespace.parser()
authentication_parser.add_argument("Authorization", location="headers",
                                   type=str,
                                   help="Bearer Access Token")

thought_parser = authentication_parser.copy()
thought_parser.add_argument("text", type=str, required=True,
                            help="Text of the thought")

model = {
    "id": fields.Integer(),
    "username": fields.String(),
    "text": fields.String(),
    "timestamp": fields.DateTime(),
}
thought_model = api_namespace.model("Thought", model)


@api_namespace.route("/me/thoughts/")
class MeThoughtListCreate(Resource):
    @api_namespace.doc("list_thoughts")
    @api_namespace.expect(authentication_parser)
    @api_namespace.marshal_with(thought_model, as_list=True)
    def get(self):
        args = authentication_parser.parse_args()
        username = authentication_header_parser(args["Authorization"])

        thoughts = (ThoughtModel
                    .query
                    .filter(ThoughtModel.username == username)
                    .order_by("id")
                    .all())
        return thoughts

    @api_namespace.doc("create_thoughts")
    @api_namespace.expect(thought_parser)
    @api_namespace.marshal_with(thought_model, code=http.client.CREATED)
    def post(self):
        args = thought_parser.parse_args()
        username = authentication_header_parser(args["Authorization"])

        new_thought = ThoughtModel(username=username,
                                    text=args["text"],
                                    timestamp=datetime.now(timezone.utc))
        db.session.add(new_thought)
        db.session.commit()

        result = api_namespace.marshal(new_thought, thought_model)

        return result, http.client.CREATED

search_parser = api_namespace.parser()
search_parser.add_argument("search", type=str, required=False,
                           help="Search in the text of the thoughts")

@api_namespace.route("/thoughts/")
class ThoughtList(Resource):

    @api_namespace.doc("list_thoughts")
    @api_namespace.marshal_with(thought_model, as_list=True)
    @api_namespace.expect(search_parser)
    def get(self):
        args = search_parser.parse_args()
        search_param = args["search"]
        query = ThoughtModel.query
        if search_param:
            param = f"%{search_param}%"
            query = (query.filter(ThoughtModel.text.ilike(param)))

        query = query.order_by("id")
        thoughts = query.all()

        return thoughts


@api_namespace.route("/thoughts/<int:thought_id>/")
class ThoughtsRetrieve(Resource):

    @api_namespace.doc("retrieve_thought")
    @api_namespace.marshal_with(thought_model)
    def get(self, thought_id):
        thought = ThoughtModel.query.get(thought_id)
        if not thought:
            return "", http.client.NOT_FOUND

        return thought
