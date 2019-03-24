import requests
import shutil
from pathlib import Path
import random
import os

from ih.chart import chart as ih_chart
import imgkit
import twitter
from placeholder_secrets import SECRETS
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

    pattern = ih_chart(design_img, palette_name="wool", scale=2, colours=16, render=False, save=False)

    with open(chart_html, 'w') as f:
        f.write(pattern)

    imgkit.from_file(chart_html, chart_img, options={"quiet": ""})
    
    # Hack - reduce the filesize of the generated image considerably by
    # running it through imagemagick
    os.system("convert %s %s" % (chart_img, chart_img))

    print("Result: %s" % chart_img)

    tweet = "Cross-stitch Sampler: \"%s\"\n\nhttps://twitter.com/tinycarebot/statuses/%s" % (latest.text, latest.id) 
    api.PostUpdate(tweet, in_reply_to_status_id=latest.id, media=chart_img)

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
    
    line_length = 10
    if len(text) > line_length:
        cul = 0
        res = []
        for x in text.split(" "):
            if x == "": 
                continue
            cul += len(x)
            if cul <= line_length:
                res.append(x)
            else:
                res.append("\n%s" % x)
                cul = 0
        text = " ".join(res)
                

    # Minecraft 32pt at ih-Scale 2 makes for pixel perfect text
    font = ImageFont.truetype("Minecraft.ttf", 32, encoding="unic")

    c = emoji[0]
    e = str(c.encode("unicode_escape")).lower().split("u")[1].strip("'").strip("0")
    url = "https://abs.twimg.com/emoji/v2/72x72/%s.png" % e

    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open("emoji.png", 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        raise ValueError("Image not found at %s" % url)

    # Transparency hacks
    epng = Image.open("emoji.png").convert("RGBA")
    alpha = epng.convert('RGBA').split()[-1]
    bg = Image.new("RGBA", epng.size, (255,255,255,255))
    bg.paste(epng, mask=alpha)
    epng = bg

    tmpimage = Image.new("RGB", (1000, 500))
    d = ImageDraw.Draw(tmpimage)
    tw, th = d.textsize(text, font=font)

    border, corner = get_random_border()

    H = th + 160 
    H = H + (H % border.height) 
    W = tw + (tw % 20) + 60 + 2
    W = W + (W % border.width)

    image = Image.new("RGB", (W, H), color=(255, 255, 255))
    d = ImageDraw.Draw(image)
    tw, th = d.textsize(text, font=font)


    lefttext = (W-tw) / 2
    lefttext = (lefttext % 2) + lefttext

    d.multiline_text((lefttext,(H - th - 30)), text, font=font, align="center", fill=(0,0,0))

    # emoji
    image.paste(epng, (int((W-epng.width)/2), 40)) 
#    ew, eh = d.textsize(emoji, font=efont)
#    d.text(((W-ew)/2, 40), emoji, font=efont, fill=(0,0,0))

    for x in range(0, H, border.height):
        image.paste(border, (0, x))
        image.paste(border, (W - border.width, x))

    border = border.transpose(Image.ROTATE_90)
    for x in range(0, W, border.width):
        image.paste(border, (x, 0))
        image.paste(border, (x, H - border.height))

    image.paste(corner, (0, 0))
    corner = corner.transpose(Image.ROTATE_90)
    image.paste(corner, (0, H-corner.height))
    corner = corner.transpose(Image.ROTATE_90)
    image.paste(corner, (W-corner.width, H-corner.height))
    corner = corner.transpose(Image.ROTATE_90)
    image.paste(corner, (W-corner.width, 0))

    return image

def get_random_border():
    BORDER_DIR = "borders/"
    
    # Assume there's always 2 files per border type, and that they match
    # Then, randomly pick one. 
    # if this breaks, blame Katie.
    length = sum(1 for _ in Path(BORDER_DIR).iterdir()) / 2
    index = random.randint(1, length)


    border = Image.open("%s/%s_border.png" % (BORDER_DIR, index))
    corner = Image.open("%s/%s_corner.png" % (BORDER_DIR, index))

    return (border, corner)
if __name__ == "__main__":
    main()
