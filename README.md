*Generate some shitty "limericks" where each line is a tweet.*

Like [this](http://pentametron.com/) and [this](http://bit.ly/11q0H8S) but
[limericks](http://en.wikipedia.org/wiki/Limerick_(poetry).

The code is written in Python and built on top of [redis](http://redis.io)
and [postgres](http://www.postgresql.org). To use it, check out the code,
set up a [virtual environment](http://www.virtualenv.org/) and then run:

```
pip install -r requirements.txt
```

The twitter scraper can be run with:

```
python twitter.py
```

Make sure that you have the right environment variables with all your Twitter
API settings. In another process, launch the parser (it uses Redis pubsub to
listen to the scraper):

```
python parse.py
```

This uses [NLTK](http://nltk.org/) to try and figure out the pronunciation of
the tweets and saves them to a Postgres database along with the number of
syllables and the last four phonemes. Finally, run the Flask app with:

```
python run_app.py
```
