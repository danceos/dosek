import re
from collections import namedtuple
from generator.tools import format_source_tree

class CodeTemplate:
    Snippet = namedtuple("Snippet", ["name", "args", "body"])

    def __init__(self, generator, filename):
        self.filename = filename
        self.generator = generator
        with open("%s/%s" % (generator.template_base, filename), "r") as fd:
            self.content = fd.read()
        self.snippets = {}
        self.__find_snippets()


    def __find_snippets(self):
        while True:
            match = re.search("{{{snippet:(.*?):(.*?)\|(.*?)}}}", self.content, re.MULTILINE | re.DOTALL)
            if not match:
                break
            name = match.group(1)
            args = match.group(2)
            body = match.group(3)
            self.content = self.content[:match.start()] + self.content[match.end():]
            self.snippets[name] = self.Snippet(name = name,
                                               args = [x.strip() for x in args.split(",")],
                                               body = body)
    def expand(self, __irgnored = None):
        text = self.content
        while True:
            match = re.search("{{{generate:(.*?)(?::(.*?))?}}}", text)
            if not match:
                break
            name = match.group(1)
            snippet = self.snippets.get(name)
            args = match.group(2)
            if snippet:
                args = args.split(",", len(snippet.args))

            nl   = match.start()
            while nl > 0 and text[nl] != '\n':
                nl -= 1
            prefix_length = match.start() - nl - 1

            result = self.__format(self.__expand_snippet(name, snippet, args), prefix_length)
            if result == None:
                result = ""
            text = text[:match.start()] + result + text[match.end():]
        return text

    def __expand_snippet(self, name, snippet, args):
        if hasattr(self, name):
            if snippet:
                return getattr(self, name)(snippet, **dict(zip(snippet.args, args)))
            else:
                return getattr(self, name)(snippet, args)

        return self.expand_snippet(snippet, **dict(zip(snippet.args, args)))

    def __format(self, text, prefix_length):
        if text is None:
            text = ""
        text = format_source_tree(self.generator, text)
        spaces = " " * prefix_length
        return text.replace("\n", "\n" + spaces)

    def expand_snippet(self, snippet, **kwargs):
        if type(snippet) == str:
            snippet = self.snippets[snippet]
        return snippet.body % kwargs
