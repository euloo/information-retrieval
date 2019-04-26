from spyne import Application, rpc, ServiceBase, Unicode, Integer, Boolean
from lxml import etree
from spyne.protocol.soap import Soap11
from spyne.protocol.json import JsonDocument
from spyne.server.wsgi import WsgiApplication
from spyne.model.complex import ComplexModel, Array
import psycopg2
from psycopg2.extras import RealDictCursor
from spyne.const.http import HTTP_400, HTTP_401, HTTP_404, HTTP_405, HTTP_413, HTTP_500
from spyne.error import Fault, InternalError, ResourceNotFoundError, RequestTooLongError, RequestNotAllowed, InvalidCredentialsError, InvalidInputError

con_str=""""""

class Movie(ComplexModel):
    _type_info = {
        'id': Unicode,
        'title': Unicode,
    }

class Soap(ServiceBase):
    @rpc(_returns=Array(Movie))
    def get_movies(ctx):
        con = psycopg2.connect(con_str)
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""SELECT id, title FROM imdb_movies_api LIMIT 100""")
        res=cur.fetchall()
        cur.close()
        con.close()
        return res

    @rpc(Unicode, _returns=Array(Movie))    
    def get_movie(ctx, movie_id):
        con = psycopg2.connect(con_str)
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""SELECT id, title FROM imdb_movies_api WHERE id = %(movie_id)s""", {"movie_id":movie_id.zfill(7)})
        res=cur.fetchall()
        cur.close()
        con.close()
        if len(res) == 0:
            raise ResourceNotFoundError
        return res
    
    @rpc(Integer, Unicode, Unicode, _returns=Array(Movie)) 
    def get_movie_by(ctx, year, genre, director):
        query="""SELECT id, title FROM imdb_movies_api WHERE 1=1 """
        if year:
            query+="""AND year = %(year)s """
        if genre:
            query+="""AND %(genre)s = ANY(genres) """
        if director:
            query+="""AND %(director)s = ANY(directors) """
        if query == """SELECT * FROM imdb_movies_api WHERE 1=1 """:
            raise InvalidInputError
        
        con = psycopg2.connect(con_str)
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute(query+"""LIMIT 100""", {"year":year,
                                            "genre":genre,
                                            "director":director})
        res=cur.fetchall()
        cur.close()
        con.close()
        if len(res) == 0:
            raise ResourceNotFoundError
        return res
    
    @rpc(Unicode, Unicode, _returns=Movie)
    def add_movie(ctx, movie_id, title):
        con = psycopg2.connect(con_str)
        cur = con.cursor()
        
        cur.execute("""SELECT COUNT(*) FROM imdb_movies_api WHERE id = %(movie_id)s""",{"movie_id":movie_id})
        cnt=cur.fetchone()[0]
        if cnt > 0:
            raise InvalidInputError
    
        movie={
          "id": movie_id, 
          "title": title, 
        }
        
        for v in [('id',str),('title',str)]:
            if movie[v[0]] and not isinstance(movie[v[0]],v[1]):
                raise InvalidInputError
        
        cur.execute("""insert into imdb_movies_api (id, title) values (%(id)s, %(title)s)""", movie)
        con.commit()
        
        cur.close()    
        con.close()
    
        return movie
    
    @rpc(Unicode, Unicode, _returns=Movie)
    def update_movie(ctx, movie_id, title):
        con = psycopg2.connect(con_str)
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""SELECT id, title FROM imdb_movies_api WHERE id = %(movie_id)s""", {"movie_id":movie_id.zfill(7)})
        res=cur.fetchall()
        if len(res) == 0:
            raise ResourceNotFoundError
        movie={
          "id": movie_id, 
          "title": title if title else res[0]['title'], 
        }
        
        for v in [('id',str),('title',str)]:
            if movie[v[0]] and not isinstance(movie[v[0]],v[1]):
                raise InvalidInputError
        
        cur.execute("""update imdb_movies_api set title=%(title)s where id=%(id)s""", movie)
        con.commit()
        
        cur.close()
        con.close()
        return movie
    
    @rpc(Unicode, _returns=Boolean)
    def delete_movie(ctx, movie_id):
        con = psycopg2.connect(con_str)
        cur = con.cursor(cursor_factory=RealDictCursor)
        cur.execute("""SELECT id, title FROM imdb_movies_api WHERE id = %(movie_id)s""", {"movie_id":movie_id.zfill(7)})
        res=cur.fetchall()
        if len(res) == 0:
            raise ResourceNotFoundError
        
        cur.execute("""DELETE FROM imdb_movies_api WHERE id=%(movie_id)s""", {"movie_id":movie_id.zfill(7)})
        con.commit()
        
        cur.close()
        con.close()
        return True
    
    def fault_to_http_response_code(self, fault):
        if isinstance(fault, RequestTooLongError):
            return HTTP_413
        if isinstance(fault, ResourceNotFoundError):
            return HTTP_404
        if isinstance(fault, RequestNotAllowed):
            return HTTP_405
        if isinstance(fault, InvalidCredentialsError):
            return HTTP_401
        if isinstance(fault, InvalidInputError):
            return HTTP_400
        if isinstance(fault, Fault) and (fault.faultcode.startswith('Client.')
                                                or fault.faultcode == 'Client'):
            return HTTP_400
    
        return HTTP_500

app = Application([Soap], tns='Movie', 
                          in_protocol=Soap11(validator='lxml'),
                         out_protocol=Soap11())

application = WsgiApplication(app)
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 5000, application)
    server.serve_forever()