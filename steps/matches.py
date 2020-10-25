anyquote = r'[\'"`]'

# Use two or more periods, or question mark to allow some directives to give
# errors without failing the test
conditional = r'(?P<err>\?|\.\.*)?'

str_vars = sv = dict( nq=anyquote, cl=conditional )
