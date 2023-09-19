import logging


def insert_donate_title_html(customTitle):
    donate_file = "templates/donate.html"
    with open(donate_file, "r") as f:
        donate_html = f.read()
    if 'class="customTitle"' in donate_html:
        logging.info("Found existing customTitle HTML in donate.html.")
        return

    customTitle_html = (
        """<h1 class="customTitle">{}""".format(customTitle) + """</h1>"""
    )

    modified_html = donate_html.replace("<h1>Donate Bitcoin</h1>", customTitle_html)

    with open(donate_file, "w") as f:
        f.write(modified_html)

    logging.info("Wrote donate.html with customTitle")

    return


def insert_index_title_html(customTitle):
    index_file = "templates/index.html"
    with open(index_file, "r") as f:
        index_html = f.read()
    if 'class="customTitle"' in index_html:
        logging.info("Found existing customTitle HTML in index.html.")
        return

    customTitle_html = (
        """<h1 class="customTitle">{}""".format(customTitle) + """</h1>"""
    )

    modified_html = index_html.replace("<h1>Pay Bitcoin</h1>", customTitle_html)

    with open(index_file, "w") as f:
        f.write(modified_html)

    logging.info("Wrote index.html with customTitle")

    return


def insert_node_title_html(customTitle):
    node_file = "templates/node.html"
    with open(node_file, "r") as f:
        node_html = f.read()
    if 'class="customTitle"' in node_html:
        logging.info("Found existing customTitle HTML in node.html.")
        return

    customTitle_html = (
        """<h1 class="customTitle">{}""".format(customTitle) + """</h1>"""
    )

    modified_html = node_html.replace("<h1>Open a channel:</h1>", customTitle_html)

    with open(node_file, "w") as f:
        f.write(modified_html)

    logging.info("Wrote node.html with customTitle")

    return
