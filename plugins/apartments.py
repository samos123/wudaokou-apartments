import os
import datetime
import logging

ORDER = 999
APARTMENTS_PATH = 'apartments/'
APARTMENTS = []

from django.template import Context
from django.template.loader import get_template
from django.template.loader_tags import BlockNode, ExtendsNode

def getNode(template, context=Context(), name='subject'):
    """
    Get django block contents from a template.
    http://stackoverflow.com/questions/2687173/
    django-how-can-i-get-a-block-from-a-template
    """
    for node in template:
        if isinstance(node, BlockNode) and node.name == name:
            return node.render(context)
        elif isinstance(node, ExtendsNode):
            return getNode(node.nodelist, context, name)
    raise Exception("Node '%s' could not be found in template." % name)


def preBuild(site):

    global APARTMENTS

    # Build all the posts
    for page in site.pages():
        if page.path.startswith(APARTMENTS_PATH):

            # Skip non html apartments
            if not page.path.endswith('.html'):
                continue

            # Find a specific defined variable in the page context,
            # and throw a warning if we're missing it.
            def find(name):
                c = page.context()
                if not name in c:
                    logging.info("Missing info '%s' for post %s" % (name, page.path))
                    return ''
                return c.get(name, '')

            # Build a context for each post
            postContext = {}
            postContext['title'] = find('title')
            postContext['date'] = find('date')
            postContext['price'] = find('price')
            postContext['term'] = find('term')
            postContext['path'] = page.path
            postContext['body'] = getNode(get_template(page.path), name="body")

            # Parse the date into a date object
            try:
                postContext['date'] = datetime.datetime.strptime(postContext['date'], '%Y-%m-%d')
            except Exception, e:
                logging.warning("Date format not correct for page %s, should be dd-mm-yy\n%s" % (page.path, e))
                continue

            APARTMENTS.append(postContext)

    # Sort the posts by date
    APARTMENTS = sorted(APARTMENTS, key=lambda x: x['date'])
    APARTMENTS.reverse()

    indexes = xrange(0, len(APARTMENTS))

    for i in indexes:
        if i+1 in indexes: APARTMENTS[i]['prevPost'] = APARTMENTS[i+1]
        if i-1 in indexes: APARTMENTS[i]['nextPost'] = APARTMENTS[i-1]


def preBuildPage(site, page, context, data):
    """
    Add the list of posts to every page context so we can
    access them from wherever on the site.
    """
    context['apartments'] = APARTMENTS

    for post in APARTMENTS:
        if post['path'] == page.path:
            context.update(post)

    return context, data
