import logging


def insert_font_family_css(customCSS):
    css_file = "static/style.css"
    with open(css_file, "r") as f:
        style_css = f.read()
    if '/* Custom Font Family CSS */' in style_css:
        logging.info("Found existing fontFamilyCSS in style.css.")
        return

    customFontFamily_css = (
        """--preset--font--family: {}; /* Custom Font Family CSS */""".format(customCSS)
    )

    modified_css = style_css.replace("--preset--font--family: \"Lucida Console\", \"Courier New\", monospace;", customFontFamily_css)

    with open(css_file, "w") as f:
        f.write(modified_css)

    logging.info("Wrote style.css with customFontFamilyCSS")

    return


def insert_background_css(customCSS):
    css_file = "static/style.css"
    with open(css_file, "r") as f:
        style_css = f.read()
    if '/* Custom Background CSS */' in style_css:
        logging.info("Found existing backgroundCSS in style.css.")
        return

    customBackground_css = (
        """--preset--primary--background: {}; /* Custom Background CSS */""".format(customCSS)
    )

    modified_css = style_css.replace("--preset--primary--background: #f7931a;", customBackground_css)

    with open(css_file, "w") as f:
        f.write(modified_css)

    logging.info("Wrote style.css with customBackgroundCSS")

    return


def insert_primary_color_css(customCSS):
    css_file = "static/style.css"
    with open(css_file, "r") as f:
        style_css = f.read()
    if '/* Custom Primary Color CSS */' in style_css:
        logging.info("Found existing primaryColorCSS in style.css.")
        return

    customPrimaryColor_css = (
        """--preset--primary--font--color: {}; /* Custom Primary Color CSS */""".format(customCSS)
    )

    modified_css = style_css.replace("--preset--primary--font--color: #000;", customPrimaryColor_css)

    with open(css_file, "w") as f:
        f.write(modified_css)

    logging.info("Wrote style.css with customPrimaryColorCSS")

    return


def insert_secondary_color_css(customCSS):
    css_file = "static/style.css"
    with open(css_file, "r") as f:
        style_css = f.read()
    if '/* Custom Secondary Color CSS */' in style_css:
        logging.info("Found existing secondaryColorCSS in style.css.")
        return

    customSecondaryColor_css = (
        """--preset--secondary--font--color: {}; /* Custom Secondary Color CSS */""".format(customCSS)
    )

    modified_css = style_css.replace("--preset--secondary--font--color: #fff;", customSecondaryColor_css)

    with open(css_file, "w") as f:
        f.write(modified_css)

    logging.info("Wrote style.css with customSecondaryColorCSS")

    return
