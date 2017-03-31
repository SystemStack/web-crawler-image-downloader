"""Reporting subsystem for web crawler."""
import time

class Stats:
    """Record stats of various sorts."""
    def __init__(self):
        self.stats = {}

    def add(self, key, count=1):
        self.table.tabularize_reporting(key, (self.stats.get(key, 0) + count))
        self.stats[key] = self.stats.get(key, 0) + count

    def report(self, table=None):
        self.table = table
        for key, count in sorted(self.stats.items()):
            print('%10d' % count, key)

def report(crawler, table=None):
    """Print a report on all completed URLs."""
    t1 = crawler.t1 or time.time()
    dt = t1 - crawler.t0
    if dt and crawler.max_tasks:
        speed = len(crawler.done) / dt / crawler.max_tasks
    else:
        speed = 0
    stats = Stats()
    stats.table = table
    try:
        show = list(crawler.done)
        show.sort(key=lambda _stat: _stat.url)
        for stat in show:
            url_report(stat, stats, table)
    except KeyboardInterrupt:
        table.tabularize_reporting("GIGO", "Interrupted")

    print('Finished', len(crawler.done),
          'urls in %.3f secs' % dt,
          '(max_tasks=%d)' % crawler.max_tasks,
          '(%.3f urls/sec/task)' % speed)

def url_report(stat, stats, table=None):
    """Print a report on the state for this URL.

    Also update the Stats instance.
    """
    if stat.exception:
        stats.add('fail')
        stats.add('fail_' + str(stat.exception.__class__.__name__))
    elif stat.next_url:
        stats.add('redirect')

    elif stat.content_type == 'text/html':
        stats.add('html')
        stats.add('html_bytes', stat.size)
    else:
        if stat.status == 200:
            stats.add('other')
            stats.add('other_bytes', stat.size)
        else:
            stats.add('error')
            stats.add('error_bytes', stat.size)
            stats.add('status_%s' % stat.status)
