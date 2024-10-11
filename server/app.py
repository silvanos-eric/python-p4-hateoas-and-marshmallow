#!/usr/bin/env python3

from flask import Flask, make_response, request
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import Newsletter, db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)


# Schemas
class NewsletterSchema(ma.SQLAlchemySchema):

    class Meta:
        model = Newsletter
        load_instance = True

    id = ma.auto_field()
    title = ma.auto_field()
    body = ma.auto_field()
    published_at = ma.auto_field()

    # HATEOAS links
    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('newsletterbyid', values=dict(id='<id>')),
            'method': 'GET'
        },
        'update': {
            'href': ma.URLFor('newsletterbyid', values=dict(id='<id>')),
            'method': 'PATCH'
        },
        'delete': {
            'href': ma.URLFor('newsletterbyid', values=dict(id='<id>')),
            'method': 'DELETE'
        },
        'collection': {
            'href': ma.URLFor('newsletters'),
            'method': 'GET'
        }
    })


class NewsletterSummarySchema(ma.SQLAlchemySchema):

    class Meta:
        model = Newsletter
        load_instance = True

    id = ma.auto_field()
    title = ma.auto_field()
    published_at = ma.auto_field()

    # Only summary fields and a self-link
    _links = ma.Hyperlinks({
        'self': {
            'href': ma.URLFor('newsletterbyid', values=dict(id='<id>'))
        }
    })


newsletter_schema = NewsletterSchema()
newsletters_summary_schema = NewsletterSummarySchema(many=True)


# Resources
class Index(Resource):

    def get(self):

        response_dict = {
            "index": "Welcome to the Newsletter RESTful API",
        }

        response = make_response(
            response_dict,
            200,
        )

        return response


api.add_resource(Index, '/')


class Newsletters(Resource):

    def get(self):
        newsletters = Newsletter.query.all()

        newsletters_json = newsletters_summary_schema.dump(newsletters)
        return newsletters_json

    def post(self):
        new_record = Newsletter(
            title=request.form['title'],
            body=request.form['body'],
        )
        db.session.add(new_record)
        db.session.commit()

        new_record_json = newsletter_schema.dump(new_record)
        return new_record_json, 201


api.add_resource(Newsletters, '/newsletters')


class NewsletterByID(Resource):

    def get(self, id):

        newsletter = db.session.get(Newsletter, id)

        newsletter_json = newsletter_schema.dump(newsletter)
        return newsletter_json

    def patch(self, id):

        newsletter = db.session.get(Newsletter, id)
        for attr in request.form:
            setattr(newsletter, attr, request.form[attr])

        db.session.add(newsletter)
        db.session.commit()

        newsletter_json = newsletter_schema.dump(newsletter)

        return newsletter_json

    def delete(self, id):

        newsletter = db.session.get(Newsletter, id)

        db.session.delete(newsletter)
        db.session.commit()

        return {"message": "record successfully deleted"}


api.add_resource(NewsletterByID, '/newsletters/<int:id>')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
