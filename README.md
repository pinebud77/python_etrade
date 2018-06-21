python-etrade
=============

ha.. the verification bypass is not working. -_-;; the auth part is useless maybe..

This library is for the personal system trading implementation.

References :
* etrade API specification
* pyetrade at github

Implementation target :
* complete login/logout API
* accounts (partial) : list, status(?)
* trade (partial) : getting the current price, trade on market price

Done :
* complete login/logout API without WEB browser access for verficiation
* account : net_value, cash value available for trade, stock list
* quote : quote ask value
* stock : trade at market value

Required Libraries :
* requests
* requests_oauthlib
* fake_useragent
