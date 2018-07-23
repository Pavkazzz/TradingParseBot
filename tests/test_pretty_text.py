from unittest import TestCase
from sources import AbstractSource
from bs4 import BeautifulSoup


class TestAbstractSource(TestCase):
    def test_pretty_text(self):
        html = """<div class="mfd-quote-text"><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span></div><blockquote class="mfd-quote-14778526"><div class="mfd-quote-info"><a href="/forum/poster/?id=99552" rel="nofollow">chromatin</a> @ <a href="/forum/post/?id=14778526" rel="nofollow">19.07.2018 16:54</a></div><div class="mfd-quote-text">*TRUMP SAYS LOOKS FORWARD TO SECOND MEETING WITH PUTIN <br> Может быть, не надо. Второй такой встречи наш ФР может и не пережить 😁</div></blockquote>"""
        text = AbstractSource.pretty_text(html, "http://mfd.ru")
        res = (
            "| [chromatin](http://mfd.ru/forum/poster/?id=99552) @ [19.07.2018 16:54](http://mfd.ru/forum/post/?id=14778526)\n"
            "|  \n"
            "|  *TRUMP SAYS LOOKS FORWARD TO SECOND*\n"
            "| MEETING WITH PUTIN  \n"
            "| Может быть, не надо. Второй такой\n"
            "| встречи наш ФР может и не пережить 😁")

        self.assertEqual(text, res)

    def test_title_with_title(self):
        html = """<a class="mfd-poster-link" href="/forum/poster/?id=88887" rel="nofollow" title="ID: 88887">Спокойный Скрудж Макдак</a>"""
        text = AbstractSource.pretty_text(html, "http://mfd.ru")
        res = "[Спокойный Скрудж Макдак](http://mfd.ru/forum/poster/?id=88887)"
        self.assertEqual(text, res)

    def test_alenka_title_comment(self):
        html = ("<li class=\"news__item\">\n"
                "<div class=\"news__counter\">\n"
                "<a href=\"/post/h5_i_magnit_dvigayut_figuryi_39017/?comment\" title=\"1 комментарий\">1</a>\n"
                "</div>\n"
                "<div class=\"news__side\">\n"
                "<time class=\"news__date\">06:36</time>\n"
                "</div>\n"
                "<div class=\"news__main\">\n"
                "<h2 class=\"news__name\">\n"
                "<a class=\"news__link\" href=\"/post/h5_i_magnit_dvigayut_figuryi_39017/\"> Х5 и \"Магнит\" двигают фигуры</a> </h2>\n"
                "</div>\n"
                "</li>")
        bs = BeautifulSoup(html, "html.parser")
        parse = [str(p) for p in bs.select('.news__side, .news__name')]
        text = AbstractSource.pretty_text(''.join(parse), "https://alenka.capital")
        res = ("06:36\n"
               "\n"
               "##  [ Х5 и \"Магнит\" двигают фигуры](https://alenka.capital/post/h5_i_magnit_dvigayut_figuryi_39017/)")
        self.assertEqual(res, text)

    def test_mfd_title_comment(self):
        html = """<a href="http://forum.mfd.ru/blogs/posts/view/?id=37688" rel="nofollow">[Блоги] Июль</a>"""
        res = AbstractSource.pretty_text(html, "http://mfd.ru")
        text = """[{Блоги} Июль](http://forum.mfd.ru/blogs/posts/view/?id=37688)"""
        self.assertEqual(res, text)

    def test_link_text(self):
        html = '<div><div class="mfd-quote-text">от нзт, как скинули и на смарте поддержите плюсиками: <br>  <br> <a href="https://vk.com/nztrusfond?w=wall-165878204_639" rel="nofollow" target="_blank">https://vk.com/nztrusfond?w=wall-165878204_639</a> <br> <a href="https://smart-lab.ru/blog/483422.php" rel="nofollow" target="_blank">https://smart-lab.ru/blog/483422.php</a></div></div><button class="mfd-button-attention" data-id="14792209" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>'
        res = AbstractSource.pretty_text(html, "http://mfd.ru")
        print(res)