# Contributors

Комлева Юлия, Никитина Наталья, [Габдулханов Марсель](https://github.com/gabmars)

# Files descriptions

**[imdb_spider/spiders/imdb.py](imdb_spider/spiders/imdb.py) - краулер imdb.com (основной)**

**[imdb_spider/spiders/kinopoisk.py](imdb_spider/spiders/kinopoisk.py) - краулер kinopoisk.ru (основной)**

[imdb_spider](imdb_spider) - директория Scrapy-проекта, включающая конфигурационные файлы и классы краулеров

[test_imdb.py](test_imdb.py) - тестовый краулер imdb.com

[test_kinopoisk.py](test_kinopoisk.py) - тестовый краулер kinopoisk.ru

[proxies.py](proxies.py) - скрипт собирающий прокси с помощью асинхронного модуля proxybroker

[fill_proxies.py](fill_proxies.py) - скрипт валидации прокси на выбранном ресурсе

[imdb_parallel.py](imdb_parallel.py) - тестовый мультпроцессный парсер imdb.com с прокруткой прокси
