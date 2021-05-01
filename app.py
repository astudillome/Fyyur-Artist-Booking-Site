#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
from sqlalchemy.sql.expression import null
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import distinct
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import sys
# import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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


db.create_all()

# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    artists = Artist.query.order_by(Artist.id.desc()).limit(5).all()
    venues = Venue.query.order_by(Venue.id.desc()).limit(5).all()
    return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.-DONE
    # num_shows should be aggregated based on number of upcoming shows per venue.
    area_data = db.session.query(Venue.city, Venue.state).distinct(
        Venue.city, Venue.state).order_by('state').all()
    data = []
    for area in area_data:
        venues = Venue.query.filter_by(state=area.state).filter_by(
            city=area.city).order_by('name').all()
        venue_data = []
        data.append({
            'city': area.city,
            'state': area.state,
            'venues': venue_data
        })
        for venue in venues:
            shows = Show.query.filter_by(
                venue_id=venue.id).order_by('id').all()
            venue_data.append({
                'id': venue.id,
                'name': venue.name,
            })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike("%" + search_term + "%")).all()
    venues_data=[]

    for venue in venues:
      venues_data.append(venue.search_term)
    
    response = {
        "count": len(venues),
        "data": venues_data
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id-DONE
    # TODO: replace with real venue data from the venues table, using venue_id-DONE
    venue = Venue.query.filter_by(id=venue_id).first()
    shows = Show.query.filter_by(venue_id=venue_id).all()
    past_shows = []
    upcoming_shows = []
    for show in shows:
        artist = Artist.query.filter_by(id=show.artist_id).first()
        show_detail = {
            "artist_id": show.artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(show.start_time)
        }

        if (show.start_time < datetime.now()):
            past_shows.append(show_detail)
        else:
            upcoming_shows.append(show_detail)
    venue_data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website_link,
        "facebook_link": venue.facebook_link,
        "image_link": venue.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres')
        facebook_link = request.form.get('facebook_link')
        image_link = request.form.get('image_link')
        website_link = request.form.get('website_link')
        seeking_talent = True if "seeking_talent" in request.form else False
        seeking_description = request.form.get('seeking_description')

        venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, facebook_link=facebook_link,
                      image_link=image_link, website_link=website_link, seeking_talent=seeking_talent, seeking_description=seeking_description)

        db.session.add(venue)
        db.session.commit()
        flash(f"Venue {name} was successfully listed!")
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(f"An error occurred. Venue {name} could not be listed.")
    finally:
        db.session.close()

    # TODO: insert form data as a new Venue record in the db, instead- DONE
    # TODO: modify data to be the data object returned from db insertion- DONE

    # on successful db insert, flash success
    # flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.-DONE
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.route('/venues<int:venue_id>', methods=['POST'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using-DONE
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        db.session.delete(venue)
        db.session.commit()
        flash(f"Successfully deleted.")
        return render_template('pages/home.html')
    except:
        db.session.rollback()
        flash(f"An error occurred, {venue.name} could not be deleted.")
    finally:
        db.session.close()

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that-DONE
    # clicking that button delete it from the db then redirect the user to the homepage-DONE
    return None

#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database-DONE
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.-DONE
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term')
    artists = Artist.query.filter(Artist.name.ilike("%" + search_term + "%")).all()
    artists_data=[]

    for artist in artists:
      artists_data.append(artist.search_term)
    
    response={
      "count": len(artists),
      "data": artists_data
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id-DONE
    artist=Artist.query.filter_by(id=artist_id).first()
    return render_template('pages/show_artist.html', artist=artist)

#  Update
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist=Artist.query.filter_by(id=artist_id).first()
    form=ArtistForm(obj=artist)
    # TODO: populate form with fields from artist with ID <artist_id>-DONE
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing-DONE
    # artist record with ID <artist_id> using the new attributes
    id=artist_id
    artist=Artist.query.get(id)
    try:
        artist.name=request.form.get('name')
        artist.city=request.form.get('city')
        artist.state=request.form.get('state')
        artist.address=request.form.get('address')
        artist.phone=request.form.get('phone')
        artist.genres=request.form.getlist('genres')
        artist.facebook_link=request.form.get('facebook_link')
        artist.image_link=request.form.get('image_link')
        artist.website_link=request.form.get('website_link')
        artist.seeking_venue=True if "seeking_venue" in request.form else False
        artist.seeking_description=request.form.get('seeking_description')
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        print(e)
    finally:
        db.session.close()
    return redirect(url_for('show_artist', artist_id=artist_id))


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue=Venue.query.filter_by(id=venue_id).first()
    form=VenueForm(obj=venue)

    # TODO: populate form with values from venue with ID <venue_id>-DONE
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing-DONE
    id=venue_id
    venue=Venue.query.get(id)
    try:
        venue.name=request.form.get('name')
        venue.city=request.form.get('city')
        venue.state=request.form.get('state')
        venue.address=request.form.get('address')
        venue.phone=request.form.get('phone')
        venue.genres=request.form.getlist('genres')
        venue.facebook_link=request.form.get('facebook_link')
        venue.image_link=request.form.get('image_link')
        venue.website_link=request.form.get('website_link')
        venue.seeking_talent=True if "seeking_talent" in request.form else False
        venue.seeking_description=request.form.get('seeking_description')
        db.session.commit()
    except ValueError as e:
        db.session.rollback()
        print(e)
    finally:
        db.session.close()
    # venue record with ID <venue_id> using the new attributes
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form=ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Artist record in the db, instead-DONE
    # TODO: modify data to be the data object returned from db insertion-DONE
    try:
        name=request.form.get('name')
        city=request.form.get('city')
        state=request.form.get('state')
        phone=request.form.get('phone')
        genres=request.form.getlist('genres')
        website=request.form.get('website_link')
        image_link=request.form.get('image_link')
        facebook_link=request.form.get('facebook_link')
        seeking_venue=True if "seeking_venue" in request.form else False
        seeking_description=request.form.get('seeking_description')

        artist=Artist(name=name, city=city, state=state, phone=phone, genres=genres, website=website, image_link=image_link,
                        facebook_link=facebook_link, seeking_venue=seeking_venue, seeking_description=seeking_description)

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + name + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + name + ' could not be listed.')
    finally:
        db.session.close()

    # TODO: on unsuccessful db insert, flash an error instead.-DONE
    # on successful db insert, flash success
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@ app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.-DONE
    # num_shows should be aggregated based on number of upcoming shows per venue.

    shows=Show.query.all()
    shows_data=[]
    
    for show in shows:
          show_details={
          "venue_id": show.venue_id,
          "venue_name": show.venue_name,
          "artist_id": show.artist_id,
          "artist_name": show.artist_name,
          "artist_image_link": show.artist_image_link,
          "start_time": str(show.start_time)
          }
          shows_data.append(show_details)
    return render_template('pages/shows.html', shows=shows_data)


@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form=ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead-DONE
    try:
        artist_id=request.form.get('artist_id')
        artist_name=Artist.query.filter_by(id=artist_id).first().name
        artist_image_link=Artist.query.filter_by(
            id=artist_id).first().image_link
        venue_id=request.form.get('venue_id')
        venue_name=Venue.query.filter_by(id=venue_id).first().name
        start_time=request.form.get('start_time')
        print(artist_name)

        show=Show(artist_id=artist_id, artist_name=artist_name, artist_image_link=artist_image_link,
                    venue_id=venue_id, venue_name=venue_name, start_time=start_time)

        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.-DONE
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler=FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''