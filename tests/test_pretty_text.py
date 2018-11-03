# -*- coding: utf-8 -*-

from selectolax.parser import HTMLParser

from tests.conftest import TestSource
from trading_bot.sources import get_click_link_with_brackets


async def test_pretty_text():
    html = """<div class="mfd-quote-text"><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span></div><blockquote class="mfd-quote-14778526"><div class="mfd-quote-info"><a href="/forum/poster/?id=99552" rel="nofollow">chromatin</a> @ <a href="/forum/post/?id=14778526" rel="nofollow">19.07.2018 16:54</a></div><div class="mfd-quote-text">*TRUMP SAYS LOOKS FORWARD TO SECOND MEETING WITH PUTIN <br> Может быть, не надо. Второй такой встречи наш ФР может и не пережить 😁</div></blockquote>"""
    text = TestSource("http://mfd.ru").pretty_text(html)
    res = ("😁😁😁\n"
           "\n"
           "| [chromatin](https://clck.ru/EZw2D) @ [19.07.2018 16:54](https://clck.ru/EZw2E)\n"
           "|  \n"
           "|  \*TRUMP SAYS LOOKS FORWARD TO\n"
           "| SECOND MEETING WITH PUTIN  \n"
           "| Может быть, не надо. Второй такой\n"
           "| встречи наш ФР может и не пережить\n"
           "| 😁")

    assert text == res


async def test_title_with_title():
    html = """<a class="mfd-poster-link" href="/forum/poster/?id=88887" rel="nofollow" title="ID: 88887">Спокойный Скрудж Макдак</a>"""
    text = TestSource("http://mfd.ru").pretty_text(html)
    res = "[Спокойный Скрудж Макдак](https://clck.ru/EZvsG)"
    assert text == res


async def test_alenka_title_comment():
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
    bs = HTMLParser(html, "html.parser")
    parse = [str(p.html) for p in bs.css('.news__side, .news__name')]
    text = TestSource("https://alenka.capital").pretty_text(''.join(parse))
    res = ("06:36\n"
           "\n"
           "##  [ Х5 и \"Магнит\" двигают фигуры](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=https://alenka.capital/post/h5_i_magnit_dvigayut_figuryi_39017/)")
    assert res, text


async def test_mfd_title_comment():
    html = """<a href="http://forum.mfd.ru/blogs/posts/view/?id=37688" rel="nofollow">[Блоги] Июль</a>"""
    res = TestSource("http://mfd.ru").pretty_text(html)
    text = """[{Блоги} Июль](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://forum.mfd.ru/blogs/posts/view/?id=37688)"""
    assert res, text


async def test_link_text():
    html = '<div><div class="mfd-quote-text">от нзт, как скинули и на смарте поддержите плюсиками: <br>  <br> <a href="https://vk.com/nztrusfond?w=wall-165878204_639" rel="nofollow" target="_blank">https://vk.com/nztrusfond?w=wall-165878204_639</a> <br> <a href="https://smart-lab.ru/blog/483422.php" rel="nofollow" target="_blank">https://smart-lab.ru/blog/483422.php</a></div></div><button class="mfd-button-attention" data-id="14792209" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>'
    text = ("от нзт, как скинули и на смарте\n"
            "поддержите плюсиками:  \n"
            "  \n"
            "[https://vk.com/nztrusfond?w=wall-165878204_639](https://clck.ru/EZw8n)   \n"
            "[https://smart-lab.ru/blog/483422.php](https://clck.ru/EZw8o)")
    res = TestSource("http://mfd.ru").pretty_text(html)
    assert text == res


async def test_link_title_text():
    html = """<a class="mfd-poster-link" href="/forum/poster/?id=106833" rel="nofollow" title="ID: 106833">wolf_rider</a>"""
    res = TestSource("http://mfd.ru").pretty_text(html)
    assert res, "[wolf_rider](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=106833)"


async def test_dash():
    html = """<div>@Discl_Bot - бот, не канал, но удобный </div>"""
    text = TestSource("https://alenka.capital").pretty_text(html)
    res = ("@Discl\_Bot - бот, не канал, но\n"
           "удобный")
    assert text == res


async def test_smiles():
    html = """<span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span>"""
    text = TestSource("http://mfd.ru").pretty_text(html)
    res = "😁😁😁😁😁"
    assert text == res


