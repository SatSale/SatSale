import requests

paynym_site = "https://paynym.is/"


def get_paynym(nym):
    if nym is None:
        return None

    r = requests.get(paynym_site + nym)

    if r.status_code == 200:
        nym_html = r.text
        nym_html = nym_html.split('<span class="paycode">')[1].split("</span>")[0]
        return nym_html


def insert_paynym_html(nym):
    donate_file = "templates/donate.html"
    with open(donate_file, "r") as f:
        donate_html = f.read()

    if 'class="paynym"' in donate_html:
        print("Found existing paynym HTML in donate.html.")
        return

    payment_code = get_paynym(nym)
    avatar_url = paynym_site + "{}/avatar".format(payment_code)
    codeimage_url = paynym_site + "{}/codeimage".format(payment_code)

    print("Fetching paynym images...")

    avatar_data = requests.get(avatar_url).content
    with open("static/avatar.png", "wb") as f:
        f.write(avatar_data)

    codeimage_data = requests.get(codeimage_url).content
    with open("static/codeimage.png", "wb") as f:
        f.write(codeimage_data)

    css_html = """
    <style>
        .paynym {
          position: relative;
          float: left;
        }

        .paynym .hoverImg {
          position: absolute;
          left: 0;
          top: 0;
          display: none;
        }

        .paynym:hover .hoverImg {
          display: block;
          }
    </style>
    """

    paynym_name_html = """
    <small style="vertical-align:middle"><a href="{}" target="_blank">{}</a></small>
    """.format(
        paynym_site + nym, nym
    )

    nym_html = (
        """
    <div class="paynym">
        <div class="imageInn">
            <img width="100px" style="border-radius:50px;" src="{{ url_for('static', filename='avatar.png') }}">
        </div>
        <div class="hoverImg">
            <img width="100px" src="{{ url_for('static', filename='codeimage.png') }}">
        </div>
        """
        + """
        <small style="vertical-align:middle"><a href="{}" target="_blank">{}</a></small>
        """.format(
            paynym_site + nym, nym
        )
        + """
    </div>
    <br>
    """
    )

    modified_html = donate_html.replace("</head>", css_html + "\n</head>")
    modified_html = modified_html.replace(
        '<div id="paymentForm">', nym_html + '\n\t<div id="paymentForm">'
    )

    with open(donate_file, "w") as f:
        f.write(modified_html)

    print("Wrote donate.html with paynym tags")

    return
