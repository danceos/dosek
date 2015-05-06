import re
import os
from collections import namedtuple
from generator.tools import format_source_tree

class CodeTemplate:
    Snippet = namedtuple("Snippet", ["name", "args", "body"])
    Generate = namedtuple("Generate", ["name", "args"])


    def __init__(self, generator, filename, begin='{{{', end='}}}'):
        self.filename = filename
        self.generator = generator
        if generator:
            filename = os.path.join(generator.template_base, filename)

        self.begin = begin
        self.end   = end

        self.env_stack = []

        with open(filename, "r") as fd:
            self.content = fd.read()
            self.content = self.content.replace("\t", "    ")
        self.snippets, self.stream = self.__find_snippets(self.content)

    def __find_snippets(self, content):
        rest = content
        stream = []
        snippets = {}
        level = 0
        current_braces = ""
        while True:
            match = re.search('(.*?)(%s|%s)(.*)' %(self.begin, self.end), rest,
                              re.MULTILINE | re.DOTALL)
            if not match:
                stream.append(rest)
                break
            before = match.group(1)
            token  = match.group(2)
            after  = match.group(3)
            if level == 0:
                stream.append(before)
            else:
                current_braces += before
                if level != 1 or token != self.end:
                    current_braces += token

            if token == self.begin:
                level += 1
            else:
                level -= 1
                if level == 0:
                    # Match Snippets
                    match = re.match("^(?:snippet:|#)(.*?)(?::(.*?))?\\|(.*)", current_braces,
                                     re.MULTILINE | re.DOTALL)
                    if match:
                        # Skip after define
                        while after[0] in " \n":
                            char, after = after[0], after[1:]
                            if char == '\n':
                                break

                        name = match.group(1)
                        args = match.group(2)
                        body = match.group(3)
                        body = body.lstrip("\n")
                        body = re.sub('\\\\\n\s*', '', body, flags = re.MULTILINE)
                        if args:
                            args = [x.strip() for x in args.split(",")
                                    if x.strip() != ""]
                        else:
                            args = []
                        snippets[name] = self.Snippet(name = name,
                                                      args = args,
                                                      body = body)
                        current_braces = ""
                    match = re.search("^(?:generate:|!)([^:\\|]*)(?::([^\\|]*))?(?:\\|(.*))?", current_braces,
                                      re.MULTILINE | re.DOTALL)
                    # Match Generates
                    if match:
                        name = match.group(1)
                        args = match.group(2)
                        body = match.group(3)
                        if args:
                            args = args.split(',')
                        else:
                            args = []
                        if body:
                            body = body.lstrip("\n")
                            body = re.sub('\\\\\n\s*', '', body, flags = re.MULTILINE)
                            snippet = self.Snippet(name, [], body)
                            args.append(snippet)
                        gen = self.Generate(name, args)
                        stream.append(gen)
                        current_braces = ""
                    assert current_braces == "", "Could not parse %s" % current_braces
            rest = after
        return snippets, stream

    def expand(self, stream = None, args = None, snippets = None):
        if not stream:
            stream = self.stream
        if not args:
            args = {}
        if not snippets:
            snippets = self.snippets

        self.env_stack.append(self.snippets)

        ret = []
        for elem in stream:
            if type(elem) == str:
                text = elem % args
                ret.append(text)
            else:
                assert isinstance(elem, self.Generate)
                snippet = snippets.get(elem.name)
                ret.append(self.__expand_snippet(elem.name, snippet, elem.args))
        return "".join(ret)

    def __expand_snippet(self, name, snippet, args):
        if hasattr(self, name):
            if snippet:
                ret = getattr(self, name)(snippet, **dict(list(zip(snippet.args, args))))
            else:
                ret = getattr(self, name)(snippet, args)

            if type(ret) == list:
                ret = "".join(ret)
            return ret

        assert snippet, "snippet:'%s' not found (%s)" % (name, args)
        return self.expand_snippet(snippet, **dict(list(zip(snippet.args, args))))

    def __format(self, text, prefix_length):
        if text is None:
            text = ""
        text = format_source_tree(self.generator, text)
        spaces = " " * prefix_length
        return text.replace("\n", "\n" + spaces)

    def expand_snippet(self, snippet, **kwargs):
        if type(snippet) == str:
            snippet = self.snippets[snippet]
        try:
            formatted =  snippet.body % kwargs
            if self.begin in formatted:
                # Recursive Snippet
                n_snippets, n_stream = self.__find_snippets(formatted)
                x = self.env_stack[-1].copy()
                x.update(n_snippets)
                return self.expand(n_stream, list(), n_snippets)
            return formatted
        except:
            raise TypeError("Instanciation of %s failed (%s)" %(snippet.name, kwargs))

    def get(self, snippet, args):
        path = args[0].split(".")
        obj = self
        for elem in path:
            obj = getattr(obj, elem)
            if callable(obj):
                obj = obj()
        return str(obj)

import unittest

class CodeTemplateTest(unittest.TestCase):
    class Inner(CodeTemplate):
        foobar = 23
        def the_calling(self):
            return self.foobar + 10
        def this(self):
            return self

        def indirection_A(self,snippet, args):
            return "XYZ"

        def counter(self, snippet, args):
            ret = ""
            for i in range(int(args[0]), int(args[1])):
                ret += self.expand_snippet(args[2], i = i)
            return ret

    def setUp(self):
        self.template = self.Inner(None, "test/template.in")

    def test_expand(self):
        exp = self.template.expand()
        lines = exp.split("\n")
        for line in lines:
            if "=" in line:
                expect, got = line.split("=")
                self.assertEqual(expect, got)

if __name__ == '__main__':
    unittest.main()
