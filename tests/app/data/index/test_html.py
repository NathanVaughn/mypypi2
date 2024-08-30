import pytest

import app.data.index.html


@pytest.mark.parametrize(
    "given, expected",
    (
        ("sha256=value", ("sha256", "value")),
        ("md5=value", ("md5", "value")),
        ("md6=value", (None, None)),
        ("sha256value", (None, None)),
        ("", (None, None)),
        ("True", (None, None)),
    ),
)
def test_parse_hash(given: str, expected: tuple[str | None, str | None]):
    """
    Check the hash parsing function.
    """
    assert app.data.index.html.parse_hash(given) == expected


def test_parse_simple_html():
    """
    Complicated test for the simple HTML parser.
    """
    content = """
    <!DOCTYPE html>
    <html>
        <head>
            <meta name="pypi:repository-version" content="1.1">
            <title>Links for black</title>
        </head>
        <body>
            <h1>Links for black</h1>

            <!-- Main test -->
            <a
            href="https://example.com/black-18.3a0-py3-none-any.whl#sha256=filehash"
            data-requires-python="&gt;=3.6"
            data-dist-info-metadata="sha256=metadatahash"
            data-core-metadata="sha256=metadatahash">black-18.3a0-py3-none-any.whl</a><br />

            <!-- Test code file with no hash -->
            <a href="https://example.com/black-18.3a0.tar.gz">black-18.3a0.tar.gz</a><br />

            <!-- Test metadata with no hash -->
            <a
            href="https://example.com/black-18.3a1-py3-none-any.whl#sha256=filehash"
            data-requires-python="&gt;=3.6"
            data-core-metadata="true">black-18.3a1-py3-none-any.whl</a><br />

            <!-- Test absolufying URLs -->
            <a href="/black-18.3a1.tar.gz">black-18.3a1.tar.gz</a><br />
        </body>
    </html>
    """
    app.data.index.html.parse_simple_html(
        html_content=content, html_url="https://example.com/", repository=None, package_name="black")
