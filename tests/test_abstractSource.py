from unittest import TestCase
from sources import MfdUserPostSource

class TestAbstractSource(TestCase):
    def test_pretty_text(self):
        source = MfdUserPostSource()
        html = """<div class="mfd-quote-text"><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span></div><blockquote class="mfd-quote-14778526"><div class="mfd-quote-info"><a href="/forum/poster/?id=99552" rel="nofollow">chromatin</a> @ <a href="/forum/post/?id=14778526" rel="nofollow">19.07.2018 16:54</a></div><div class="mfd-quote-text">*TRUMP SAYS LOOKS FORWARD TO SECOND MEETING WITH PUTIN <br> Может быть, не надо. Второй такой встречи наш ФР может и не пережить 😁</div></blockquote>"""
        text = source.pretty_text(html, "http://mfd.ru")
        res = (
            "| [chromatin](http://mfd.ru/forum/poster/?id=99552) @ [19.07.2018 16:54](http://mfd.ru/forum/post/?id=14778526)\n"
            "|  \n"
            "|  *TRUMP SAYS LOOKS FORWARD TO SECOND*\n"
            "| MEETING WITH PUTIN  \n"
            "| Может быть, не надо. Второй такой\n"
            "| встречи наш ФР может и не пережить 😁")

        self.assertEqual(text, res)

