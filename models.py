
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# TODO: connect to a local postgresql database- DONE

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='venue', lazy=True)
    upcoming_shows = db.Column(db.ARRAY(db.String()))
    past_shows = db.Column(db.ARRAY(db.String()))
    past_shows_count = db.Column(db.Integer)
    upcoming_shows_count = db.Column(db.Integer)

    @property
    def search_term(self):
        return {
            'id': self.id,
            'name': self.name,
            'num_upcoming_shows': self.upcoming_shows_count
        }
        
    def __repr__(self):
        return '<Venue {}>'.format(self.name)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate-DONE


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', backref='artist', lazy=True)
    
    @property
    def search_term(self):
        return {
            'id': self.id,
            'name': self.name,
        }
        
    def __repr__(self):
        return '<Artist {}>'.format(self.name)

# TODO: implement any missing fields, as a database migration using Flask-Migrate-DONE
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.-DONE


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    artist_name = db.Column(db.String(120))
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    venue_name = db.Column(db.String(120))
    artist_image_link = db.Column(db.String(500))
    start_time = db.Column(db.DateTime)

    def __repr__(self):
        return '<Show {}>'.format(self.artist_id, self.venue_id)


# db.create_all()