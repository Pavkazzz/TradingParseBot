# -*- coding: utf-8 -*-
import re

_transform_smiles = {
    """<span class="mfd-emoticon mfd-emoticon-smile"></span>""": "\U0001f642",
    """<span class="mfd-emoticon mfd-emoticon-sad"></span>""":  "\U0001f626",
    """<span class="mfd-emoticon mfd-emoticon-angry"></span>""": "\U0001f620",
    """<span class="mfd-emoticon mfd-emoticon-blank"></span>""": "\U0001f610",
    """<span class="mfd-emoticon mfd-emoticon-blink"></span>""": "\U0001f632",
    """<span class="mfd-emoticon mfd-emoticon-blush"></span>""": "\U0001f633",
    """<span class="mfd-emoticon mfd-emoticon-censored"></span>""": "\U0001f92C",
    """<span class="mfd-emoticon mfd-emoticon-cool"></span>""": "\U0001f60E",
    """<span class="mfd-emoticon mfd-emoticon-crazy"></span>""": "\U0001f616",
    """<span class="mfd-emoticon mfd-emoticon-dead"></span>""": "\U0001f635",
    """<span class="mfd-emoticon mfd-emoticon-dry"></span>""": "\U0001f60F",
    """<span class="mfd-emoticon mfd-emoticon-ermm"></span>""": "\U0001f612",
    """<span class="mfd-emoticon mfd-emoticon-facepalm"></span>""": "\U0001f926",
    """<span class="mfd-emoticon mfd-emoticon-grin"></span>""": "\U0001f601",
    """<span class="mfd-emoticon mfd-emoticon-happy"></span>""": "\U0001f60F",
    """<span class="mfd-emoticon mfd-emoticon-heart"></span>""": "\U00002764",
    """<span class="mfd-emoticon mfd-emoticon-huh"></span>""": "\U0001f914",
    """<span class="mfd-emoticon mfd-emoticon-laugh"></span>""": "\U0001f606",
    """<span class="mfd-emoticon mfd-emoticon-lol"></span>""": "\U0001f602",
    """<span class="mfd-emoticon mfd-emoticon-mad"></span>""": "\U0001f621",
    """<span class="mfd-emoticon mfd-emoticon-ninja"></span>""": "\U0001f47E",
    """<span class="mfd-emoticon mfd-emoticon-nuke"></span>""": "\U00002622",
    """<span class="mfd-emoticon mfd-emoticon-ohmy"></span>""": "\U0001f632",
    """<span class="mfd-emoticon mfd-emoticon-rolleyes"></span>""": "\U0001f60F",
    """<span class="mfd-emoticon mfd-emoticon-shiny"></span>""": "\U0001f60A",
    """<span class="mfd-emoticon mfd-emoticon-sick"></span>""": "\U0001F922",
    """<span class="mfd-emoticon mfd-emoticon-sleep"></span>""": "\U0001f634",
    """<span class="mfd-emoticon mfd-emoticon-tongue"></span>""": "\U0001f61b",
    """<span class="mfd-emoticon mfd-emoticon-unsure"></span>""": "\U0001f61f",
    """<span class="mfd-emoticon mfd-emoticon-wink"></span>""": "\U0001f609"
}


def transform_emoji(html):
    for key, val in _transform_smiles.items():
        html = html.replace(key, val)

    return html
