## Lab 4
REST API

### get_movies() (GET)
Получить выборку из 100 случайных фильмов
~~~~
curl -i http://<HOST>:<PORT>/movies/api/imdb -u <USERNAME>:<PASSWORD>
~~~~

### get_movie(movie_id) (GET)
Получить фильм по id
~~~~
curl -i http://<HOST>:<PORT>/movies/api/imdb/<movie_id> -u <USERNAME>:<PASSWORD>
~~~~

### add_movie() (POST)
Добавить фильм
~~~~
curl -i -H "Content-Type: application/json" -X POST -d '{"id":"<movie_id>"[,"year":"<year>", "title":"<title>", "release_dates":"<release_dates>", "genres":"<genres>", "directors":"<directors>", "top_3_cast":"<top_3_cast>", "raiting":"<raiting>", "storyline":"<storyline>", "synopsis":"<synopsis>"]}' http://<HOST>:<PORT>/movies/api/imdb -u <USERNAME>:<PASSWORD>
~~~~

### update_movie(movie_id) (PUT)
Обновить информацию о фильме
~~~~
curl -i -H "Content-Type: application/json" -X PUT -d '{["year":"<year>", "title":"<title>", "release_dates":"<release_dates>", "genres":"<genres>", "directors":"<directors>", "top_3_cast":"<top_3_cast>", "raiting":"<raiting>", "storyline":"<storyline>", "synopsis":"<synopsis>"]}' http://<HOST>:<PORT>/movies/api/imdb/movie_id -u <USERNAME>:<PASSWORD>
~~~~

### delete_movie(movie_id) (DELETE)
Удалить фильм по id
~~~~
curl -i -X DELETE http://<HOST>:<PORT>/movies/api/imdb/<movie_id> -u <USERNAME>:<PASSWORD>
~~~~
