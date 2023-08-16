import re
import sys
import os
import pydoc

DIRECTIVES_TO_INCLUDE = [
    'autosummary', 'module', 'currentmodule', 'automodule', 'class',
    'autoclass', 'method', 'classmethod', 'coroutinemethod', 'automethod',
    'staticmethod', 'function', 'autofunction', 'c:function', 'data',
    'attribute', 'exception', 'c:var', 'c:type', 'decorator', 'envvar',
    'autodata', 'template'
]
class Parser:
    def __init__(self, file=None):
        self.lines = []
        self.indices = {}
        
    def save_raw(self, path, content):
        tmp = '\n'.join(content)
        tmp = re.sub(r'.\x08', '', tmp)
        with open(path, 'w') as f:
            f.write(tmp)
    

    def read(self, stream):
        """Read all lines from stream STREAM, and store the lines in the
        object attribute LINES.  All `autosummary` directives are converted to
        pseudo `autosummary_` directives."""

        def repl_autoloaded(m):
            cat = m.group(1)      # the template: function or class
            buf = m.group(2)

            buf = re.sub(r'^ +', '.. {}:: '.format(cat), buf, flags=re.MULTILINE)
            return '\n' + buf + '\n\n'

        buf = f.read()
        # a = re.match(r'\n.. autosummary::.*?\n\n(.+?)\n\n', buf)
        # print(re.findall(r'\.\.\sautosummary::.*?:template:(.*?).rst\n\n(.*?)\n\n', buf, flags=re.DOTALL))
        buf = re.sub(r'\.\.\sautosummary::.*?:template:(.*?).rst\n\n(.*?)\n\n', 
                    repl_autoloaded,
                    buf,
                    flags=re.DOTALL)
        self.lines = buf.splitlines()

    def parse_directive(self, astr):
        """Check the existence of an ReST directive in string ASTR.  Return a
        tuple of (DIRECTIVE, VALUE) if it exists.  If a directive is not
        found, retrun (None, None)."""
        m = re.search(r'\.\. *([^:]+):: *(.*)', astr)
        if m:
            return m.groups()
        else:
            return None, None

    def compose_name(self, *kargs):
        """Return a string joined by '.' from the list of arguments."""
        components = [n for n in kargs if n is not None]
        return '.'.join(components)

    def is_valid_name(self, name):
        """Check if name NAME is a valid Python symbol name.  Return True if
        valid and return False otherwise."""
        try:
            obj = pydoc.locate(name)
        except pydoc.ErrorDuringImport:
            return False
        if obj is not None:
            return True
        return False

    def resolve_name(self, name, module=None, cls=None):
        """Locate a valid symbol name NAME in either global name space, module
        MODULE, or class CLS.  Retun a valid symbol name as a string.  Return
        None if no valid symbol is found."""
        if module is None:
            module = self.module
        if cls is None:
            cls = self.cls
        for m in [module, None]:
            for c in [cls, None]:
                n = self.compose_name(m, c, name)
                if self.is_valid_name(n):
                    return n
        return None

    def pydoc_lines_for(self, name):
        """Return a list of lines for PyDoc document for NAME.  If no document
        for NAME is found, return an empty array."""
        name = self.resolve_name(name)
        if name is None:
            return '', []
        doc = pydoc.render_doc(name)
        lines = doc.splitlines()
        # discard the header lines

        return name, lines[2:]

    def reset_context(self):
        self.module = None
        self.cls = None

    def track_context(self, line):
        key, val = self.parse_directive(line)
        if key in ['module', 'currentmodule', 'automodule']:
            self.module = val

    def expand_auto_directives(self, save_dir=None):
        """Expand all auto directives with corresponding PyDoc documents."""
        lines = []
        class_cnt = 0
        func_cnt = 0
        self.reset_context()
        for line in self.lines:
            lines.append(line)
            self.track_context(line)
            key, val = self.parse_directive(line)
            # if key and key.startswith('auto') and val:
            if key and key=='function' and val:
                api, content = self.pydoc_lines_for(val)
                lines += content
                if save_dir and api:
                    func_cnt += 1
                    self.save_raw(os.path.join(save_dir, api), content)
                
            elif key and key=='class' and val:
                class_cnt += 1

        self.lines = lines
        return class_cnt, func_cnt

    def parse(self, save_dir=None):
        return self.expand_auto_directives(save_dir)
        # self.parse_indices()

file = '/Users/danning/Desktop/deepflaw/scikit-learn/doc/modules/classes.rst'      # scikit-learn/doc/modules/classes.rst
rst = Parser()
with open(file) as f:
    rst.read(f)
class_cnt, func_cnt = rst.parse(save_dir = '/Users/danning/Desktop/deepflaw/exp2/code/dl-fuzzer/doc_analysis/collect_doc/sklearn/raw')
print('# Class: {}, # Function: {}'.format(class_cnt, func_cnt))