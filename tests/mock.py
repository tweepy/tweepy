import random
import string

def mock_tweet():
    """Generate some random tweet text."""
    count = random.randint(70, 140)
    return ''.join([random.choice(string.letters) for i in xrange(count)])

