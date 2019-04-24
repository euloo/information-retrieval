from flask import Flask, jsonify, abort, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
#from flask_httpauth import HTTPBasicAuth
import hashlib
import psycopg2
from psycopg2.extras import RealDictCursor

con_str=""""""

auth = HTTPBasicAuth()

app = Flask(__name__)

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad Request: '+str(error)}), 400)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(405)
def method_not_allowed(error):
    return make_response(jsonify({'error': 'Method Not Allowed'}), 405)

@auth.verify_password
def verify_password(username, password):
    if username == 'developer':
        m = hashlib.md5()
        m.update(password.encode())
        return m.hexdigest()=='b8b2f3f552b8ee1465ad4c30f466f51b'
    return None

@app.route('/movies/api/imdb', methods=['GET'])
@auth.login_required
def get_movies():
    con = psycopg2.connect(con_str)
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM imdb_movies_api ORDER BY random() LIMIT 100""")
    res=cur.fetchall()
    cur.close()
    con.close()
    return jsonify({'movies': res})

@app.route('/movies/api/imdb/<string:movie_id>', methods=['GET'])
@auth.login_required
def get_movie(movie_id):
    con = psycopg2.connect(con_str)
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM imdb_movies_api where id = %(movie_id)s""", {"movie_id":movie_id.zfill(7)})
    res=cur.fetchall()
    cur.close()
    con.close()
    if len(res) == 0:
        abort(404)
    return jsonify({'movie': res})

@app.route('/movies/api/imdb', methods=['POST'])
@auth.login_required
def add_movie():
    if not request.json or not 'id' in request.json:
        abort(400)
    con = psycopg2.connect(con_str)
    cur = con.cursor()
    
    cur.execute("""select count(*) from imdb_movies_api where id = %(movie_id)s""",{"movie_id":request.json['id']})
    cnt=cur.fetchone()[0]
    if cnt > 0:
        abort(400)

    movie={
      "id": request.json['id'], 
      "year": request.json.get('year'),
      "title": request.json.get('title'), 
      "release_dates": request.json.get('release_dates'), 
      "genres": request.json.get('genres'), 
      "directors": request.json.get('directors'), 
      "top_3_cast": request.json.get('top_3_cast'), 
      "raiting": request.json.get('raiting'), 
      "storyline": request.json.get('storyline'), 
      "synopsis": request.json.get('synopsis')
    }
    
    for v in [('id',str),('year',int),('title',str),('release_dates',list),
              ('genres',list),('directors',list),('top_3_cast',list),('raiting',int),
              ('storyline',str),('synopsis',str)]:
        if movie[v[0]] and not isinstance(movie[v[0]],v[1]):
            abort(400)
    
    cur.execute("""insert into imdb_movies_api 
                values (%(id)s, %(year)s, %(title)s, %(release_dates)s,
                %(genres)s, %(directors)s, %(top_3_cast)s, %(raiting)s, 
                 %(storyline)s, %(synopsis)s)""", movie)
    con.commit()
    
    cur.close()    
    con.close()

    return jsonify({'movie': movie}), 201

@app.route('/movies/api/imdb/<string:movie_id>', methods=['PUT'])
@auth.login_required
def update_movie(movie_id):
    if not request.json:
        abort(400)
    con = psycopg2.connect(con_str)
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM imdb_movies_api where id = %(movie_id)s""", {"movie_id":movie_id.zfill(7)})
    res=cur.fetchall()
    if len(res) == 0:
        abort(404)
    movie={
      "id": movie_id, 
      "year": request.json.get('year',res[0]['year']),
      "title": request.json.get('title',res[0]['title']), 
      "release_dates": request.json.get('release_dates',res[0]['release_dates']), 
      "genres": request.json.get('genres',res[0]['genres']), 
      "directors": request.json.get('directors',res[0]['directors']), 
      "top_3_cast": request.json.get('top_3_cast',res[0]['top_3_cast']), 
      "raiting": request.json.get('raiting',res[0]['raiting']), 
      "storyline": request.json.get('storyline',res[0]['storyline']), 
      "synopsis": request.json.get('synopsis',res[0]['synopsis'])
    }
    
    for v in [('id',str),('year',int),('title',str),('release_dates',list),
              ('genres',list),('directors',list),('top_3_cast',list),
              ('raiting',int),('storyline',str),('synopsis',str)]:
        if movie[v[0]] and not isinstance(movie[v[0]],v[1]):
            abort(400)
    
    cur.execute("""update imdb_movies_api set
                year=%(year)s, title=%(title)s, 
                release_dates=%(release_dates)s,genres=%(genres)s, 
                directors=%(directors)s, top_3_cast=%(top_3_cast)s, 
                raiting=%(raiting)s, storyline=%(storyline)s,
                synopsis=%(synopsis)s where id=%(id)s""", movie)
    con.commit()
    
    cur.close()
    con.close()
    return jsonify({'movie': movie})

@app.route('/movies/api/imdb/<string:movie_id>', methods=['DELETE'])
@auth.login_required
def delete_task(movie_id):
    con = psycopg2.connect(con_str)
    cur = con.cursor(cursor_factory=RealDictCursor)
    cur.execute("""SELECT * FROM imdb_movies_api where id = %(movie_id)s""", {"movie_id":movie_id.zfill(7)})
    res=cur.fetchall()
    if len(res) == 0:
        abort(404)
    
    cur.execute("""delete from imdb_movies_api where id=%(movie_id)s""", {"movie_id":movie_id.zfill(7)})
    con.commit()
    
    cur.close()
    con.close()
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)