async def test_dot():
    html = """Вот так просто взять и внести? <span class="mfd-emoticon mfd-emoticon-smile"></span> <br>  <br> <a href="http://www.consultant.ru/document/cons_doc_LAW_8743/9ca79eb480b2842d107d0fe21f8352b6b5e67916/" rel="nofollow" target="_blank">http://www.consultant.ru/document/cons_doc_LAW_...</a> <br> 1. Уставный капитал общества может быть увеличен путем увеличения номинальной стоимости акций или размещения дополнительных акций."""
    text = TestSource("http://mfd.ru").pretty_text(html)
    res = ("Вот так просто взять и внести? 🙂  \n"
           "  \n"
           "[http://www.consultant.ru/document/cons_doc_LAW_...](https://clck.ru/EZw2H)   \n"
           "1. Уставный капитал общества может\n"
           "быть увеличен путем увеличения\n"
           "номинальной стоимости акций или\n"
           "размещения дополнительных акций.")

    assert text == res


async def test_quote():
    html = """<div><blockquote class="mfd-quote-14819322"><div class="mfd-quote-info"><a href="/forum/poster/?id=58730" rel="nofollow">DflbvSv</a> @ <a href="/forum/post/?id=14819322" rel="nofollow">27.07.2018 14:30</a></div><blockquote class="mfd-quote-14818813"><div class="mfd-quote-info"><a href="/forum/poster/?id=72299" rel="nofollow">Volshebnik</a> @ <a href="/forum/post/?id=14818813" rel="nofollow">27.07.2018 13:15</a></div><div class="mfd-quote-text">Тем не менее бяка по 4 коп фундаментально оч дешева, вопрос только в том когда в стакан придут большие кошельки...</div></blockquote><div class="mfd-quote-text">Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% (<a href="https://news.rambler.ru/business/39911599-bank-otkrytie-peredal-binbanku-aktsii-vtb-za-40-mlrd-rub/" rel="nofollow" target="_blank">https://news.rambler.ru/business/39911599-bank-...</a>). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций</div></blockquote><div class="mfd-quote-text">Sehr gut!!! <br> В нашем полку прибыло<span class="mfd-emoticon mfd-emoticon-smile"></span> <br> <a href="http://lite.mfd.ru/forum/post/?id=14635042" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14635042</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=14467774" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14467774</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=13651199" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=13651199</a> <br> я тут уже давно толкую, что ФФ не тот, что указан у аналов и на сайте мосбиржи <br>  <br> если этот факт признать, то ВТБ надо немедленно отправить в эшелон... <br> а последствия для капы очевидны</div></div><button class="mfd-button-attention" data-id="14819412" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    text = TestSource("http://mfd.ru").pretty_text(html)
    res = (
        "| [DflbvSv](https://clck.ru/EZw2J) @ [27.07.2018 14:30](https://clck.ru/EZw2K)\n"
        "|\n"
        "| \n"
        "| | [Volshebnik](https://clck.ru/EZw2L) @ [27.07.2018 13:15](https://clck.ru/EZw2M)\n"
        "| |  \n"
        "| |  Тем не менее бяка по 4 коп\n"
        "| | фундаментально оч дешева, вопрос\n"
        "| | только в том когда в стакан придут\n"
        "| | большие кошельки...\n"
        "| | \n"
        "|  \n"
        "|  Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% ([https://news.rambler.ru/business/39911599-bank-...](https://clck.ru/EZw6P). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций\n"
        "\n"
        "Sehr gut!!!  \n"
        "В нашем полку прибыло🙂  \n"
        "[http://lite.mfd.ru/forum/post/?id=14635042](https://clck.ru/EZw2N)   \n"
        "[http://lite.mfd.ru/forum/post/?id=14467774](https://clck.ru/EZw2P)   \n"
        "[http://lite.mfd.ru/forum/post/?id=13651199](https://clck.ru/EZw2Q)   \n"
        "я тут уже давно толкую, что ФФ не\n"
        "тот, что указан у аналов и на\n"
        "сайте мосбиржи  \n"
        "  \n"
        "если этот факт признать, то ВТБ\n"
        "надо немедленно отправить в\n"
        "эшелон...  \n"
        "а последствия для капы очевидны")
    assert text == res


async def test_dot2():
    html = """<div><blockquote class="mfd-quote-14819862"><div class="mfd-quote-info"><a href="/forum/poster/?id=79103" rel="nofollow">Камаз Доходов</a> @ <a href="/forum/post/?id=14819862" rel="nofollow">27.07.2018 15:44</a></div><blockquote class="mfd-quote-14819835"><div class="mfd-quote-info"><a href="/forum/poster/?id=74012" rel="nofollow">калита</a> @ <a href="/forum/post/?id=14819835" rel="nofollow">27.07.2018 15:39</a></div><div class="mfd-quote-text">добро пожаловать ПФ РФ</div></blockquote><div class="mfd-quote-text">- ПФ РФ недавно отдали на разграбление Игорю Шувалову. <br> С чего ради вдруг он переведёт ПФ РФ из своего банка в ВТБ?</div></blockquote><div class="mfd-quote-text">Не про перевод речь, а про размещение акций ВТБ.</div></div><button class="mfd-button-attention" data-id="14819872" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    text = TestSource("http://mfd.ru").pretty_text(html)
    res = (
        "| [Камаз Доходов](https://clck.ru/EZw2R) @ [27.07.2018 15:44](https://clck.ru/EZw2S)\n"
        "|\n"
        "| \n"
        "| | [калита](https://clck.ru/EZw2T) @ [27.07.2018 15:39](https://clck.ru/EZw2U)\n"
        "| |  \n"
        "| |  добро пожаловать ПФ РФ\n"
        "| | \n"
        "|  \n"
        "|  - ПФ РФ недавно отдали на\n"
        "| разграбление Игорю Шувалову.  \n"
        "| С чего ради вдруг он переведёт ПФ\n"
        "| РФ из своего банка в ВТБ?\n"
        "\n"
        "Не про перевод речь, а про\n"
        "размещение акций ВТБ.")
    assert text == res


