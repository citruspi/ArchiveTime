![](http://archiveteam.org/images/8/8a/Archivetime.png)

## Done Reading (Google Reader)

> Google Reader acts as a cache for RSS/Atom feed content, keeping deleted posts and deleted blogs accessible (if you can recreate the RSS/Atom feed URL). After the Reader shutdown, this data might still be available[1] via the Feeds API, but we'd like to grab most of this data before July 1 through the much more straightforward /reader/ API.

[Project Page](http://www.archiveteam.org/index.php?title=Google_Reader)

## Stack

- Beanstalkd
- MySQL
- Clients

## Dependencies

- MySQL-python==1.2.4
- PyYAML==3.10
- beanstalkc==0.3.0
- docopt==0.6.1
- peewee==2.1.2
- requests==1.2.3
- six==1.3.0
- termcolor==1.1.0
- wsgiref==0.1.2

Install with `pip`:

    $ pip install -r ../requirements.txt

## Configuration

Create `config.py` inside `./donereading`:

     tumblr = {
         'database': {
                         'host': '',
                         'database': '',
                         'username': '',
                         'password': ''
                    },
         'beanstalkd': {
                         'host': '',
                         'port': 11300,
                         'tube': ''
                      }   
     }

## Usage

### Archive

    $ python <service>.py archive --verbose

_Sample Output_

    (ArchiveTime)lemon:donereading mihir$ python tumblr.py archive --verbose

    ------------- ARCHIVE TIME! -------------

    [INDEXING] http://18thalleyway.tumblr.com
    [DISCOVERED] http://ianthony475.tumblr.com
    [ADDED] http://ianthony475.tumblr.com
    [DISCOVERED] http://vworp-goes-the-tardis.tumblr.com
    [ADDED] http://vworp-goes-the-tardis.tumblr.com
    [DISCOVERED] http://older-aang.tumblr.com
    [ADDED] http://older-aang.tumblr.com
    [DISCOVERED] http://64kbps.tumblr.com
    [ADDED] http://64kbps.tumblr.com
    [DISCOVERED] http://shalrath.tumblr.com
    [ADDED] http://shalrath.tumblr.com
    [DISCOVERED] http://londreaming.tumblr.com
    [ADDED] http://londreaming.tumblr.com
    [DISCOVERED] http://placentaandllamas.tumblr.com
    [ADDED] http://placentaandllamas.tumblr.com
    [DISCOVERED] http://isthisjustphantasy.tumblr.com
    [ADDED] http://isthisjustphantasy.tumblr.com
    [DISCOVERED] http://krabstickz.tumblr.com
    [ADDED] http://krabstickz.tumblr.com
    [DISCOVERED] http://chiakigrl.tumblr.com
    [ADDED] http://chiakigrl.tumblr.com
    [DISCOVERED] http://john-egbert.tumblr.com
    [ADDED] http://john-egbert.tumblr.com
    [DISCOVERED] http://winchestters.tumblr.com
    [ADDED] http://winchestters.tumblr.com
    [DISCOVERED] http://motherfuckingredranger.tumblr.com
    [ADDED] http://motherfuckingredranger.tumblr.com
    [DISCOVERED] http://ijustwanttowritestories.tumblr.com
    [ADDED] http://ijustwanttowritestories.tumblr.com
    [INDEXING] http://18thandhoyt.tumblr.com
    ...


### Export

Export all records:

    $ python <service>.py export
    
Only export records which have not been previously exported:

    $ python <service>.py export --new

This will write a list of usernames or URLS to a `.txt` file. It can be uploaded [here](http://allyourfeed.ludios.org:8080/index.html).


### Statistics

    $ python <service>.py statistics

_Sample Output_

    (ArchiveTime)lemon:donereading mihir$ python tumblr.py statistics

    ------------- ARCHIVE TIME! -------------

    78836 Queued Jobs
    85561 Recorded Blogs


## Getting Started

### Tumblr

The script requires a starting point - a page to get more pages from.

Manually push it into `Beanstalkd` tube before starting to archive:

    (ArchiveTime)lemon:donereading mihir$ python
    Python 2.7.2 (default, Jun 20 2012, 16:23:33) 
    [GCC 4.2.1 Compatible Apple Clang 4.0 (tags/Apple/clang-418.0.60)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.

    >>> import config
    >>>
    >>> beanstalk = beanstalkc.Connection(host=config.tumblr['beanstalks']['host'], port=config.tumblr['beanstalks']['port'])
    >>> beanstalk.use(config.tumblr['beanstalkd']['tube'])
    >>> beanstalk.watch(config.tumblr['beanstalkd']['tube'])
    >>> beanstalk.ignore('default')
    >>>
    >>> beanstalk.put('http://some-blog.tumblr.com')

The more you put into `Beanstalkd`, the more it has to work with - I put in 8,000+ blogs before starting the script.