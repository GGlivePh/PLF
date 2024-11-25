import os
import xml
import qrcode
import xml.etree.ElementTree as ET
import io
import base64
from joblib import Parallel, delayed
import subprocess


DATE="2024-05-21"


n_labs = 24
START= 0

configs ={
    "large":{
        "N_REPS": 2,
        "n_blanks": 0,
        "OUT_DIR": "labels-large",
        "TEMPLATE": "template_large.svg",
        "TILES":  "4x12"
    },


    "small":{
        "N_REPS":3,
        "n_blanks" : 8,
        "OUT_DIR": "labels",
        "TEMPLATE": "template.svg",
        "TILES":  "5x16"}
}


def convert(output):
    png = os.path.splitext(output)[0] + ".png"
    subprocess.run(["magick",  "-density", "1200",output,  png])
    assert os.path.isfile(png)


def make_one_lab(args):
    i,conf = args

    lab = f"{DATE}_{i:04d}"
    if i >= START + n_labs:
        root[2][0][0].text = "DUMMY!"
        img = qrcode.make(lab)
        n_rep = 1
    else:
        root[2][0][0].text = lab
        img = qrcode.make(lab)
        n_rep = conf["N_REPS"]

    with io.BytesIO() as output:
        img.save(output, format="PNG")
        content = base64.b64encode(output.getbuffer())

    new_image = b"data:image/png;base64," + content
    root[2][2].attrib["{http://www.w3.org/1999/xlink}href"] = new_image.decode()

    for rep in range(n_rep):
        output = f"{conf["OUT_DIR"]}/{lab}-{rep}.svg"
        with open(output, "wb") as f:
            tree.write(f)
            convert(output)

for mode,conf in configs.items():
    os.makedirs(conf["OUT_DIR"],exist_ok=True)
    tree = ET.parse(conf["TEMPLATE"])
    root = tree.getroot()

    Parallel(n_jobs=1, prefer="processes")(
        delayed(make_one_lab)((i, conf))  for i in range(START, START+n_labs + conf["n_blanks"]))
    tmp_file = "/tmp/all_labels.png"
    command = f'montage {conf['OUT_DIR']}/{DATE}*.png -tile {conf["TILES"]} -geometry +0+0 {tmp_file}'
    print(command)
    os.system(command)
    command = f'mogrify -gravity center -extent  9763x14009 {tmp_file}'
    print(command)
    os.system(command)
    command = f'magick {tmp_file} -page a4 {DATE}_{mode}_labels.pdf'
    print(command)
    os.system(command)

    #for i in *.svg; do convert   -density 1200 $i  $(echo $i | sed s/svg/png/g); done
    #
    # #montage  2024-*.png  -tile 4x12   -geometry +0+0 all_labs.png
    # mogrify -gravity center -extent  9763x14009 all_labs.png && convert all_labs.png  -page a4 all_labs.pdf
    # #