def test_links():
    html = """<div><blockquote class="mfd-quote-14819322"><div class="mfd-quote-info"><a href="/forum/poster/?id=58730" rel="nofollow">DflbvSv</a> @ <a href="/forum/post/?id=14819322" rel="nofollow">27.07.2018 14:30</a></div><blockquote class="mfd-quote-14818813"><div class="mfd-quote-info"><a href="/forum/poster/?id=72299" rel="nofollow">Volshebnik</a> @ <a href="/forum/post/?id=14818813" rel="nofollow">27.07.2018 13:15</a></div><div class="mfd-quote-text">Тем не менее бяка по 4 коп фундаментально оч дешева, вопрос только в том когда в стакан придут большие кошельки...</div></blockquote><div class="mfd-quote-text">Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% (<a href="https://news.rambler.ru/business/39911599-bank-otkrytie-peredal-binbanku-aktsii-vtb-za-40-mlrd-rub/" rel="nofollow" target="_blank">https://news.rambler.ru/business/39911599-bank-...</a>). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций</div></blockquote><div class="mfd-quote-text">Sehr gut!!! <br> В нашем полку прибыло<span class="mfd-emoticon mfd-emoticon-smile"></span> <br> <a href="http://lite.mfd.ru/forum/post/?id=14635042" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14635042</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=14467774" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14467774</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=13651199" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=13651199</a> <br> я тут уже давно толкую, что ФФ не тот, что указан у аналов и на сайте мосбиржи <br>  <br> если этот факт признать, то ВТБ надо немедленно отправить в эшелон... <br> а последствия для капы очевидны</div></div><button class="mfd-button-attention" data-id="14819412" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    res = """| [DflbvSv](https://clck.ru/EZw2J) @ [27.07.2018 14:30](https://clck.ru/EZw2K)
|
| 
| | [Volshebnik](https://clck.ru/EZw2L) @ [27.07.2018 13:15](https://clck.ru/EZw2M)
| |  
| |  Тем не менее бяка по 4 коп
| | фундаментально оч дешева, вопрос
| | только в том когда в стакан придут
| | большие кошельки...
| | 
|  
|  Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% ([https://news.rambler.ru/business/39911599-bank-...](https://clck.ru/EZw6P). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций

Sehr gut!!!  
В нашем полку прибыло🙂  
[http://lite.mfd.ru/forum/post/?id=14635042](https://clck.ru/EZw2N)   
[http://lite.mfd.ru/forum/post/?id=14467774](https://clck.ru/EZw2P)   
[http://lite.mfd.ru/forum/post/?id=13651199](https://clck.ru/EZw2Q)   
я тут уже давно толкую, что ФФ не
тот, что указан у аналов и на
сайте мосбиржи  
  
если этот факт признать, то ВТБ
надо немедленно отправить в
эшелон...  
а последствия для капы очевидны"""
    text = TestSource("http://mfd.ru").pretty_text(html)
    assert text == res


async def test_image():
    html = """<div><blockquote class="mfd-quote-15241410"><div class="mfd-quote-info"><a href="/forum/poster/?id=71373" rel="nofollow">Max__</a> @ <a href="/forum/post/?id=15241410" rel="nofollow">14.10.2018 09:24</a></div><div class="mfd-quote-text">Утро доброе народ, НЕ СПАМ! кто хочет купить книгу на Литрес но пока этого не сделал, цена или еще по каким другим причинам, вот вам промокод topadvert50autmn 50% скидка на одну покупку, Хорошая возможность приобрести Герасименко - "Финансовая отчетность для руководителей и начинающих специалистов." Всех благ, друзья, развивайтесь! <br>  <br> <a href="http://funkyimg.com/view/2M5Rs" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2M5Rs.png" alt="Показать в полный размер"></a></div></blockquote><div class="mfd-quote-text">Спасибо, но давно ещё скачал в ПДФ бесплатно =) Кому надо - пишите, скину.</div></div><button class="mfd-button-attention" data-id="15241463" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    res = """| [Max__](https://clck.ru/EZuxS) @ [14.10.2018 09:24](https://clck.ru/EZuxT)
|  
|  Утро доброе народ, НЕ СПАМ! кто
| хочет купить книгу на Литрес но
| пока этого не сделал, цена или еще
| по каким другим причинам, вот вам
| промокод topadvert50autmn 50%
| скидка на одну покупку, Хорошая
| возможность приобрести Герасименко
| - "Финансовая отчетность для
| руководителей и начинающих
| специалистов." Всех благ, друзья,
| развивайтесь!  
|   
| [Показать в полный размер](https://clck.ru/EZuaL)

Спасибо, но давно ещё скачал в ПДФ
бесплатно =) Кому надо - пишите,
скину."""

    md = TestSource("http://mfd.ru").pretty_text(html)
    assert md == res


async def test_multiple_image():
    html = """<div class="mfd-post-top"><div class="mfd-post-top-0" id="15276180"><a class="mfd-poster-link" href="/forum/poster/?id=87947" rel="nofollow" title="ID: 87947">Параноик</a></div><div class="mfd-post-top-1"><a class="mfd-post-link" href="http://forum.mfd.ru/forum/post/?id=15276180" rel="nofollow" title="Ссылка на это сообщение">21.10.2018 16:14</a></div><div class="mfd-post-top-4"><button class="mfd-button-quote" style="visibility: hidden;" type="button">&nbsp;</button></div><div class="mfd-post-top-2"><span id="mfdPostRating15276180">&nbsp;</span></div><div class="mfd-post-top-3 mfd-post-top-3-disabled"><form><label class="mfd-post-rate--1"><input data-id="15276180" data-status="1" data-vote="-1" name="ratePost" type="radio">−1</label><label class="mfd-post-rate-0" style="display: none;"><input data-id="15276180" data-status="1" data-vote="0" name="ratePost" type="radio">0</label><label class="mfd-post-rate-1"><input data-id="15276180" data-status="1" data-vote="1" name="ratePost" type="radio">+1</label></form></div><div class="mfd-clear"></div></div><table><tbody><tr><td class="mfd-post-body-left-container"><div class="mfd-post-body-left"><div class="mfd-post-avatar"><a href="/forum/poster/?id=87947" rel="nofollow" title="ID: 87947"><img alt="" src="http://forum.mfd.ru/forum/user/87947/avatar.jpg"></a></div><div class="mfdPosterInfoShort"><div class="mfd-poster-info-rating mfd-icon-profile-star"><a href="/forum/poster/rating/?id=87947" rel="nofollow" title="Детализация рейтинга (1207)">1207</a></div></div></div></td><td class="mfd-post-body-right-container"><div class="mfd-post-body-right"><div><div class="mfd-quote-text"><a href="http://funkyimg.com/view/2Mjij" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2Mjij.png" alt="Показать в полный размер"></a> <br>  <br> <a href="http://funkyimg.com/view/2Mjob" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2Mjob.png" alt="Показать в полный размер"></a> <br>  <br> <a href="http://funkyimg.com/view/2Mjp8" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2Mjp8.png" alt="Показать в полный размер"></a> <br>  <br> <span class="mfd-emoticon mfd-emoticon-smile"></span></div></div><button class="mfd-button-attention" data-id="15276180" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button></div></td></tr></tbody></table>"""
    res = ("[Параноик](https://clck.ru/EaGsv)\n"
           "\n"
           "[21.10.2018 16:14](https://clck.ru/EaHPW)\n"
           "\n"
           "\n"
           "\n"
           "\n"
           "\n"
           "−10+1\n"
           "\n"
           "[](https://clck.ru/EaGsv)\n"
           "\n"
           "[1207](https://clck.ru/EaHPZ)\n"
           "\n"
           "|\n"
           "\n"
           "[Показать в полный размер](https://clck.ru/EaHS9)   \n"
           "  \n"
           "[Показать в полный размер](https://clck.ru/EaHSA)   \n"
           "  \n"
           "[Показать в полный размер](https://clck.ru/EaHSB)   \n"
           "  \n"
           "🙂  \n"
           "  \n"
           "---|---")
    assert res == TestSource("http://mfd.ru").pretty_text(html)


async def test_russian_links():
    url = 'http://peretok.ru/articles/strategy/19079/ВИЭ'
    res = '(https://clck.ru/EYqGb)'
    assert res == get_click_link_with_brackets(url)
