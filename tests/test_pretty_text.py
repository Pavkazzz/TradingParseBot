# -*- coding: utf-8 -*-
from selectolax.parser import HTMLParser

from trading_bot.sources import AbstractSource, replace_url_for_chatbase


async def test_pretty_text():
    html = """<div class="mfd-quote-text"><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span></div><blockquote class="mfd-quote-14778526"><div class="mfd-quote-info"><a href="/forum/poster/?id=99552" rel="nofollow">chromatin</a> @ <a href="/forum/post/?id=14778526" rel="nofollow">19.07.2018 16:54</a></div><div class="mfd-quote-text">*TRUMP SAYS LOOKS FORWARD TO SECOND MEETING WITH PUTIN <br> Может быть, не надо. Второй такой встречи наш ФР может и не пережить 😁</div></blockquote>"""
    text = AbstractSource.pretty_text(html, "http://mfd.ru")
    res = ("😁😁😁\n"
           "\n"
           "| [chromatin](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=99552) @ [19.07.2018 16:54](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/post/?id=14778526)\n"
           "|  \n"
           "|  \*TRUMP SAYS LOOKS FORWARD TO\n"
           "| SECOND MEETING WITH PUTIN  \n"
           "| Может быть, не надо. Второй такой\n"
           "| встречи наш ФР может и не пережить\n"
           "| 😁")

    assert text == res


async def test_title_with_title():
    html = """<a class="mfd-poster-link" href="/forum/poster/?id=88887" rel="nofollow" title="ID: 88887">Спокойный Скрудж Макдак</a>"""
    text = AbstractSource.pretty_text(html, "http://mfd.ru")
    res = "[Спокойный Скрудж Макдак](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=88887)"
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
    text = AbstractSource.pretty_text(''.join(parse), "https://alenka.capital")
    res = ("06:36\n"
           "\n"
           "##  [ Х5 и \"Магнит\" двигают фигуры](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=https://alenka.capital/post/h5_i_magnit_dvigayut_figuryi_39017/)")
    assert res, text


async def test_mfd_title_comment():
    html = """<a href="http://forum.mfd.ru/blogs/posts/view/?id=37688" rel="nofollow">[Блоги] Июль</a>"""
    res = AbstractSource.pretty_text(html, "http://mfd.ru")
    text = """[{Блоги} Июль](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://forum.mfd.ru/blogs/posts/view/?id=37688)"""
    assert res, text


async def test_link_text():
    html = '<div><div class="mfd-quote-text">от нзт, как скинули и на смарте поддержите плюсиками: <br>  <br> <a href="https://vk.com/nztrusfond?w=wall-165878204_639" rel="nofollow" target="_blank">https://vk.com/nztrusfond?w=wall-165878204_639</a> <br> <a href="https://smart-lab.ru/blog/483422.php" rel="nofollow" target="_blank">https://smart-lab.ru/blog/483422.php</a></div></div><button class="mfd-button-attention" data-id="14792209" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>'
    text = ("от нзт, как скинули и на смарте\n"
            "поддержите плюсиками:  \n"
            "  \n"
            "[https://vk.com/nztrusfond?w=wall-165878204_639](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=https://vk.com/nztrusfond?w=wall-165878204_639)   \n"
            "[https://smart-lab.ru/blog/483422.php](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=https://smart-lab.ru/blog/483422.php)")
    res = AbstractSource.pretty_text(html, "http://mfd.ru")
    assert text == res


async def test_link_title_text():
    html = """<a class="mfd-poster-link" href="/forum/poster/?id=106833" rel="nofollow" title="ID: 106833">wolf_rider</a>"""
    res = AbstractSource.pretty_text(html, "http://mfd.ru")
    assert res, "[wolf_rider](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=106833)"


async def test_dash():
    html = """<div>@Discl_Bot - бот, не канал, но удобный </div>"""
    text = AbstractSource.pretty_text(html, "https://alenka.capital")
    res = ("@Discl\_Bot - бот, не канал, но\n"
           "удобный")
    assert text == res


async def test_smiles():
    html = """<span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span>"""
    text = AbstractSource.pretty_text(html, "http://mfd.ru")
    res = "😁😁😁😁😁"
    assert text == res


async def test_dot():
    html = """Вот так просто взять и внести? <span class="mfd-emoticon mfd-emoticon-smile"></span> <br>  <br> <a href="http://www.consultant.ru/document/cons_doc_LAW_8743/9ca79eb480b2842d107d0fe21f8352b6b5e67916/" rel="nofollow" target="_blank">http://www.consultant.ru/document/cons_doc_LAW_...</a> <br> 1. Уставный капитал общества может быть увеличен путем увеличения номинальной стоимости акций или размещения дополнительных акций."""
    text = AbstractSource.pretty_text(html, "http://mfd.ru")
    res = ("Вот так просто взять и внести? 🙂  \n"
           "  \n"
           "[http://www.consultant.ru/document/cons_doc_LAW_...](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://www.consultant.ru/document/cons_doc_LAW_8743/9ca79eb480b2842d107d0fe21f8352b6b5e67916/)   \n"
           "1. Уставный капитал общества может\n"
           "быть увеличен путем увеличения\n"
           "номинальной стоимости акций или\n"
           "размещения дополнительных акций.")

    assert text == res


