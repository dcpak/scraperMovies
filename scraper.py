import codecs
import hashlib
import os
import re
import urllib.parse
import urllib.request

DIR_INPUT = 'm:\\downloads\\movies\\'

TPL_LINK_SEARCH_LIVE = 'https://www.filmweb.pl/search/live?q=<phrase/>'
TPL_LINK_SEARCH = 'https://www.filmweb.pl/search?q=<phrase/>'
TPL_LINK_MOVIE = 'https://www.filmweb.pl/film/<title/>-<year/>-<id/>'

TPL_DESCRIPTION_START = '<span itemprop="description">'
TPL_MOVIE = '<div class="movie">' \
            '<div class="image"><image/></div>' \
            '<a  href="<linkSearch/>" target="_blank" class="nameMovie"><nameMovie/></a>' \
            '<a href="<linkMovie/>" target="_blank" class="title"><title/></a>' \
            '<div class="year"><year/></div>' \
            '<div class="description"><description/></div>' \
            '<div class="counter"><counter/></div>' \
            '</div>\n'
TPL_IMAGE = '<img src="https://fwcdn.pl/fpo<image/>" />'

DIR_CACHE_SEARCH = 'cache/search/'
DIR_CACHE_MOVIE = 'cache/movie/'

FILE_OUTPUT_TPL = 'template.html'
FILE_OUTPUT = 'movies_information.html'

MAX_COUNTER = 0

counter = 0
content_file = ''
for _, dirs, _ in os.walk(DIR_INPUT):
    if dirs:
        for _dir in dirs:
            if MAX_COUNTER == 0 or counter < MAX_COUNTER:
                counter += 1
                name_movie = re.sub('(^ +)|( +$)',
                                    '',
                                    re.sub(' +',
                                           ' ',
                                           re.sub('\[[^]]*]',
                                                  '',
                                                  re.sub('\([^)]*\)',
                                                         '',
                                                         _dir)
                                                  )
                                           )
                                    )
                if name_movie[0] != '!':
                    hash_name_movie = hashlib.md5(name_movie.encode('utf-8')).hexdigest()
                    try:
                        with codecs.open(DIR_CACHE_SEARCH + hash_name_movie, 'r', 'utf-8') as file:
                            response_search = file.read()
                    except FileNotFoundError:
                        link_search = TPL_LINK_SEARCH_LIVE.replace('<phrase/>', urllib.parse.quote_plus(name_movie))
                        with urllib.request.urlopen(link_search) as request:
                            response_search = request.read().decode('utf-8')
                        with codecs.open(DIR_CACHE_SEARCH + hash_name_movie, 'w', 'utf-8') as file:
                            file.write(response_search)
                    result_search = response_search.split('\\c')

                    if result_search[0] == 'f':
                        link_movie = TPL_LINK_MOVIE \
                            .replace('<title/>', urllib.parse.quote_plus(result_search[3])) \
                            .replace('<year/>', urllib.parse.quote_plus(result_search[6])) \
                            .replace('<id/>', urllib.parse.quote_plus(result_search[1]))
                        try:
                            with codecs.open(DIR_CACHE_MOVIE + hash_name_movie, 'r', 'utf-8') as file:
                                response_movie = file.read()
                        except FileNotFoundError:
                            try:
                                with urllib.request.urlopen(link_movie) as request:
                                    response_movie = request.read().decode('utf-8')
                                with codecs.open(DIR_CACHE_MOVIE + hash_name_movie, 'w', 'utf-8-sig') as file:
                                    file.write(response_movie)
                            except Exception:
                                print(link_movie)
                        movie = {
                            'title': result_search[3],
                            'year': result_search[6],
                            'image': '',
                            'description': ''
                        }
                        if result_search[2]:
                            movie['image'] = TPL_IMAGE.replace('<image/>', result_search[2])
                        match_description = re.search(TPL_DESCRIPTION_START + '[^<]*', response_movie)
                        if match_description:
                            movie['description'] = response_movie[match_description.start() + len(
                                TPL_DESCRIPTION_START): match_description.end()]
                        content_file += TPL_MOVIE\
                            .replace('<nameMovie/>', name_movie)\
                            .replace('<title/>', movie['title'])\
                            .replace('<year/>', movie['year'])\
                            .replace('<image/>', movie['image'])\
                            .replace('<description/>', movie['description'])\
                            .replace('<linkMovie/>', link_movie)\
                            .replace('<counter/>', str(counter))\
                            .replace('<linkSearch/>', TPL_LINK_SEARCH.replace('<phrase/>', urllib.parse.quote_plus(name_movie)))
with codecs.open(FILE_OUTPUT_TPL, 'r', 'utf-8') as file:
    tpl_file_output = file.read()
    with codecs.open(FILE_OUTPUT, 'w', 'utf-8-sig') as file:
        file.write(tpl_file_output.replace('<content/>', content_file))
