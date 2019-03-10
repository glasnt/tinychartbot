from ih.chart import chart as ih_chart
import imgkit
from emojificate.filter import emojificate
import twitter
from placeholder_secrets import SECRETS
from manual import designit
from PIL import Image, ImageDraw, ImageFont

SCREEN_NAME = "tinycarebot"
 
def main():
    api = connect(SECRETS)
    latest = get_latest_tweet(api, SCREEN_NAME)
    text = latest.text.split(":")
    design = designit(text)

    design_img = "design.png"
    chart_html = "chart.html"
    chart_img = "chart.png"
    
    design.save(design_img)

    pattern = ih_chart(design_img, palette_name="wool", scale=2, colours=8, render=False, save=False)

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


def designit(data):
    emoji, text = data
    
    line_length = 18
    if len(text) > line_length:
        cul = 0
        res = []
        for x in text.split(" "):
            cul += len(x)
            if cul <= line_length:
                res.append(x)
            else:
                res.append("\n%s" % x)
                cul = 0
        text = " ".join(res)
                

    if emoji in ["🌊"]:
        emoji = "💧"

    font = ImageFont.truetype("Minecraft.ttf", 32, encoding="unic")
    efont = ImageFont.truetype("og-dcm-emoji.ttf", 64, encoding="unic")

    tmpimage = Image.new("RGB", (1000, 500))
    d = ImageDraw.Draw(tmpimage)
    tw, th = d.textsize(text, font=font)

    H = th + 160
    W = tw + (tw % 20) + 60

    image = Image.new("RGB", (W, H), color=(255, 255, 255))
    d = ImageDraw.Draw(image)
    tw, th = d.textsize(text, font=font)

    d.multiline_text(((W-tw)/2,(H - th - 30)), text, font=font, align="center", fill=(0,0,0))
    # emoji
    ew, eh = d.textsize(emoji, font=efont)
    d.text(((W-ew)/2, 40), emoji, font=efont, fill=(0,0,0))

    # borders
    index = 1
    border = Image.open("borders/%d_border.png" % index)
    for x in range(0, H, border.height):
        image.paste(border, (0, x))
        image.paste(border, (W - border.width, x))

    border = border.transpose(Image.ROTATE_90)
    for x in range(0, W, border.width):
        image.paste(border, (x, 0))
        image.paste(border, (x, H - border.height))

    corner = Image.open("borders/%d_corner.png" % index)
    image.paste(corner, (0, 0))
    corner = corner.transpose(Image.ROTATE_90)
    image.paste(corner, (0, H-corner.height))
    corner = corner.transpose(Image.ROTATE_90)
    image.paste(corner, (W-corner.width, H-corner.height))
    corner = corner.transpose(Image.ROTATE_90)
    image.paste(corner, (W-corner.width, 0))

    
    return image

#def designit(data):
#    emoji, text = data
#
#    emoji = emojificate(emoji)
#    html = """
#        <link rel='stylesheet' href='style.css'>
#        <div class='border'>
#            <div class='emoji'>%s</div>
#            <div class='text'>%s</div>
#        </div>
#        """ % (emoji, text)
#    return html

if __name__ == "__main__":
    main()
