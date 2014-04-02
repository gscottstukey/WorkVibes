import re

replacement_patterns = [
        (r'won\'t', 'will not'),
        (r'can\'t', 'cannot'),
        (r'i\'m', 'i am'),
        (r'ain\'t', 'is not'),
        (r'(\w+)\'ll', '\g<1> will'),
        (r'(\w+)n\'t', '\g<1> not'),
        (r'(\w+)\'ve', '\g<1> have'),
        (r'(\w+t)\'s', '\g<1> is'),
        (r'(\w+)\'re', '\g<1> are'),
        (r'(\w+)\'d', '\g<1> would'),
        (r'E\.g\.', 'for example'),
        (r'-', ' '),
        (r';', '.'),
        (r':\)', ','),
        (r'/', ' '),
        (r'( \d\.)+', ''),
        (r'\)', '. '),
        (r' \(', ', '),
        (r'\*', ', '),
        (r'\. \.', '.'),
        (r'\. \,', '.'),
        (r'[\.]([A-Z])+', '. \g<1>'),
        (r'\+', ' and '),
        (r'\!.', '!'),
        (r'([a-z])([A-Z])+','\g<1> \g<2>')
]
# missing .a, .A as separate sentences?

class RegexpReplacer(object):
    def __init__(self, patterns=replacement_patterns):
        self.patterns = [(re.compile(regex), repl) for (regex, repl) in patterns]

    def replace(self, text):
        s = text
        for (pattern, repl) in self.patterns:
            (s, count) = re.subn(pattern, repl, s)
        return s