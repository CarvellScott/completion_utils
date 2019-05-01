# completion_utils

A lightweight set of functions intended to make writing shell completion functions in python easier. Install with `pip install .` and import what you need from `completion_utils`. Generally you only need to import `bash_completion_decorator`, and decorate a function with it.

## Usage
Supposing you have some simple completion like this already...
```
#!/usr/bin/env python3
import sys

def foobar():
    return ["a", "bunch", "of", "potential", "matches"]


def completion_hook(cmd, curr_word, prev_word):
    potential_matches = foobar()
    matches = [k for k in potential_matches if k.startswith(curr_word)]
    return matches


def main():
    results = completion_hook(*sys.argv[1:])
    if len(results):
          print("\n".join(results))


if __name__ == "__main__":
    main()
```

You can then decorate `completion_hook` with `bash_completion_decorator` to have shell completion automatically supply the necessary arguments and use bash_complete to test out the results of potential completions.
```
#!/usr/bin/env python3
import sys
import unittest
from completion_utils import bash_completion_decorator, bash_complete

class CompletionTestCase_up(unittest.TestCase):
    def test_all_options_show(self):
        expected = "\n".join(sorted(foobar()))
        actual = bash_complete("heylook ", __file__)

    def test_one_option(self):
        expected = "m"
        actual = bash_complete("heylook m", __file__)

def foobar():
    return ["a", "bunch", "of", "potential", "matches"]


@bash_completion_decorator
def completion_hook(cmd, curr_word, prev_word):
    potential_matches = foobar()
    matches = [k for k in potential_matches if k.startswith(curr_word)]
    return matches

if __name__ == "__main__":
    completion_hook()
```
