Coding Style for CoRedOS  {#coding_style}
========================

You may violate/break any of the following rules __if you have a good reason__ to
do so, e.g., if readability is notably enhanced.

For Python code, try to stick to <http://www.python.org/dev/peps/pep-0008>.
Especially use 4 spaces per indentation level, and don't mix tabs and spaces
for indentation.

The following style rules apply to C/C++ code:

## Language ##
Comments, commit messages, "temporary" stuff: __English__ (without exception!)

## Naming conventions ##
   * Source files: .cc (Source), .h (Header), .ah (Aspect Header), MixedCase
   * Namespaces: lowercase
   * Classes, (global) functions: MixedCase, starting with uppercase letter
   * Public members: MixedCase, starting with lowercase letter
   * Private & protected members: starting with `m_`
   * Global Variables: starting with `g_`
   * Preprocessor macros: uppercase
     -  Include guard for MyFooBar.hpp: `__MY_FOO_BAR_HPP__`
   * Constant variables: uppercase
   * (no convention for local variables)
   * typedefs: lowercase, underscores (`good_name_t`)
   * abbreviations (even in identifiers): uppercase
   * A variable name must have at least 2 characters

## Comments ##
* Doxygen comments:
   -  In detail for all public members (parameters, return value, side
      effects, ...)
   -  (At least) Briefly for private/protected members
   -  At the top of each header file: `\@file` and `\@brief`
   -  For each complex data type (and its elements)
* Explain *nontrivial* program logic not only by describing the "what's
  happening here", but also the "why are we doing it this way".
* Use "normal" C/C++ comments within functions (`//`, `/**/`).
* No author names, creation dates, change logs etc. in source files.
  That's why we're using a VCS.

## Formatting ##
* Indentation: 1 tab (tabstop at 4 spaces)
  -  may be relaxed / mixed with spaces for better readability of
     multi-line statements, e.g.:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.c}
cout << "The counter value is: "
<TAB> << value;
if (first_looong_condition &&
<TAB>second_looong_condition) {
<TAB>...
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Preprocessor directives start in column 1.

* Max. line length: 100 characters.

* `public`/`private`/`protected` has the same identation as its surrounding
   `class Foo` statement (we'd waste one indentation level for every class
   definition otherwise):
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.c}
class Foo {
public:
<TAB>void doSomething();
};
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* Similarly (and for the same reason) for namespaces and switch/case statements:
~~~~~~~~~~~~~~~~~~~~{.c}
switch (foo) {
case 1:
<TAB>...
}
~~~~~~~~~~~~~~~~~~~~

* Compound statements (blocks): `<Space>+{` in the same line as its
governing control structure (`if`, `while`, `for`, `switch`, `try`) or
`namespace`/`class` definition:
~~~~~~~~~~~~~~~~~~~~~~{.c}
if (something {
<TAB> ...
}
~~~~~~~~~~~~~~~~~~~~~~

* Method/Function definitions are an exception to this (`{` in a new line):

  Definition:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.c}
void myFunction(int i)
{
<TAB>...
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

  Declaration:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.c}
void myFunction(int i);
~~~~~~~~~~~~~~~~~~~~~~~~~~~~


* Control structure tokens (`if`, `try`, `for`, ...) are followed by a
single space for better disambiguation from function definitions:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~{.c}
if (...) {
<TAB>...
} else if (...) {
<TAB>...
} else {
<TAB>...
}
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

