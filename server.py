from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import gridfs
import socket
import base64

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://mongo:27017/dev"
mongo = PyMongo(app)
db = mongo.db
fs = gridfs.GridFS(db)
     
@app.route('/')
def index():
    '''
    Index page of server.
    Shows diagnostic message about pod in which it is running.
    Parameters:
        None
    '''
    hostname = socket.gethostname()
    return jsonify(
        message="Book storage is running inside {} pod".format(hostname)
    )

@app.route('/books')
def show_all_contents():
    '''
    API to show all books in database by default.
    It also can filter books if filters are not blank.
    Parameters:
        None
    '''
    name_filt = request.args.getlist('name[]')
    author_filt = request.args.getlist('author[]')
    genre_filt = request.args.getlist('genre[]')
    publisher_filt = request.args.getlist('publisher[]')
    date_of_death_filt = request.args.getlist('date_of_death[]')

    filter = {}
    if len(name_filt) > 0: filter['name'] = {'$in': name_filt}
    if len(author_filt) > 0:  filter['author'] = {'$in': author_filt}
    if len(genre_filt) > 0: filter['genre'] = {'$in': genre_filt}
    if len(publisher_filt) > 0:  filter['publisher'] = {'$in': publisher_filt}
    if len(date_of_death_filt) > 0:
        _death_filter = {'date_of_death': {'$in': date_of_death_filt}}
        _authors = db.authors.find(_death_filter)
        filter['date_of_death'] = {'$in': _authors['name'].values()}

    _books = db.books.find(filter)

    if not _books:
        return jsonify(
            status=False,
            data=None
        ), 500

    item = {}
    data = []
    for book in _books:
        item = {
            '_id': str(book['_id']),
            'name': book['name'],
            'author': book['author'],
            'year': book['year'],
            'genre': book['genre'],
            'pages': book['pages'],
            'publisher': book['publisher']
        }
        data.append(item)

    return jsonify(
        status=True,
        data=data
    ), 200

@app.route('/books/<id>')
def show_one_book(id):
    '''
    API to show one books with full information about book and author.
    Parameters:
        id - id of book.
    '''
    _book = db.books.find_one({'_id': ObjectId(id)})

    if not _book:
        return jsonify(
            status=False,
            data=None
        ), 500

    _author = db.authors.find_one({'name': _book['author']})

    if not _author:
        return jsonify(
            status=False,
            data=None
        ), 500

    item = {}
    data = []
    item = {
        '_id': str(_book['_id']),
        'name': _book['name'],
        'author': _book['author'],
        'author_description': _author['description'],
        'author_date_of_birth': _author['date_of_birth'],
        'author_date_of_death': _author['date_of_death'],
        'year': _book['year'],
        'genre': _book['genre'],
        'pages': _book['pages'],
        'publisher': _book['publisher']
    }
    data.append(item)

    return jsonify(
        status=True,
        data=data
    ), 200

@app.route('/books/<id>/download')
def download_book(id):
    '''
    API to download book pdf by id.
    Parameters:
        id - id of book to download.
    '''
    _book = db.books.find_one({'_id': ObjectId(id)})

    if not _book:
        return jsonify(
            status=False,
            data=None
        ), 500

    pdf_encoded = fs.get(_book['_id'])
    if not pdf_encoded:
        return jsonify(
            status=False,
            data=None
        ), 500

    pdf_decoded = base64.b64decode(pdf_encoded)

    return jsonify(
        status=True,
        data=pdf_decoded
    ), 200
  
@app.route('/add_book', methods=['POST'])
def add_book():
    '''
    API to add one book to database.
    Parameters:
        None
    POST request uses JSON with structure:
        name: name of the book
        author: book's author
        year: year of publishing (only numerical values)
        genre: book's genre
        pages: number of book's pages (only numerical values)
        publisher: book's publisher
        pdf_document: pdf version of the book (optional)
    '''
    data = request.get_json(force=True)

    if not data['year'].isnumeric() or not data['pages'].isnumeric():
        return jsonify(
            status=False,
            data=None
        ), 400

    item = {
        'name': data['name'],
        'author': data['author'],
        'year': data['year'],
        'genre': data['genre'],
        'pages': data['pages'],
        'publisher': data['publisher']
    }

    db.books.insert_one(item)

    if 'pdf_document' in request.files:
        pdf_document = request.files['pdf_document']
        pdf_document_encoded = base64.b64encode(pdf_document)
        fs.put(pdf_document_encoded, _id=db.books.find_one(item)['_id'])
        mongo.save_file(pdf_document.filename, pdf_document_encoded)
        item['pdf_document_name'] = pdf_document.filename

    return jsonify(
        status=True,
        message='Book saved successfully!'
    ), 200

@app.route('/add_author', methods=['POST'])
def add_author():
    '''
    API to add one author.
    POST request uses JSON with structure:
        name: author's name
        description: short description of author
        date_of_birth: author's birth date (only numerical)
        date_of_death: author's death date (only numerical)
    Parameters:
        None
    '''
    data = request.get_json(force=True)

    if not data['date_of_birth'].isnumeric() or not data['date_of_death'].isnumeric():
        return jsonify(
            status=False,
            data=None
        ), 400

    item = {
        'name': data['name'],
        'description': data['description'],
        'date_of_birth': data['date_of_birth'],
        'date_of_death': data['date_of_death'],
    }

    db.authors.insert_one(item)

    return jsonify(
        status=True,
        message='Author saved successfully!'
    ), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)