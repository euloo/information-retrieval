# Contributors

[Комлева Юлия](https://github.com/euloo), [Никитина Наталья](https://github.com/Nicklausse), [Габдулханов Марсель](https://github.com/gabmars)

# Files descriptions

**[imdb_spider/spiders/imdb.py](imdb_spider/spiders/imdb.py) - краулер imdb.com (основной)**

**[imdb_spider/spiders/kinopoisk.py](imdb_spider/spiders/kinopoisk.py) - краулер kinopoisk.ru (основной)**

[imdb_spider](imdb_spider) - директория Scrapy-проекта, включающая конфигурационные файлы и классы краулеров

[imdb_res.py](imdb_res.py) - скрипт загрузки результатов парсинга в базу данных

[kinopoisk_id_crawler.py](kinopoisk_id_crawler.py) - извлекатель идентификаторов фильмов с kinopoisk.ru, с помощью поиска по названию

[test_imdb.py](test_imdb.py) - тестовый краулер imdb.com

[test_kinopoisk.py](test_kinopoisk.py) - тестовый краулер kinopoisk.ru

[proxies.py](proxies.py) - скрипт собирающий прокси с помощью асинхронного модуля proxybroker

[fill_proxies.py](fill_proxies.py) - скрипт валидации прокси на выбранном ресурсе

[imdb_parallel.py](imdb_parallel.py) - тестовый мультпроцессный парсер imdb.com с прокруткой прокси
