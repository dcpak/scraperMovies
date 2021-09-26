import os
import re
import urllib.parse
import urllib.request

DIR_INPUT = 'm:\\downloads\\movies\\!wspolne\\'
TPL_LINK_SEARCH = 'https://www.filmweb.pl/search/live?q=<phrase/>'
TPL_LINK_MOVIE = 'https://www.filmweb.pl/film/<title/>-<year/>-<id/>'
MAX_COUNTER = 3

counter = 0
for _, dirs, _ in os.walk(DIR_INPUT):
    if dirs:
        for _dir in dirs:
            if counter < MAX_COUNTER:
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
                link_search = TPL_LINK_SEARCH.replace('<phrase/>', urllib.parse.quote_plus(name_movie))
                request_search = urllib.request.urlopen(link_search)
                response_search = str(request_search.read())
                result_search = response_search.split('\\\\c')
                if result_search[0] == 'b\'f' or result_search[0] == 'b"f':
                    link_movie = TPL_LINK_MOVIE\
                        .replace('<title/>', urllib.parse.quote_plus(result_search[3]))\
                        .replace('<year/>', urllib.parse.quote_plus(result_search[6]))\
                        .replace('<id/>', urllib.parse.quote_plus(result_search[1]))
                    print(name_movie, link_search, link_movie)
