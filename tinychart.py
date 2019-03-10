from ih.chart import chart as ih_chart
import imgkit
from emojificate.filter import emojificate
import twitter
from placeholder_secrets import SECRETS

#tinycare = "https://twitter.com/tinycarebot/status/1104476321978171392"

SCREEN_NAME = "tinycarebot"
def main():
    api = connect(SECRETS)
    latest = get_latest_tweet(api, SCREEN_NAME)
    text = latest.text.split(":")
    chart = chartit(text)

    design_html = "design.html"
    design_img = "design.png"
    chart_html = "chart.html"
    chart_img = "chart.png"

    with open(design_html, 'w') as f:
        f.write(chart)

    options = {"crop-w": 460, "quiet": ""}
    imgkit.from_file(design_html, design_img, options=options)

    pattern = ih_chart(design_img, palette_name="wool", scale=2, colours=16, render=False, save=False)

    with open(chart_html, 'w') as f:
        f.write(pattern)

    imgkit.from_file(chart_html, chart_img, options={"quiet": ""})
    print("Result: %s" % chart_img)

def connect(s):
    api = twitter.Api(
        consumer_key=s["MY_CONSUMER_KEY"],
        consumer_secret=s["MY_CONSUMER_SECRET"],
        access_token_key=s["MY_ACCESS_TOKEN_KEY"],
        access_token_secret=s["MY_ACCESS_TOKEN_SECRET"],
    )
    return api

def get_latest_tweet(api, SCREEN_NAME):

    return api.GetUserTimeline(screen_name=SCREEN_NAME, count=1, exclude_replies=True)[0]

    # Escape early if our image is stale.
    now = int(datetime.datetime.utcnow().strftime("%s"))
    if now - latest.created_at_in_seconds > 15 * 60:
        print("Latest tweet is out of date!")
        print("It is currently %s" % time.ctime())
        print(latest)
        sys.exit(1)
    return latest

def chartit(data):
    emoji, text = data

    emoji = emojificate(emoji)
    html = """
        <link rel='stylesheet' href='style.css'>
        <div class='border'>
            <div class='emoji'>%s</div>
            <div class='text'>%s</div>
        </div>
        """ % (emoji, text)
    return html

if __name__ == "__main__":
    main()