async def test_quote():
    html = """<div><blockquote class="mfd-quote-14819322"><div class="mfd-quote-info"><a href="/forum/poster/?id=58730" rel="nofollow">DflbvSv</a> @ <a href="/forum/post/?id=14819322" rel="nofollow">27.07.2018 14:30</a></div><blockquote class="mfd-quote-14818813"><div class="mfd-quote-info"><a href="/forum/poster/?id=72299" rel="nofollow">Volshebnik</a> @ <a href="/forum/post/?id=14818813" rel="nofollow">27.07.2018 13:15</a></div><div class="mfd-quote-text">Тем не менее бяка по 4 коп фундаментально оч дешева, вопрос только в том когда в стакан придут большие кошельки...</div></blockquote><div class="mfd-quote-text">Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% (<a href="https://news.rambler.ru/business/39911599-bank-otkrytie-peredal-binbanku-aktsii-vtb-za-40-mlrd-rub/" rel="nofollow" target="_blank">https://news.rambler.ru/business/39911599-bank-...</a>). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций</div></blockquote><div class="mfd-quote-text">Sehr gut!!! <br> В нашем полку прибыло<span class="mfd-emoticon mfd-emoticon-smile"></span> <br> <a href="http://lite.mfd.ru/forum/post/?id=14635042" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14635042</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=14467774" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14467774</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=13651199" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=13651199</a> <br> я тут уже давно толкую, что ФФ не тот, что указан у аналов и на сайте мосбиржи <br>  <br> если этот факт признать, то ВТБ надо немедленно отправить в эшелон... <br> а последствия для капы очевидны</div></div><button class="mfd-button-attention" data-id="14819412" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    text = AbstractSource.pretty_text(html, "http://mfd.ru")
    res = (
        "| [DflbvSv](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=58730) @ [27.07.2018 14:30](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/post/?id=14819322)\n"
        "|\n"
        "| \n"
        "| | [Volshebnik](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=72299) @ [27.07.2018 13:15](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/post/?id=14818813)\n"
        "| |  \n"
        "| |  Тем не менее бяка по 4 коп\n"
        "| | фундаментально оч дешева, вопрос\n"
        "| | только в том когда в стакан придут\n"
        "| | большие кошельки...\n"
        "| | \n"
        "|  \n"
        "|  Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% ([https://news.rambler.ru/business/39911599-bank-...](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=https://news.rambler.ru/business/39911599-bank-otkrytie-peredal-binbanku-aktsii-vtb-za-40-mlrd-rub/)). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций\n"
        "\n"
        "Sehr gut!!!  \n"
        "В нашем полку прибыло🙂  \n"
        "[http://lite.mfd.ru/forum/post/?id=14635042](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/forum/post/?id=14635042)   \n"
        "[http://lite.mfd.ru/forum/post/?id=14467774](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/forum/post/?id=14467774)   \n"
        "[http://lite.mfd.ru/forum/post/?id=13651199](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/forum/post/?id=13651199)   \n"
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
    text = AbstractSource.pretty_text(html, "http://mfd.ru")
    res = (
        "| [Камаз Доходов](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=79103) @ [27.07.2018 15:44](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/post/?id=14819862)\n"
        "|\n"
        "| \n"
        "| | [калита](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=74012) @ [27.07.2018 15:39](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/post/?id=14819835)\n"
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
    res = """| [DflbvSv](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=58730) @ [27.07.2018 14:30](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/post/?id=14819322)
|
| 
| | [Volshebnik](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=72299) @ [27.07.2018 13:15](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/post/?id=14818813)
| |  
| |  Тем не менее бяка по 4 коп
| | фундаментально оч дешева, вопрос
| | только в том когда в стакан придут
| | большие кошельки...
| | 
|  
|  Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% ([https://news.rambler.ru/business/39911599-bank-...](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=https://news.rambler.ru/business/39911599-bank-otkrytie-peredal-binbanku-aktsii-vtb-za-40-mlrd-rub/)). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций

Sehr gut!!!  
В нашем полку прибыло🙂  
[http://lite.mfd.ru/forum/post/?id=14635042](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/forum/post/?id=14635042)   
[http://lite.mfd.ru/forum/post/?id=14467774](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/forum/post/?id=14467774)   
[http://lite.mfd.ru/forum/post/?id=13651199](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://lite.mfd.ru/forum/post/?id=13651199)   
я тут уже давно толкую, что ФФ не
тот, что указан у аналов и на
сайте мосбиржи  
  
если этот факт признать, то ВТБ
надо немедленно отправить в
эшелон...  
а последствия для капы очевидны"""
    text = AbstractSource.pretty_text(html, "http://mfd.ru")
    assert text == res


async def test_image():
    html = """<div><blockquote class="mfd-quote-15241410"><div class="mfd-quote-info"><a href="/forum/poster/?id=71373" rel="nofollow">Max__</a> @ <a href="/forum/post/?id=15241410" rel="nofollow">14.10.2018 09:24</a></div><div class="mfd-quote-text">Утро доброе народ, НЕ СПАМ! кто хочет купить книгу на Литрес но пока этого не сделал, цена или еще по каким другим причинам, вот вам промокод topadvert50autmn 50% скидка на одну покупку, Хорошая возможность приобрести Герасименко - "Финансовая отчетность для руководителей и начинающих специалистов." Всех благ, друзья, развивайтесь! <br>  <br> <a href="http://funkyimg.com/view/2M5Rs" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2M5Rs.png" alt="Показать в полный размер"></a></div></blockquote><div class="mfd-quote-text">Спасибо, но давно ещё скачал в ПДФ бесплатно =) Кому надо - пишите, скину.</div></div><button class="mfd-button-attention" data-id="15241463" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    print(AbstractSource.pretty_text(html, "http://mfd.ru"))