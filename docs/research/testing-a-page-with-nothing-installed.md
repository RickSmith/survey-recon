# Testing a job page when nothing may be installed

Research compiled 2026-09-19, for
[issue #190](https://github.com/RickSmith/survey-recon/issues/190), a child of
the job-page map
[#188](https://github.com/RickSmith/survey-recon/issues/188).

The job page is one self-contained HTML file per screening run. A surveyor
makes it on a laptop with nothing installed, and a principal opens it with the
Wi-Fi off. It will carry hand-written JavaScript. Click a flagged tract and see
why it is flagged. Toggle a layer on and off.

This page records the options for testing that behavior, what each one costs,
and which bucket each one falls into. It records nothing else. A human picks,
and nothing here has been built.

---

## The two buckets

Issue #190 asks for these to be separated, because they have different answers.

| Bucket | Question | How strict |
|---|---|---|
| **1. CI** | What may GitHub Actions install? | Loose. Nothing here touches a surveyor's laptop |
| **2. The laptop** | What must `python -m unittest` run on a bare Python? | Strict. This is the rule that binds |

### Does this repo already treat CI as off the attendee path?

Yes, and it says so in three places. `CLAUDE.md` is not one of them. Its rule is
written about people rather than machines: "Attendees must be able to run this"
and "Do not add a Node dependency to anything attendees run." The words
"attendees run" are what leave CI room, and no line in `CLAUDE.md` names CI at
all.

The three places that do say it:

> `requirements-docs.txt`: "Only maintainers install these. Nothing an attendee
> does requires them - the site is already published, and reading it needs a
> browser and nothing else."

> `.gitignore`: "# Node (present only for maintainers, not attendees)"

> `.github/workflows/slides.yml`: "Marp runs in a container that already carries
> a browser inside it, which is what draws the PDF. Nobody has to install
> anything."

So CI already installs MkDocs, and already runs a Node command-line tool, Marp,
pinned at `marpteam/marp-cli:v4.5.1` inside a container. Neither one is on the
attendee path and both are written down as such.

The test workflow is the opposite case, and it is deliberate:

> `.github/workflows/tests.yml`: "No install step, and that is deliberate rather
> than missing. The tool has no dependencies - standard library only - and
> CLAUDE.md is blunt about keeping it that way."

## What is true of this repo today

All of this was checked in the working tree on 2026-09-19.

| Claim | How it was checked | Result |
|---|---|---|
| `corridor-screen/corridor_screen/` has zero third-party imports | every `import` and `from` statement parsed with `ast`, each root module name compared against `sys.stdlib_module_names` | **0 third-party.** The standard-library modules used are `argparse`, `datetime`, `hashlib`, `html`, `json`, `math`, `os`, `pathlib`, `re`, `sys`, `time`, `tomllib`, `unicodedata`, `urllib`, `xml` |
| `corridor-screen/tests/` has zero third-party imports | the same check | **0 third-party** |
| The suite runs on a bare Python | `python -m unittest discover -s tests -t .` from `corridor-screen/`, on Python 3.11.9, no virtual environment | `Ran 1165 tests`, `OK`, 77.7 seconds |
| CI installs nothing to run it | `.github/workflows/tests.yml` | no install step, and a comment saying why |
| The repo already parses its own generated artifacts in tests | `corridor-screen/tests/test_drawings.py` | reads every number back out of the eight committed SVG drawings with `xml.etree.ElementTree`, and compares each drawing byte for byte with a fresh one |
| The repo already refuses a dependency by test | the same file, `TestNothingIsInstalled` | reads `drawings.py` as text and fails on any import outside a named standard-library set |

`CONTEXT.md` has no entry for JavaScript, browser, CSS or job page. Searched on
2026-09-19: zero hits for each. Whatever is chosen here adds vocabulary that
`CLAUDE.md` requires to be written down.

---

## Option 1 — read the generated page as text and structure

The Python standard library has an HTML parser. It does not have an HTML tree
or a CSS parser.

### The trap: the XML parser this repo already uses will not read HTML

`xml.etree.ElementTree` is what `test_drawings.py` uses on the SVG drawings, and
SVG is XML. An HTML page is not. Both of these were run on 2026-09-19:

```
>>> xml.etree.ElementTree.fromstring(page)          # an ordinary HTML5 page
ParseError: mismatched tag: line 2, column 62
>>> xml.etree.ElementTree.fromstring("<script>if (a < b && c) { go(); }</script>")
ParseError: not well-formed (invalid token): line 1, column 15
```

The second line is the one that matters. A `<` or an `&&` inside embedded
JavaScript is not well-formed XML, so the habit this repo already has does not
carry over to the job page unchanged.

### What does work

`html.parser.HTMLParser`, from the standard library. The Python documentation
describes it as a way to "create a parser instance able to parse invalid
markup," and says of script bodies: "The content of elements like `script` and
`style` is returned as is, without further parsing."

Run on the same sample page on 2026-09-19, it read every tag in order, reported
`checked` as a bare boolean attribute with the value `None`, and handed back the
94-character script body as raw text.

### What this catches

| Catches | Example |
|---|---|
| Every flagged tract has a reason panel, and the panel says what the run says | a tract flagged in `screening.json` with an empty panel |
| The count of drawn tracts matches the run | 524 tracts in the run, 523 in the page |
| Accessibility wiring is present | a toggle with no `aria-controls`, or an id it points at that is missing |
| The page is self-contained | any `src` or `href` pointing off the file |
| The script did not drift | the extracted script body compared with a committed copy |
| The print rules are present | an `@media print` block, found as text |

### What this cannot catch

It reads markup. It does not run anything. So it is blind to a handler wired to
the wrong element, a toggle that opens two panels at once, a CSS rule that hides
the panel the button opens, and any ordering or timing fault. It also cannot
parse CSS, because the standard library has no CSS parser.

### Precedent

Django's `django/test/html.py` is 274 lines, imports only `html` and
`html.parser` from the standard library, and is what `assertHTMLEqual` is built
on. A stdlib-only HTML tree for tests is a known, bounded piece of work.

---

## Option 2 — a JavaScript engine in the standard library

**Not found.** Where we looked:

- The Python 3 standard library reference index, all 34 chapters. There is a
  chapter named "Structured Markup Processing Tools" and one named "Internet
  Data Handling." Neither holds a script engine, and no chapter does
- `sys.stdlib_module_names` on Python 3.11.9, which holds 305 names. Searched
  for `js`, `script` and `ecma`. The only hits are `json` and `_json`
- The same list searched for `css`. Zero hits

Third-party engines exist. `dukpy`, `quickjs`, `js2py`, `pythonmonkey` and
`mini-racer` are each a `pip install`, and several carry compiled extensions.
Every one of them is ruled out of bucket 2 by the dependency rule.

One engine does ship with Windows. Windows Script Host runs JScript, which
Microsoft documents as "the Microsoft implementation of the ECMA 262 language
specification (ECMAScript Edition 3)." That is a 1999 language with no DOM, and
it is Windows only. It is not a way to test a web page.

---

## Option 3 — the browser the reader already has

Chrome and Edge take a `--dump-dom` flag. Chrome's own documentation says it
"prints the serialized DOM of the target page to stdout," and that "Chrome first
parses the HTML code into a DOM, executes any `<script>`" before serializing it
back.

This was run on 2026-09-19 on Windows 11, against the Microsoft Edge that came
with the operating system. Nothing was installed.

```
$ msedge.exe --headless --disable-gpu --virtual-time-budget=3000 \
    --dump-dom "file:///C:/Users/.../selftest.html"
<button id="why" aria-expanded="true" aria-controls="panel">A-7</button>
<div id="panel">Flagged: cemetery within 50 ft</div>
<div id="results">PASS 2 checks</div>
```

The page went in with `aria-expanded="false"` and a `hidden` panel. The script
ran, the attribute flipped, the `hidden` attribute came off, and the page's own
two assertions passed. A Python test can read that output with `html.parser`.

### Its real costs

- **It loads a page. It does not click one.** Everything under test has to run
  at load time, which is what option 7 below is for
- **It exits 0 when the file is missing.** Confirmed on 2026-09-19: a
  `file:///C:/no/such/file.html` dump printed Chromium's error page and returned
  exit code 0. A test has to assert on a marker in the output, never on the
  command having run
- **A long Windows path fails the same silent way.** The first run of the
  demonstration above sat in this repo's scratchpad, and the dump came back as
  Chromium's error page. Moving the file to a short path fixed it. This repo
  already carries `cache.long_path` for the same reason
- **The binary is in a different place on every machine.** The test has to find
  it with `shutil.which` and skip when it cannot
- **macOS has no equivalent for Safari.** A Mac with Chrome or Edge installed is
  fine. A Mac with neither is a skip

### In CI this costs nothing at all

The `ubuntu-24.04` runner image ships Google Chrome 152, Chromium 152, Microsoft
Edge 152 and Firefox 155, with ChromeDriver, Edge WebDriver and Geckodriver
beside them. So a browser step in bucket 1 adds no install line.

---

## Option 4 — browser automation libraries

These are the tools that can click. Each one is a dependency, and the question
is only which bucket it can live in.

| Tool | What must be installed | Bucket |
|---|---|---|
| **Playwright** | `pip install pytest-playwright`, then `playwright install`, which downloads browser binaries. Python 3.8 or newer | 1 only |
| **Selenium** | `pip install selenium`. Selenium Manager then finds or downloads the driver, and it needs network access to do it | 1 only |
| **W3C WebDriver, spoken by hand** | nothing from PyPI. A driver binary and a browser | 1 in practice |

The third row is worth a look before it is dismissed. The W3C WebDriver
specification says a remote end "must provide an HTTP compliant wire protocol
where the endpoints map to different commands," with JSON payloads. Creating a
session, loading a URL, finding an element, clicking it and reading an attribute
back are five ordinary HTTP requests. `urllib.request` and `json` can make them,
and both are already imported elsewhere in this tool.

The cost is that the repo would then own a WebDriver client. It would still need
a driver binary, which no surveyor has, so this stays a bucket 1 answer. What it
buys is a clicking test with no pip install anywhere, on a runner that already
carries ChromeDriver.

---

## Option 5 — write the page so the behavior is mostly not JavaScript

The cheapest test is the one that does not need an engine, because the behavior
was never in a script.

| Behavior | Markup that does it | Source |
|---|---|---|
| Click a tract, see why | `<details>` and `<summary>` | HTML Standard: the `details` element "represents a disclosure widget from which the user can obtain additional information or controls," and its `open` attribute says whether the extra information is shown |
| Toggle a layer | a checkbox, `:checked`, and the subsequent-sibling combinator `~` | Selectors Level 4: `:checked` matches "a user interface element E that is checked/selected"; `~` matches "an F element preceded by an E element" |
| Jump to a flagged tract | `:target` | Selectors Level 4: "an E element being the target of the current URL" |
| The PDF | `@media print` | Media Queries Level 4: `print` "Matches printers, and devices intended to reproduce a printed display" |

Every one of those is markup, and markup is exactly what option 1 can read. The
behavior stops being something a test has to run and becomes something a test
can look at.

The cost is honest and it is not small. Styling a checkbox into something a
principal reads as a layer switch is real CSS work. `<details>` has its own
printing question, and #188 already lists the printed equivalent of every
interaction as not yet settled. A map with many layers may want state that this
does not express.

---

## Option 6 — generate the interactive state at build time

Write every reason panel into the HTML from Python, with its text already
final. The script's whole job is then to show and hide what is already there.

This is the habit the repo already has. `test_drawings.py` reads every number
back out of the committed SVG and compares it with `project-sh16/screening.json`.
The same test regenerates each drawing and compares it byte for byte with the
committed one, with the message "re-run the drawings command and commit the
result." A job page built the same way gets the same test for free, through
`html.parser` rather than `ElementTree`.

What is left in JavaScript after this is a few lines that add and remove a
class. That is a surface a reviewer can read in full, which is a different kind
of safety from a test and a real one.

---

## Option 7 — the page carries its own assertions

The page, or a sibling test page, runs its own checks at load and writes the
result into the DOM. A surveyor opens it and reads PASS or FAIL. CI reads the
same thing through option 3.

The precedent is the browser vendors' own conformance suite. In
web-platform-tests, assertions run inside the page through `testharness.js`, and
a reporting script carries the outcome out. The shape is established.

The demonstration under option 3 is this option working end to end, on a Windows
laptop, with nothing installed.

Its danger is the one this repo already has a rule about. If the script never
runs, the results element still says whatever it said at build time. So it must
start at a value that reads as failure, such as `not run`, and the Python test
must assert on the passing marker. Silence must never read as success.

---

## What other projects with this constraint do

**Django** ships browser tests and does not make anyone run them. Its own
contributor docs say: "Some tests require Selenium and a web browser. To run
these tests, you must install the selenium package and run the tests with the
`--selenium=<BROWSERS>` option." In `django/test/selenium.py` at version 5.2 the
mechanism is one line, with the comment "If no browsers were specified, skip
this class (it'll still be discovered)," followed by
`return unittest.skip("No browsers specified.")(test_class)`. The class is
collected and skipped, so the suite still reports `OK`.

**Sphinx** generates JavaScript into every page it builds, and tests that
JavaScript in a place the Python suite never goes. Its JS specs live in
`tests/js/`, run under `npm test`, and are driven by a separate GitHub workflow
that fires only when a JavaScript file or the test folder changes. The fixtures
those specs read are generated by a Python script,
`utils/generate_js_fixtures.py`, and committed. Installing Sphinx needs no Node,
and running its Python tests does not run a browser.

The pattern both of them share is the same one issue #190 already guessed at.
Split the suite. The part that needs a tool is discovered, named and skipped,
and it lives where the tool is.

---

## The options side by side

| # | Option | Bucket | On a surveyor's laptop | Catches |
|---|---|---|---|---|
| 1 | `html.parser` over the generated page | 2 | nothing to install | content, structure, wiring, self-containment |
| 2 | a stdlib JavaScript engine | — | **not found** | — |
| 3 | headless Chrome or Edge, `--dump-dom` | 1 and 2, skipping | nothing to install, skips when no browser is found | everything the page does at load |
| 4 | Playwright, Selenium, or WebDriver by hand | 1 only | a pip install, so it never runs there | clicking, keyboard, layout, timing |
| 5 | `<details>`, `:checked`, `:target`, `@media print` | 2 | nothing to install | turns behavior into markup that option 1 reads |
| 6 | generate the panel contents in Python | 2 | nothing to install | every word a reader sees, against the run |
| 7 | the page asserts on itself at load | 2 with option 3 | nothing to install | the script's own logic, in a real browser |

---

## Not found, and where we looked

- **A JavaScript engine in the Python standard library.** Looked in the library
  reference index and in `sys.stdlib_module_names` on 3.11.9
- **A CSS parser in the Python standard library.** Looked in the same two places
- **Any line in `CLAUDE.md` that names CI, GitHub Actions or a workflow.**
  Searched the file on 2026-09-19. The separation is real and it is written in
  `requirements-docs.txt`, `.gitignore` and two workflow comments instead
- **Any existing test in this repo that starts a browser or a subprocess other
  than `git`.** Searched `corridor-screen/tests/`. The only `subprocess` use is
  in `test_roe.py`, and it runs `git`
- **A `webbrowser` module that can read a page back.** The standard library has
  `webbrowser`, and it opens a URL for a human. It reports nothing about what
  the page then did

---

## Source URLs

- Python standard library reference — https://docs.python.org/3/library/index.html
- `html.parser` — https://docs.python.org/3/library/html.parser.html
- `unittest`, skipping tests — https://docs.python.org/3/library/unittest.html
- Django, running the test suite — https://docs.djangoproject.com/en/5.2/internals/contributing/writing-code/unit-tests/
- Django `django/test/selenium.py`, tag 5.2 — https://github.com/django/django/blob/5.2/django/test/selenium.py
- Django `django/test/html.py` — https://github.com/django/django/blob/main/django/test/html.py
- Sphinx JavaScript tests — https://github.com/sphinx-doc/sphinx/tree/master/tests/js
- Sphinx Node workflow — https://github.com/sphinx-doc/sphinx/blob/master/.github/workflows/nodejs.yml
- web-platform-tests, `testharness.js` — https://web-platform-tests.org/writing-tests/testharness.html
- Chrome Headless command-line reference — https://developer.chrome.com/docs/automation-and-testing/headless-cli
- GitHub Actions `ubuntu-24.04` runner image — https://github.com/actions/runner-images/blob/main/images/ubuntu/Ubuntu2404-Readme.md
- Playwright for Python, installation — https://playwright.dev/python/docs/intro
- Selenium, install the library — https://www.selenium.dev/documentation/webdriver/getting_started/install_library/
- Selenium Manager — https://www.selenium.dev/documentation/selenium_manager/
- W3C WebDriver — https://www.w3.org/TR/webdriver2/
- HTML Standard, interactive elements — https://html.spec.whatwg.org/multipage/interactive-elements.html
- Selectors Level 4 — https://www.w3.org/TR/selectors-4/
- Media Queries Level 4 — https://www.w3.org/TR/mediaqueries-4/
- MkDocs configuration, validation and strict — https://www.mkdocs.org/user-guide/configuration/
- Microsoft, JScript and ECMAScript Edition 3 — https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/scripting-articles/d1et7k7c(v=vs.84)
