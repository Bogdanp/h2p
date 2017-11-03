import tempfile

from h2p import generate_pdf


def test_can_generate_pdfs():
    # Given that I have some HTML
    html = "<h1>Hello!</h1>"

    # And an output path
    _, path = tempfile.mkstemp()

    # When I try to convert that HTML to a PDF
    task = generate_pdf(path, source_html=html)
    task.result()

    # Then the output should be created
    with open(path, "rb") as f:
        data = f.read()
        assert data.startswith(b"%PDF-1.4")


def test_can_generate_many_pdfs():
    # Given that I have some HTML
    html = "<h1>Hello!</h1>"

    # When I try to conver many pdfs at once
    tasks = []
    for _ in range(8):
        _, path = tempfile.mkstemp()
        tasks.append((path, generate_pdf(path, source_html=html)))

    # Then each one should generate output
    for path, task in tasks:
        task.result()

        with open(path, "rb") as f:
            data = f.read()
            assert data.startswith(b"%PDF-1.4")
