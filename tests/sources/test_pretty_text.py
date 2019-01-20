# -*- coding: utf-8 -*-
from selectolax.parser import HTMLParser

from tests.conftest import EmptyTestSource
from trading_bot.sources.sources import MarkdownFormatter


async def test_pretty_text():
    html = """<div class="mfd-quote-text"><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span></div><blockquote class="mfd-quote-14778526"><div class="mfd-quote-info"><a href="/forum/poster/?id=99552" rel="nofollow">chromatin</a> @ <a href="/forum/post/?id=14778526" rel="nofollow">19.07.2018 16:54</a></div><div class="mfd-quote-text">*TRUMP SAYS LOOKS FORWARD TO SECOND MEETING WITH PUTIN <br> Может быть, не надо. Второй такой встречи наш ФР может и не пережить 😁</div></blockquote>"""
    text = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    res = (
        "😁😁😁\n"
        "\n"
        "| [chromatin](http://mfd.ru/forum/poster/?id=99552) @ [19.07.2018 16:54](http://mfd.ru/forum/post/?id=14778526)\n"
        "|  \n"
        "|  \*TRUMP SAYS LOOKS FORWARD TO\n"
        "| SECOND MEETING WITH PUTIN  \n"
        "| Может быть, не надо. Второй такой\n"
        "| встречи наш ФР может и не пережить\n"
        "| 😁"
    )

    assert text == res


async def test_title_with_title():
    html = """<a class="mfd-poster-link" href="/forum/poster/?id=88887" rel="nofollow" title="ID: 88887">Спокойный Скрудж Макдак</a>"""
    text = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    res = "[Спокойный Скрудж Макдак](http://mfd.ru/forum/poster/?id=88887)"
    assert text == res


async def test_alenka_title_comment():
    html = (
        '<li class="news__item">\n'
        '<div class="news__counter">\n'
        '<a href="/post/h5_i_magnit_dvigayut_figuryi_39017/?comment" title="1 комментарий">1</a>\n'
        "</div>\n"
        '<div class="news__side">\n'
        '<time class="news__date">06:36</time>\n'
        "</div>\n"
        '<div class="news__main">\n'
        '<h2 class="news__name">\n'
        '<a class="news__link" href="/post/h5_i_magnit_dvigayut_figuryi_39017/"> Х5 и "Магнит" двигают фигуры</a> </h2>\n'
        "</div>\n"
        "</li>"
    )
    bs = HTMLParser(html, "html.parser")
    parse = [str(p.html) for p in bs.css(".news__side, .news__name")]
    text = await EmptyTestSource("https://alenka.capital").pretty_text(
        "".join(parse))
    res = (
        "06:36\n"
        "\n"
        '##  [ Х5 и "Магнит" двигают фигуры](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=https://alenka.capital/post/h5_i_magnit_dvigayut_figuryi_39017/)'
    )
    assert res, text


async def test_mfd_title_comment():
    html = """<a href="http://forum.mfd.ru/blogs/posts/view/?id=37688" rel="nofollow">[Блоги] Июль</a>"""
    res = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    text = """[{Блоги} Июль](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://forum.mfd.ru/blogs/posts/view/?id=37688)"""
    assert res, text


async def test_link_text():
    html = '<div><div class="mfd-quote-text">от нзт, как скинули и на смарте поддержите плюсиками: <br>  <br> <a href="https://vk.com/nztrusfond?w=wall-165878204_639" rel="nofollow" target="_blank">https://vk.com/nztrusfond?w=wall-165878204_639</a> <br> <a href="https://smart-lab.ru/blog/483422.php" rel="nofollow" target="_blank">https://smart-lab.ru/blog/483422.php</a></div></div><button class="mfd-button-attention" data-id="14792209" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>'
    text = (
        "от нзт, как скинули и на смарте\n"
        "поддержите плюсиками:  \n"
        "  \n"
        "[https://vk.com/nztrusfond?w=wall-165878204_639](https://vk.com/nztrusfond?w=wall-165878204_639)   \n"
        "[https://smart-lab.ru/blog/483422.php](https://smart-lab.ru/blog/483422.php)"
    )
    res = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    assert text == res


async def test_link_title_text():
    html = """<a class="mfd-poster-link" href="/forum/poster/?id=106833" rel="nofollow" title="ID: 106833">wolf_rider</a>"""
    res = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    assert (
        res
    ), "[wolf_rider](https://chatbase.com/r?api_key=dd11ff93-afcc-4253-ba2e-72fec6e46a35&platform=Telegram&url=http://mfd.ru/forum/poster/?id=106833)"


async def test_dash():
    html = """<div>@Discl_Bot - бот, не канал, но удобный </div>"""
    text = await EmptyTestSource("https://alenka.capital").pretty_text(html)
    res = (
        "@Discl\_Bot - бот, не канал, но\n"
        "удобный"
    )
    assert text == res


async def test_smiles():
    html = """<span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span><span class="mfd-emoticon mfd-emoticon-grin"></span>"""
    text = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    res = "😁😁😁😁😁"
    assert text == res


async def test_dot():
    html = """Вот так просто взять и внести? <span class="mfd-emoticon mfd-emoticon-smile"></span> <br>  <br> <a href="http://www.consultant.ru/document/cons_doc_LAW_8743/9ca79eb480b2842d107d0fe21f8352b6b5e67916/" rel="nofollow" target="_blank">http://www.consultant.ru/document/cons_doc_LAW_...</a> <br> 1. Уставный капитал общества может быть увеличен путем увеличения номинальной стоимости акций или размещения дополнительных акций."""
    text = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    res = (
        "Вот так просто взять и внести? 🙂  \n"
        "  \n"
        "[http://www.consultant.ru/document/cons_doc_LAW_...](http://www.consultant.ru/document/cons_doc_LAW_8743/9ca79eb480b2842d107d0fe21f8352b6b5e67916/)   \n"
        "1. Уставный капитал общества может\n"
        "быть увеличен путем увеличения\n"
        "номинальной стоимости акций или\n"
        "размещения дополнительных акций."
    )

    assert text == res


async def test_quote():
    html = """<div><blockquote class="mfd-quote-14819322"><div class="mfd-quote-info"><a href="/forum/poster/?id=58730" rel="nofollow">DflbvSv</a> @ <a href="/forum/post/?id=14819322" rel="nofollow">27.07.2018 14:30</a></div><blockquote class="mfd-quote-14818813"><div class="mfd-quote-info"><a href="/forum/poster/?id=72299" rel="nofollow">Volshebnik</a> @ <a href="/forum/post/?id=14818813" rel="nofollow">27.07.2018 13:15</a></div><div class="mfd-quote-text">Тем не менее бяка по 4 коп фундаментально оч дешева, вопрос только в том когда в стакан придут большие кошельки...</div></blockquote><div class="mfd-quote-text">Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% (<a href="https://news.rambler.ru/business/39911599-bank-otkrytie-peredal-binbanku-aktsii-vtb-za-40-mlrd-rub/" rel="nofollow" target="_blank">https://news.rambler.ru/business/39911599-bank-...</a>). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций</div></blockquote><div class="mfd-quote-text">Sehr gut!!! <br> В нашем полку прибыло<span class="mfd-emoticon mfd-emoticon-smile"></span> <br> <a href="http://lite.mfd.ru/forum/post/?id=14635042" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14635042</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=14467774" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=14467774</a> <br> <a href="http://lite.mfd.ru/forum/post/?id=13651199" rel="nofollow" target="_blank">http://lite.mfd.ru/forum/post/?id=13651199</a> <br> я тут уже давно толкую, что ФФ не тот, что указан у аналов и на сайте мосбиржи <br>  <br> если этот факт признать, то ВТБ надо немедленно отправить в эшелон... <br> а последствия для капы очевидны</div></div><button class="mfd-button-attention" data-id="14819412" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    text = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    res = (
        "| [DflbvSv](http://mfd.ru/forum/poster/?id=58730) @ [27.07.2018 14:30](http://mfd.ru/forum/post/?id=14819322)\n"
        "|\n"
        "| \n"
        "| | [Volshebnik](http://mfd.ru/forum/poster/?id=72299) @ [27.07.2018 13:15](http://mfd.ru/forum/post/?id=14818813)\n"
        "| |  \n"
        "| |  Тем не менее бяка по 4 коп\n"
        "| | фундаментально оч дешева, вопрос\n"
        "| | только в том когда в стакан придут\n"
        "| | большие кошельки...\n"
        "| | \n"
        "|  \n"
        "|  Открывашка попыталась, скупив почти 14% голосующих акций, но, судя по всему, надорвалась. После 24 мая у открывашки 7,8%, у собрата по несчастью (Бинбанка) - 5,99% ([https://news.rambler.ru/business/39911599-bank-...](https://news.rambler.ru/business/39911599-bank-otkrytie-peredal-binbanku-aktsii-vtb-za-40-mlrd-rub/)). Исходя из свободного обращения на рынке 15% акций, то получается, что на рынке идет торговля 1,21% акций\n"
        "\n"
        "Sehr gut!!!  \n"
        "В нашем полку прибыло🙂  \n"
        "[http://lite.mfd.ru/forum/post/?id=14635042](http://lite.mfd.ru/forum/post/?id=14635042)   \n"
        "[http://lite.mfd.ru/forum/post/?id=14467774](http://lite.mfd.ru/forum/post/?id=14467774)   \n"
        "[http://lite.mfd.ru/forum/post/?id=13651199](http://lite.mfd.ru/forum/post/?id=13651199)   \n"
        "я тут уже давно толкую, что ФФ не\n"
        "тот, что указан у аналов и на сайте\n"
        "мосбиржи  \n"
        "  \n"
        "если этот факт признать, то ВТБ надо\n"
        "немедленно отправить в эшелон...  \n"
        "а последствия для капы очевидны"
    )
    assert text == res


async def test_dot2():
    html = """<div><blockquote class="mfd-quote-14819862"><div class="mfd-quote-info"><a href="/forum/poster/?id=79103" rel="nofollow">Камаз Доходов</a> @ <a href="/forum/post/?id=14819862" rel="nofollow">27.07.2018 15:44</a></div><blockquote class="mfd-quote-14819835"><div class="mfd-quote-info"><a href="/forum/poster/?id=74012" rel="nofollow">калита</a> @ <a href="/forum/post/?id=14819835" rel="nofollow">27.07.2018 15:39</a></div><div class="mfd-quote-text">добро пожаловать ПФ РФ</div></blockquote><div class="mfd-quote-text">- ПФ РФ недавно отдали на разграбление Игорю Шувалову. <br> С чего ради вдруг он переведёт ПФ РФ из своего банка в ВТБ?</div></blockquote><div class="mfd-quote-text">Не про перевод речь, а про размещение акций ВТБ.</div></div><button class="mfd-button-attention" data-id="14819872" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    text = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    res = (
        "| [Камаз Доходов](http://mfd.ru/forum/poster/?id=79103) @ [27.07.2018 15:44](http://mfd.ru/forum/post/?id=14819862)\n"
        "|\n"
        "| \n"
        "| | [калита](http://mfd.ru/forum/poster/?id=74012) @ [27.07.2018 15:39](http://mfd.ru/forum/post/?id=14819835)\n"
        "| |  \n"
        "| |  добро пожаловать ПФ РФ\n"
        "| | \n"
        "|  \n"
        "|  - ПФ РФ недавно отдали на\n"
        "| разграбление Игорю Шувалову.  \n"
        "| С чего ради вдруг он переведёт ПФ РФ\n"
        "| из своего банка в ВТБ?\n"
        "\n"
        "Не про перевод речь, а про\n"
        "размещение акций ВТБ."
    )
    assert text == res


async def test_image():
    html = """<div><blockquote class="mfd-quote-15241410"><div class="mfd-quote-info"><a href="/forum/poster/?id=71373" rel="nofollow">Max__</a> @ <a href="/forum/post/?id=15241410" rel="nofollow">14.10.2018 09:24</a></div><div class="mfd-quote-text">Утро доброе народ, НЕ СПАМ! кто хочет купить книгу на Литрес но пока этого не сделал, цена или еще по каким другим причинам, вот вам промокод topadvert50autmn 50% скидка на одну покупку, Хорошая возможность приобрести Герасименко - "Финансовая отчетность для руководителей и начинающих специалистов." Всех благ, друзья, развивайтесь! <br>  <br> <a href="http://funkyimg.com/view/2M5Rs" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2M5Rs.png" alt="Показать в полный размер"></a></div></blockquote><div class="mfd-quote-text">Спасибо, но давно ещё скачал в ПДФ бесплатно =) Кому надо - пишите, скину.</div></div><button class="mfd-button-attention" data-id="15241463" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>"""
    res = (
        "| [Max__](http://mfd.ru/forum/poster/?id=71373) @ [14.10.2018 09:24](http://mfd.ru/forum/post/?id=15241410)\n"
        "|  \n"
        "|  Утро доброе народ, НЕ СПАМ! кто\n"
        "| хочет купить книгу на Литрес но пока\n"
        "| этого не сделал, цена или еще по\n"
        "| каким другим причинам, вот вам\n"
        "| промокод topadvert50autmn 50%\n"
        "| скидка на одну покупку, Хорошая\n"
        "| возможность приобрести\n"
        "| Герасименко - \"Финансовая\n"
        "| отчетность для руководителей и\n"
        "| начинающих специалистов.\" Всех\n"
        "| благ, друзья, развивайтесь!  \n"
        "|   \n"
        "| [Показать в полный размер](http://funkyimg.com/view/2M5Rs)\n"
        "\n"
        "Спасибо, но давно ещё скачал в ПДФ\n"
        "бесплатно =) Кому надо - пишите,\n"
        "скину."
    )

    md = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    assert md == res


async def test_multiple_image():
    html = """<div class="mfd-post-top"><div class="mfd-post-top-0" id="15276180"><a class="mfd-poster-link" href="/forum/poster/?id=87947" rel="nofollow" title="ID: 87947">Параноик</a></div><div class="mfd-post-top-1"><a class="mfd-post-link" href="http://forum.mfd.ru/forum/post/?id=15276180" rel="nofollow" title="Ссылка на это сообщение">21.10.2018 16:14</a></div><div class="mfd-post-top-4"><button class="mfd-button-quote" style="visibility: hidden;" type="button">&nbsp;</button></div><div class="mfd-post-top-2"><span id="mfdPostRating15276180">&nbsp;</span></div><div class="mfd-post-top-3 mfd-post-top-3-disabled"><form><label class="mfd-post-rate--1"><input data-id="15276180" data-status="1" data-vote="-1" name="ratePost" type="radio">−1</label><label class="mfd-post-rate-0" style="display: none;"><input data-id="15276180" data-status="1" data-vote="0" name="ratePost" type="radio">0</label><label class="mfd-post-rate-1"><input data-id="15276180" data-status="1" data-vote="1" name="ratePost" type="radio">+1</label></form></div><div class="mfd-clear"></div></div><table><tbody><tr><td class="mfd-post-body-left-container"><div class="mfd-post-body-left"><div class="mfd-post-avatar"><a href="/forum/poster/?id=87947" rel="nofollow" title="ID: 87947"><img alt="" src="http://forum.mfd.ru/forum/user/87947/avatar.jpg"></a></div><div class="mfdPosterInfoShort"><div class="mfd-poster-info-rating mfd-icon-profile-star"><a href="/forum/poster/rating/?id=87947" rel="nofollow" title="Детализация рейтинга (1207)">1207</a></div></div></div></td><td class="mfd-post-body-right-container"><div class="mfd-post-body-right"><div><div class="mfd-quote-text"><a href="http://funkyimg.com/view/2Mjij" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2Mjij.png" alt="Показать в полный размер"></a> <br>  <br> <a href="http://funkyimg.com/view/2Mjob" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2Mjob.png" alt="Показать в полный размер"></a> <br>  <br> <a href="http://funkyimg.com/view/2Mjp8" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2Mjp8.png" alt="Показать в полный размер"></a> <br>  <br> <span class="mfd-emoticon mfd-emoticon-smile"></span></div></div><button class="mfd-button-attention" data-id="15276180" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button></div></td></tr></tbody></table>"""
    res = (
        "[Параноик](http://mfd.ru/forum/poster/?id=87947)\n"
        "\n"
        "[21.10.2018 16:14](http://forum.mfd.ru/forum/post/?id=15276180)\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "\n"
        "−10+1\n"
        "\n"
        "[](http://mfd.ru/forum/poster/?id=87947)\n"
        "\n"
        "[1207](http://mfd.ru/forum/poster/rating/?id=87947)\n"
        "\n"
        "|\n"
        "\n"
        "[Показать в полный размер](http://funkyimg.com/view/2Mjij)   \n"
        "  \n"
        "[Показать в полный размер](http://funkyimg.com/view/2Mjob)   \n"
        "  \n"
        "[Показать в полный размер](http://funkyimg.com/view/2Mjp8)   \n"
        "  \n"
        "🙂  \n"
        "  \n"
        "---|---"
    )
    assert res == await EmptyTestSource("http://mfd.ru").pretty_text(html)


async def test_russian_links(redis):
    url = "http://peretok.ru/articles/strategy/19079/ВИЭ"
    res = "https://clck.ru/F54uE"
    assert res == (
        await MarkdownFormatter(None, redis=redis).get_shorten_link(url)
    )[1]


async def test_nzt_links():
    link = "https://vk.com/@nztrusfond-obzor-portfelya-po-rezultatam-oktyabrya"
    assert (await MarkdownFormatter(None).get_shorten_link(url=link))[1] == link


async def test_quoting():
    html = """<div class="mfd-post-body-right"><div><blockquote class="mfd-quote-15384866"><div class="mfd-quote-info"><a href="/forum/poster/?id=110132" rel="nofollow">Тул Равий</a> @ <a href="/forum/post/?id=15384866" rel="nofollow">09.11.2018 15:12</a></div><div class="mfd-quote-text">Пришел. Включил. Подумал. <br> Что, мол, таки да - накаркал.</div><blockquote class="mfd-quote-15372976"><div class="mfd-quote-info"><a href="/forum/poster/?id=110132" rel="nofollow">Тул Равий</a> @ <a href="/forum/post/?id=15372976" rel="nofollow">07.11.2018 22:33</a></div><div class="mfd-quote-text">Коррекция неминуема как победа пролетарской революции. Ибо.  <br> Во-первых: мне пора опять закупиться, потому, что «те, что были на прошлой неделе мы уже съели» (доедал сегодня, осталось немного и ВТБ, между прочим).  <br> Во-вторых,   <br> ... <br> Из того, что попадемся. Мы — попадемся в принципе.</div></blockquote><blockquote class="mfd-quote-15358318"><div class="mfd-quote-info"><a href="/forum/poster/?id=110132" rel="nofollow">Тул Равий</a> @ <a href="/forum/post/?id=15358318" rel="nofollow">05.11.2018 19:05</a></div><div class="mfd-quote-text">... нефть сколько стоить будет в декабре в след году?, <br> - Год длинный. ИМХО, в целом, не выше 80. Скорее около 70, как бы не ниже. Но не ниже 60. Это и удобная цена для сланцевиков. Лично я ориентируюсь на эти цифры. В 100 не верю. Даже в 90. Потом - да. Но больше по причине повышения себестоимости добычи в целом.  Нас, кстати, это касается чуть ли не в первую очередь. С Ираном до конца 2019, так или иначе, разрулят.</div></blockquote><div class="mfd-quote-text">Вот только брать, ИМХО, еще нечего... Так, по ощущениям (ибо с математикой - "не очень").</div></blockquote><div class="mfd-quote-text">так ничего и не падало считай, больше половины падения сегодня это сбер-газ-лук...</div></div><button class="mfd-button-attention" data-id="15385002" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button></div>"""
    res = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    expected = (
        "| [Тул Равий](http://mfd.ru/forum/poster/?id=110132) @ [09.11.2018 15:12](http://mfd.ru/forum/post/?id=15384866)\n"
        "|  \n"
        "|  Пришел. Включил. Подумал.  \n"
        "| Что, мол, таки да - накаркал.\n"
        "| \n"
        "|\n"
        "| \n"
        "| | [Тул Равий](http://mfd.ru/forum/poster/?id=110132) @ [07.11.2018 22:33](http://mfd.ru/forum/post/?id=15372976)\n"
        "| |  \n"
        "| |  Коррекция неминуема как победа\n"
        "| | пролетарской революции. Ибо.  \n"
        "| | Во-первых: мне пора опять\n"
        "| | закупиться, потому, что «те, что были\n"
        "| | на прошлой неделе мы уже съели»\n"
        "| | (доедал сегодня, осталось немного и\n"
        "| | ВТБ, между прочим).  \n"
        "| | Во-вторых,  \n"
        "| | ...  \n"
        "| | Из того, что попадемся. Мы —\n"
        "| | попадемся в принципе.\n"
        "| | \n"
        "|\n"
        "| \n"
        "| | [Тул Равий](http://mfd.ru/forum/poster/?id=110132) @ [05.11.2018 19:05](http://mfd.ru/forum/post/?id=15358318)\n"
        "| |  \n"
        "| |  ... нефть сколько стоить будет в\n"
        "| | декабре в след году?,  \n"
        "| | - Год длинный. ИМХО, в целом, не\n"
        "| | выше 80. Скорее около 70, как бы не\n"
        "| | ниже. Но не ниже 60. Это и удобная\n"
        "| | цена для сланцевиков. Лично я\n"
        "| | ориентируюсь на эти цифры. В 100 не\n"
        "| | верю. Даже в 90. Потом - да. Но\n"
        "| | больше по причине повышения\n"
        "| | себестоимости добычи в целом. Нас,\n"
        "| | кстати, это касается чуть ли не в\n"
        "| | первую очередь. С Ираном до конца\n"
        "| | 2019, так или иначе, разрулят.\n"
        "| | \n"
        "|  \n"
        "|  Вот только брать, ИМХО, еще\n"
        "| нечего... Так, по ощущениям (ибо с\n"
        "| математикой - \"не очень\").\n"
        "\n"
        "так ничего и не падало считай,\n"
        "больше половины падения сегодня\n"
        "это сбер-газ-лук...")
    assert res == expected


async def test_too_long():
    html = """<div class="mfd-post-top"><div class="mfd-post-top-0" id="15436361"><a class="mfd-poster-link" href="/forum/poster/?id=95837" rel="nofollow" title="ID: 95837">Пумба</a></div><div class="mfd-post-top-1"><a class="mfd-post-link" href="http://forum.mfd.ru/forum/post/?id=15436361" rel="nofollow" title="Ссылка на это сообщение">19.11.2018 07:50</a></div><div class="mfd-post-top-4"><a class="mfd-button-pm" href="/user/messages/send/?to=95837" title="Послать личное сообщение"> </a> &nbsp;&nbsp;&nbsp; <span class="mfd-icon-delete" style="visibility: hidden;" type="button">&nbsp;</span><button class="mfd-button-edit" style="visibility: hidden;" type="button">&nbsp;</button><button class="mfd-button-quote" data-id="15436361" name="quotePost" title="Цитировать" type="button"> </button></div><div class="mfd-post-top-2"><span id="mfdPostRating15436361">&nbsp;</span></div><div class="mfd-post-top-3"><form><label class="mfd-post-rate--1"><input data-id="15436361" data-status="0" data-vote="-1" name="ratePost" type="radio">−1</label><label class="mfd-post-rate-0" style="display: none;"><input data-id="15436361" data-status="0" data-vote="0" name="ratePost" type="radio">0</label><label class="mfd-post-rate-1"><input data-id="15436361" data-status="0" data-vote="1" name="ratePost" type="radio">+1</label></form></div><div class="mfd-clear"></div></div><table><tbody><tr><td class="mfd-post-body-left-container" rowspan="2"><div class="mfd-post-body-left"><div class="mfd-post-avatar"><a href="/forum/poster/?id=95837" rel="nofollow" title="ID: 95837"><img alt="" src="http://forum.mfd.ru/forum/user/95837/15417862113016985.jpeg"></a></div><div class="mfdPosterInfoShort"><div class="mfd-poster-info-rating mfd-icon-profile-star"><a href="/forum/poster/rating/?id=95837" rel="nofollow" title="Детализация рейтинга (1987)">1987</a></div><div class="mfd-poster-info-icons"><a class="mfd-icon-profile-hat-3" href="/forum/poster/forecasts/?id=95837" rel="nofollow" title="962 место в рейтинге прогнозов"></a><a class="mfd-icon-profile-blog" href="/forum/poster/?id=95837" rel="nofollow" title="Блог пользователя"></a></div></div></div></td><td class="mfd-post-body-right-container"><div class="mfd-post-body-right"><div><blockquote class="mfd-quote-15436355"><div class="mfd-quote-info"><a href="/forum/poster/?id=85472" rel="nofollow">emply</a> @ <a href="/forum/post/?id=15436355" rel="nofollow">19.11.2018 07:45</a></div><div class="mfd-quote-text">Шлак с кучей долгов</div><blockquote class="mfd-quote-15436341"><div class="mfd-quote-info"><a href="/forum/poster/?id=95837" rel="nofollow">Пумба</a> @ <a href="/forum/post/?id=15436341" rel="nofollow">19.11.2018 07:34</a></div><div class="mfd-quote-text">Коллеги, представляю Вашему вниманию фундаментальный разбор акции ПАО ГИТ. <br> Вы поймете почему я считаю этот эмитент одним из главных "Тёмных лошадок" Российского рынка, о том почему 2019 год пройдет под эгидой Реформы ЖКХ и даже найдете связь ПАО ГИТ с В.В. Путиным, итак поехали..... <br>  <br> <i>Справочно ПАО «ГИТ» — всероссийских многопрофильный холдинг в сфере ЖКХ, признанный лидер российского рынка ЖКХ, крупнейшая частная компания в сфере управления недвижимостью в Северо-Западном регионе и одна из крупнейших в России. </i> <br>  <br> I. <b><u>Владелец</u></b> <br> Грант Агасьян - бизнесмен, депутат Финляндский округ Санкт-Петербурга 5-го созыва, владелец Холдинга ПАО ГИТ.  <br> 1. Родился в 1987 году. Работал помощником юриста, генеральным директором юридических компаний. В 2009 году окончил Санкт-Петербургский инженерно-экономический университет по специальности «юриспруденция». Женат. <b>В 2014 году оказывал помощь в работе правительству Крыма в присоединении к Российской Федерации</b>. Имеет поощрения в работе с гражданами от ВПП «Единая Россия», Правительства Крыма. Член партии «Единая Россия». Работает над кандидатской диссертацией. <b>Председатель совета директоров ПАО «Городские инновационные технологии. </b>С 2014 г. – депутат Муниципального совета Финляндского округа. <br> <a href="http://finokrug.spb.ru/publ/info/290" rel="nofollow" target="_blank">http://finokrug.spb.ru/publ/info/290</a> <br> 2. Является Организатором пикета за передачу Исаакиевского собора РПЦ <br> <a href="https://echo.msk.ru/news/1917464-echo.html" rel="nofollow" target="_blank">https://echo.msk.ru/news/1917464-echo.html</a> <br> 3. Поддерживает главный Петербургский Крестный Ход <br> <a href="http://paogit.ru/news/pao_git_krestniy_hod" rel="nofollow" target="_blank">http://paogit.ru/news/pao_git_krestniy_hod</a> <br> 4. Является владельцем ММА клуба "СЕЧЬ" <br> <a href="https://vk.com/sech_mma" rel="nofollow" target="_blank">https://vk.com/sech_mma</a> <br> 5. Владеет 31% акциями ПАО ГИТ <br>  <br> <b><u>II. Структура холдинга</u></b> <br> Согласно отчету МФСО за 6 месяцев 2018 года в холдинг ПАО ГИТ входит 30 дочерних и зависимых обществ, из них 19 управляющих компаний. <br> <a href="https://e-disclosure.azipi.ru/upload/iblock/4c1/4c1b24163f0ad9a2c0d70c62e8908fa3.rar" rel="nofollow" target="_blank">https://e-disclosure.azipi.ru/upload/iblock/4c1...</a> (приложение №2 стр. 17) <br> Холдинг управляет 4 916 227 кв.м. жилья <br> <a href="http://funkyimg.com/view/2NgDT" rel="nofollow" target="_blank">http://funkyimg.com/view/2NgDT</a> <br> Таким образом ПАО ГИТ размещается на 10 месте среди УК РФ <br> <a href="http://funkyimg.com/view/2NgDY" rel="nofollow" target="_blank">http://funkyimg.com/view/2NgDY</a> <br>  <br> Кроме услуг ЖКХ холдинг работает в таких направлениях как: <br> Организация эксплуатации жилищного и нежилого фонда; Техническое обслуживание и ремонт общих коммуникаций, технических устройств, строительных конструкций и инженерных систем зданий; Техническое обслуживание (содержание) жилищного и нежилого фонда; Работы по уборке лестничных клеток, мусоропроводов и дворов; Деятельность в области архитектуры; инженерно-технологическое проектирование; геолого-разведочные работы и геофизические работы; Услуги индивидуального проектирования, управления строительством, услуги по реконструкции и модернизации. Строительство жилых помещений, строительство коммерческой недвижимости; вывоз строительного и бытового мусора; Операции с недвижимым имуществом за вознаграждение или на договорной основе; Аренда и управление собственным или арендованным недвижимым имуществом;  <br>  <br> <b>На 18.11.2018 дочерние и зависимые общества являются гарантирующими поставщиками государственных предприятий на сумму 30 025 406 рублей</b> <br>  <br> <b><u>III. МФСО</u></b> <br>  <br> ПАО ГИТ провел IPO в 2015 году. За это время выручка выросла в 6 раз , чистая прибыль в 3,2 раза, обязательства в 2,7 раза , кстати нераспределенная прибыль на сегодня составляет почти 196 млн рублей или 0,448 рубля на 1 акцию. <br>  <br> Выручка 2015 год - 336 940 000 рублей <br> Выручка 2016 год - 1 006 275 000 рублей  <br> <b>Выручка 2017 год - 2 051 998 000 рублей </b> <br> Выручка 6 месяцев 2018 года - 1 164 707 000 рублей <br>  <br> Чистая прибыль 2015 год -21 000 000 рублей <br> Чистая прибыль 2016 год - 60 517 000 рублей <br> <b>Чистая прибыль 2017 год - 68 759 000 рублей <br> Чистая прибыль 6 месяцев 2018 года - 76 058 000 рублей</b> <br>  <br> Нераспределенная прибыль 2015 год  - 14 982 000 рублей <br> Нераспределенная прибыль 2016 год - 75 499 000 рублей <br> <b>Нераспределенная прибыль 2017 год - 126 532 000 рублей <br> Нераспределенная прибыль 6 месяцев 2018 года - 195 990 000 рублей</b> <br>  <br> Итого обязательств 2015 год - 291 551 000 рублей <br> Итого обязательств 2016 год - 967 968 000 рублей <br> <b>Итого обязательств 2017 год - 800 792 000 рублей</b> <br> Итого обязательство 6 месяцев 2018 года - 829 116 000 рублей <br>  <br> <b><u>IV. Обязательства - долги </u></b> <br>  <br> Управляющая компания выполняет большой объем обязательств перед жильцами. Благодаря ей во время осуществляет ремонт дома, предоставляются качественные коммунальные услуги. Жильцы обязаны оплачивать лишь работу УК и те ресурсы, которые они ежедневно используют. УК при этом выступает посредником между ними и ресурсоснажающими организациями, обязуясь заниматься сбором платежей и передачей денег. Но не все владельцы квартир добросовестно относятся к своим обязанностям и не оплачивают коммунальные услуги или работу подрядчиков. <br>  <br> Как видим эта проблема не обошла стороной ГИТ. Хоть и обязательства на конец 2017 года сократились на 18% , но все равно составляют внушительную сумму 800 792 000 рублей. <br> Решение проблемы задолженности жителей перед УК , а соответственно и перед ресурсосберегающими организациями предложили правительство Российской Федерации, а именно <br> 1. В конце марта этого года Госдума приняла закон о прямых расчетах между собственниками жилья и ресурсоснабжающими организациями <br> <a href="http://forum.mfd.ru/forum/post/?id=14381345" rel="nofollow" target="_blank">http://forum.mfd.ru/forum/post/?id=14381345</a> <br> 2. Коммунальщики заявили о планах передавать коллекторам долги по ЖКХ <br> <a href="https://www.rbc.ru/society/07/11/2018/5be22e369a79475e157078b6" rel="nofollow" target="_blank">https://www.rbc.ru/society/07/11/2018/5be22e369...</a> <br>  <br> <b><u>V. Дивиденды</u></b> <br> Дивиденды 2015 год на 1 акцию - 0,001 рублей <br> Дивиденды 2016 год на 1 акцию - 0,01 рублей <br> Дивиденды 2017 год на 1 акцию - 0,02 рублей <br>  <br> Как видим дивиденды тоже растут из года в год, кроме того ПАО ГИТ планирует ввести дивидендную политику и выплачивать дивиденды 2 раза в год  <br> <a href="http://paogit.ru/news/pao_git_dividendy_2_raza_v_god" rel="nofollow" target="_blank">http://paogit.ru/news/pao_git_dividendy_2_raza_...</a> <br>  <br> <b><u>VI. Кредитный рейтинг</u></b> <br> RAEX (Эксперт РА) подтвердил рейтинг компании «Городские инновационные технологии». Прогноз по рейтингу - стабильный. <br> <a href="https://raexpert.ru/releases/2018/Jun25/" rel="nofollow" target="_blank">https://raexpert.ru/releases/2018/Jun25/</a> <br>  <br> <b><u>VII. Реформа ЖКХ, Инвестиции 2,5 трлн. рублей</u></b> <br>  <br> 1. <b>ФАС подготовила предложения о передаче ЖКХ в регионах в частные руки.</b> <br> <a href="https://www.rbc.ru/economics/09/02/2018/5a7c63759a794794eeae9c5e" rel="nofollow" target="_blank">https://www.rbc.ru/economics/09/02/2018/5a7c637...</a> <br>  <br> Глав российских регионов следует обязать провести масштабную приватизацию, а также довести до определенного уровня долю частного бизнеса в разных отраслях, в том числе в ЖКХ, здравоохранении и дошкольном образовании. Такие предложения содержатся в проекте доклада (есть у РБК) рабочей группы к заседанию Госсовета по развитию конкуренции в субъектах. Документ подготовила Федеральная антимонопольная служба (ФАС). <br>  <br> <b>Губернаторы, согласно предложениям из доклада, до 2020 года должны организовать приватизацию или ликвидацию не менее 50% государственных унитарных предприятий (ГУП) в своих регионах, к 2022 году должны быть приватизированы или ликвидированы все ГУП. Такие же меры следует провести и на муниципальном уровне.</b> <br>  <br> <b>Рынок объемом 2,4 трлн руб. Даже оставшиеся в региональной собственности предприятия ЖКХ не должны управляться государством. ФАС предлагает передать объекты, находящиеся в собственности субъектов или муниципалитетов, в концессию (договор, при котором частная компания инвестирует в объект, находящийся в госсобственности, и использует его на безвозмездной основе). Сделать это предлагается до 2020 года при посредстве конкурсных процедур.</b> <br>  <br> Объем рынка жилищно-коммунальных услуг в 2016 году составил 2,4 трлн руб., говорилось в исследовании компании Bussinesstat, это почти в полтора раза больше его размера в 2012 году. «Показатель рос как за счет увеличения натурального объема рынка, так и за счет повышения тарифов на жилищно-коммунальные услуги», — отмечают аналитики. По их прогнозу до 2021 года рынок продолжит расти темпами 4–6% ежегодно (в натуральном выражении, то есть по количеству обслуженных помещений). Ускорить рост может госпрограмма по обеспечению комфортным жильем. <br>  <br> 2. Москва. 17 сентября. ИНТЕРФАКС - Комиссия по законопроектной деятельности одобрила законопроект о запрете на создание новых государственных и муниципальных унитарных предприятий за рядом исключений, а также о ликвидации или реорганизации действующих на товарных рынках ГУПов и МУПов к 1 января 2021 года, сообщила пресс-служба правительства в понедельник. <br>  <br> <a href="https://www.ipku.ru/stati_44_FZ/odobren_zakonoproekt_o_likvidacii_ili_reorganizaci.html" rel="nofollow" target="_blank">https://www.ipku.ru/stati_44_FZ/odobren_zakonop...</a> <br>  <br> <b><i>Грубо говоря, рынок ЖКХ составляет 2,4 трлн рублей в год и требует глобальной модернизации, в 2020 году все ГУПы и МУПы будут ликвидированы и переданы по конкурсным процедурам частным компаниям. <br> Далее до 2025 года планируется ввести инвестиции в сектор порядка 500 млрд рублей ежегодно</i></b> <br> и ПАО ГИТ планирует активно принимать участие в приватизации ГУПов и МУПов  <br> Подробнее тут <br> <a href="http://bujet.ru/article/336226.php" rel="nofollow" target="_blank">http://bujet.ru/article/336226.php</a> <br> <a href="http://paogit.ru/news/teploenergetika_git_" rel="nofollow" target="_blank">http://paogit.ru/news/teploenergetika_git_</a> <br>  <br> <b><u>VIII. Капитализация</u></b> <br> На фоне грядущей реформы ЖКХ и ежегодного роста бизнеса холдинга, капитализация на бирже составляет всего 191 843 000 рублей, что безусловно является позитивным фактором для наращивания портфеля.  <br> Для сравнения можете взглянуть на список "аутсайдеров" ММВБ по капитализации. <br> <a href="http://funkyimg.com/view/2NgVZ" rel="nofollow" target="_blank">http://funkyimg.com/view/2NgVZ</a> <br> ПАО ГИТ на мой взгляд является единственным фаворитом который сможет повторить путь Профнастила. <br>  <br> <b><u>IX. Ежегодный рост тарифов ЖКХ</u></b> <br> Сфера ЖКХ является "тихой гаванью" при любом кризисе. Т.к. повышение тарифов будут следовать экономической ситуации в стране. <br> <a href="http://takovzakon.ru/dvuhjetapnoe-povyshenie-tarifov-zhkh-s-1-janvarja-2019-goda-poslednie-novosti/" rel="nofollow" target="_blank">http://takovzakon.ru/dvuhjetapnoe-povyshenie-ta...</a> <br> Двухэтапное повышение тарифов ЖКХ с 1 января 2019 года. <br>  <br> <b><u>X. Планы развития и реализуемые проекты</u></b> <br>  <br> Группа компаний «ГИТ» имеет ряд стратегических проектов, реализацией которых она планирует заняться на протяжении следующих лет: <br>  <br> 1.	Развитие своего присутствия в различных регионах и увеличение общего объема управляемых площадей до 30. 000. 000 метров квадратных. Региональное развитие компании, выход в новые регионы и занятие во всех регионах присутствия холдинга лидирующего положения. <br> 2.	Занятие ключевых позиций в качестве ЖКХ холдинга в центральном регионе РФ, Москве и Московской области. <br> 3.	Активное участия в региональных программах капитального ремонта строительных компаний, входящих в холдинг ГИТ. Внедрение современных технологий в рамках реализации федеральной программы капитального ремонта. <br> 4.	Активное развитие компании в сфере теплоэнергетики и коммунальной инфраструктуры, как в рамках частных инвестиций, так и в рамках концессионных соглашений во всех регионах присутствия холдинга. <br> 5.	Развитие направления, связанного с переработкой, вывозом и утилизацией ТБО и других видов отходов, как в качестве независимого игрока, так и в качестве единого оператора в рамках концессионных соглашений в различных регионах РФ. <br> 6.	Развитие телекоммуникационных услуг для жителей управляемых домов предоставление новых современных решений на базе совместных предприятий организованных с крупнейшими телекоммуникационными компаниями России. <br> 7.	Развитие социально-ответственного бизнеса и широкое взаимодействие с региональной властью с целью эффективного решения социальных задач в регионах и повышения качества жизни Россиян. <br>  <br> В.В.Путин поздравляет клуб MMA «СЕЧЬ» (владелец Грант Агасьян) с победой на «президентском» турнире.<span class="mfd-emoticon mfd-emoticon-grin"></span> <br> <a href="http://funkyimg.com/view/2NgWZ" rel="nofollow" target="_blank"><img src="http://funkyimg.com/p/2NgWZ.jpg" alt="Показать в полный размер"></a> <br> <a href="http://paogit.ru/news/pao_git_prezident_pobeda" rel="nofollow" target="_blank">http://paogit.ru/news/pao_git_prezident_pobeda</a> <br>  <br> <b><u>XII. Фри-флоат и список аффилированных лиц</u></b> <br> <a class="mfd-blockquote-link-0" href="http://funkyimg.com/i/2LGk6.png" rel="nofollow" target="_blank">http://funkyimg.com/i/2LGk6.png</a><div class="mfd-blockquote-link-1"><a href="http://funkyimg.com/i/2LGk6.png" target="_blank" title="Показать изображение"><img alt="Показать изображение" src="http://funkyimg.com/p/2LGk6.png"></a></div> <br> На 18.11.2018 года фри-флота = 50,49% <br>  <br>  <br> <b><u>XIII. выводы</u></b> <br> ПАО ГИТ, компания показала впечатлительные результаты роста. За 2017 год площадь обслуживающих помещений увеличилась в 2 раза, выручка компании также показала кратный рост и увеличилась до 2,052 млрд руб, в тоже время обязательства за 2017 год уменьшились на 18% до уровня 800млн. рублей, что свидетельствует об умении руководства принимать взвешенные решения и искать способы укрепления бизнеса. В тоже время стоит отметить, что компания растет на фоне реформы ЖКХ. До 2022 года правительство России планирует инвестировать в отрасль порядка 3 трлн рублей. (за 2017 год этот показатель составил 435,6 миллиарда рублей). <br> Из минусов могу выделить тот факт, что не все компании холдинга оформлены на ПАО ГИТ.  <br> Большинство из них "Зависимые" общества.  <br>  <br> На мой взгляд котировки на 16.11.2018г (0,439р) не отражают всей фундаментальной стоимости акции, и текущее падение являются временным спекулятивным эффектом. <br> Только нераспределенная прибыль на 6 месяцев 2018 года составляет 0,448 руб./акцию , Р/Е = 2,8. <br> Акции ПАО ГИТ в данный момент - наивысшая точка для спекуляций среди ММБВ, это связано с низкой капитализацией эмитента и рядом предпосылок развития сферы ЖКХ.  <br>  <br> Настало время для стабилизации и роста котировок.</div></blockquote></blockquote><div class="mfd-quote-text">Про ГТЛ и Профнастил тоже так писали, но когда появилась идея она дала всем заработать. <br> В ЖКХ например - это ликвидация и передача государственных компаний (ГУПов и МУПов) в частные руки до 2020 года и инвестиции в отрасль до 2023 года 2,5трлн. рублей. <br> Аналоги на ММВБ есть но только косвенно - это группа компаний ПИК, капитализацию Вы сами можете сравнить.</div></div><button class="mfd-button-attention" data-id="15436361" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button></div></td></tr><tr><td class="mfd-post-signature">--------------------<div>Самая недооцененная и прибыльная фишка декабря 2018 - 2019 года. <br> Полный фундаментальный разбор тут <br> <a href="http://forum.mfd.ru/forum/post/?id=15435746" rel="nofollow" target="_blank">http://forum.mfd.ru/forum/post/?id=15435746</a></div></td></tr></tbody></table>"""
    res = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    exp = ("[Пумба](http://mfd.ru/forum/poster/?id=95837)\n"
           "\n"
           "[19.11.2018 07:50](http://forum.mfd.ru/forum/post/?id=15436361)\n"
           "\n"
           "[ ](http://mfd.ru/user/messages/send/?to=95837)       \n"
           "\n"
           "\n"
           "\n"
           "−10+1\n"
           "\n"
           "[](http://mfd.ru/forum/poster/?id=95837)\n"
           "\n"
           "[1987](http://mfd.ru/forum/poster/rating/?id=95837)\n"
           "\n"
           "[](http://mfd.ru/forum/poster/forecasts/?id=95837)[](http://mfd.ru/forum/poster/?id=95837)\n"
           "\n"
           "|\n"
           "| \n"
           "| [emply](http://mfd.ru/forum/poster/?id=85472) @ [19.11.2018 07:45](http://mfd.ru/forum/post/?id=15436355)\n"
           "|  \n"
           "|  Шлак с кучей долгов\n"
           "| \n"
           "|\n"
           "| \n"
           "| | [Пумба](http://mfd.ru/forum/poster/?id=95837) @ [19.11.2018 07:34](http://mfd.ru/forum/post/?id=15436341)\n"
           "| |  \n"
           "| |  Коллеги, представляю Вашему\n"
           "| | вниманию фундаментальный разбор\n"
           "| | акции ПАО ГИТ.  \n"
           "| | Вы поймете почему я считаю этот\n"
           "| | эмитент одним из главных \"Тёмных\n"
           "| | лошадок\" Российского рынка, о том\n"
           "| | почему 2019 год пройдет под эгидой\n"
           "| | Реформы ЖКХ и даже найдете связь\n"
           "| | ПАО ГИТ с В.В. Путиным, итак\n"
           "| | поехали.....  \n"
           "| |   \n"
           "| | _Справочно ПАО «ГИТ» —\n"
           "| | всероссийских многопрофильный\n"
           "| | холдинг в сфере ЖКХ, признанный\n"
           "| | лидер российского рынка ЖКХ,\n"
           "| | крупнейшая частная компания в сфере\n"
           "| | управления недвижимостью в\n"
           "| | Северо-Западном регионе и одна из\n"
           "| | крупнейших в России._  \n"
           "| |   \n"
           "| | I. **_Владелец_**  \n"
           "| | Грант Агасьян - бизнесмен, депутат\n"
           "| | Финляндский округ Санкт-Петербурга\n"
           "| | 5-го созыва, владелец Холдинга ПАО\n"
           "| | ГИТ.  \n"
           "| | 1. Родился в 1987 году. Работал\n"
           "| | помощником юриста, генеральным\n"
           "| | директором юридических компаний.\n"
           "| | В 2009 году окончил Санкт-\n"
           "| | Петербургский инженерно-\n"
           "| | экономический университет по\n"
           "| | специальности «юриспруденция».\n"
           "| | Женат. **В 2014 году оказывал\n"
           "| | помощь в работе правительству\n"
           "| | Крыма в присоединении к Российской\n"
           "| | Федерации**. Имеет поощрения в\n"
           "| | работе с гражданами от ВПП «Единая\n"
           "| | Россия», Правительства Крыма. Член\n"
           "| | партии «Единая Россия». Работает\n"
           "| | над кандидатской диссертацией.\n"
           "| | **Председатель совета директоров\n"
           "| | ПАО «Городские инновационные\n"
           "| | технологии.** С 2014 г. – депутат\n"
           "| | Муниципального совета\n"
           "| | Финляндского округа.  \n"
           "| | [http://finokrug.spb.ru/publ/info/290](http://finokrug.spb.ru/publ/info/290)   \n"
           "| | 2. Является Организатором пикета за\n"
           "| | передачу Исаакиевского собора РПЦ  \n"
           "| | [https://echo.msk.ru/news/1917464-echo.html](https://echo.msk.ru/news/1917464-echo.html)   \n"
           "| | 3. Поддерживает главный\n"
           "| | Петербургский Крестный Ход  \n"
           "| | [http://paogit.ru/news/pao_git_krestniy_hod](http://paogit.ru/news/pao_git_krestniy_hod)   \n"
           "| | 4. Является владельцем ММА клуба\n"
           "| | \"СЕЧЬ\"  \n"
           "| | [https://vk.com/sech_mma](https://vk.com/sech_mma)   \n"
           "| | 5. Владеет 31% акциями ПАО ГИТ  \n"
           "| |   \n"
           "| | **_II. Структура холдинга_**  \n"
           "| | Согласно отчету МФСО за 6 месяцев\n"
           "| | 2018 года в холдинг ПАО ГИТ входит\n"
           "| | 30 дочерних и зависимых обществ, из\n"
           "| | них 19 управляющих компаний.  \n"
           "| | [https://e-disclosure.azipi.ru/upload/iblock/4c1...](https://e-disclosure.azipi.ru/upload/iblock/4c1/4c1b24163f0ad9a2c0d70c62e8908fa3.rar) (приложение №2 стр. 17)   \n"
           "| | Холдинг управляет 4 916 227 кв.м.\n"
           "| | жилья  \n"
           "| | [http://funkyimg.com/view/2NgDT](http://funkyimg.com/view/2NgDT)   \n"
           "| | Таким образом ПАО ГИТ размещается\n"
           "| | на 10 месте среди УК РФ  \n"
           "| | [http://funkyimg.com/view/2NgDY](http://funkyimg.com/view/2NgDY)   \n"
           "| |   \n"
           "| | Кроме услуг ЖКХ холдинг работает в\n"
           "| | таких направлениях как:  \n"
           "| | Организация эксплуатации\n"
           "| | жилищного и нежилого фонда;\n"
           "| | Техническое обслуживание и ремонт\n"
           "| | общих коммуникаций, технических\n"
           "| | устройств, строительных\n"
           "| | конструкций и инженерных систем\n"
           "| | зданий; Техническое обслуживание\n"
           "| | (содержание) жилищного и нежилого\n"
           "| | фонда; Работы по уборке лестничных\n"
           "| | клеток, мусоропроводов и дворов;\n"
           "| | Деятельность в области\n"
           "| | архитектуры; инженерно-\n"
           "| | технологическое проектирование;\n"
           "| | геолого-разведочные работы и\n"
           "| | геофизические работы; Услуги\n"
           "| | индивидуального проектирования,\n"
           "| | управления строительством, услуги\n"
           "| | по реконструкции и модернизации.\n"
           "| | Строительство жилых помещений,\n"
           "| | строительство коммерческой\n"
           "| | недви...")
    assert res == exp


async def test_entity():
    html = """<div class="mfd-post mfd-post-selected" id="table15501364"><div class="mfd-post-top"><div class="mfd-post-top-0" id="15501364"><a class="mfd-poster-link" href="/forum/poster/?id=57337" rel="nofollow" title="ID: 57337">arsagera</a></div><div class="mfd-post-top-1"><a class="mfd-post-link" href="http://forum.mfd.ru/forum/post/?id=15501364" rel="nofollow" title="Ссылка на это сообщение">29.11.2018 18:22</a></div><div class="mfd-post-top-4"><a class="mfd-button-pm" href="/user/messages/send/?to=57337" title="Послать личное сообщение"> </a> &nbsp;&nbsp;&nbsp; <span class="mfd-icon-delete" style="visibility: hidden;" type="button">&nbsp;</span><button class="mfd-button-edit" style="visibility: hidden;" type="button">&nbsp;</button><button class="mfd-button-quote" data-id="15501364" name="quotePost" title="Цитировать" type="button"> </button></div><div class="mfd-post-top-2"><span class="u" id="mfdPostRating15501364">2</span><div class="mfd-post-ratingdetails" style="display: none;"><table><tbody><tr><td><a href="/forum/poster/?id=93229" rel="nofollow">Bumerrang</a></td><td>+</td></tr><tr><td><a href="/forum/poster/?id=69399" rel="nofollow">bsv_sml</a></td><td>+</td></tr></tbody></table></div></div><div class="mfd-post-top-3"><form><label class="mfd-post-rate--1"><input data-id="15501364" data-status="0" data-vote="-1" name="ratePost" type="radio">−1</label><label class="mfd-post-rate-0" style="display: none;"><input data-id="15501364" data-status="0" data-vote="0" name="ratePost" type="radio">0</label><label class="mfd-post-rate-1"><input data-id="15501364" data-status="0" data-vote="1" name="ratePost" type="radio">+1</label></form></div><div class="mfd-clear"></div></div><table><tbody><tr><td class="mfd-post-body-left-container" rowspan="2"><div class="mfd-post-body-left"><div class="mfd-post-avatar"><a href="/forum/poster/?id=57337" rel="nofollow" title="ID: 57337"><img alt="" src="http://forum.mfd.ru/forum/user/57337/avatar.jpg"></a></div><div class="mfdPosterInfoShort"><div class="mfd-poster-info-rating mfd-icon-profile-star"><a href="/forum/poster/rating/?id=57337" rel="nofollow" title="Детализация рейтинга (1480)">1480</a></div><div class="mfd-poster-info-icons"><a class="mfd-icon-profile-blog" href="/forum/poster/?id=57337" rel="nofollow" title="Блог пользователя"></a></div></div></div></td><td class="mfd-post-body-right-container"><div class="mfd-post-body-right"><div><div class="mfd-quote-text"><b>Акрон (AKRN) <br> Итоги 9 мес. 2018 года: курсовые разницы сократили прибыль</b> <br>  <br> Акрон раскрыл консолидированную финансовую отчетность по МСФО за 9 месяцев 2018 года. <br>  <br> см. таблицу: <a href="https://bf.arsagera.ru/proizvodstvo_mineralnyh_udobrenij/akron/itogi_9_mes_2018_goda/" rel="nofollow" target="_blank">https://bf.arsagera.ru/proizvodstvo_mineralnyh_...</a> <br>  <br> Выручка компании увеличилась на 12,3% - до 77,8 млрд руб. Существенный рост продемонстрировала выручка от продажи комплексных удобрений (+12,4%), составившая 34,1 млрд руб. на фоне снижения объемов реализации на 5,6% до 1,88 млн тонн и роста средних цен реализации на 19% – до 18,2 тыс. руб. за тонну. Еще более впечатляющую динамику показала выручка от продаж аммиачной селитры (+30,1%), которая составила 12,2 млрд руб. на фоне увеличения объемов реализации до 1 050 тыс. тонн (+7,1%) и средней цены на 21,5% – до 11,6 тыс. руб. за тонну. Выручка от реализации карбамидо-аммиачной смеси увеличилась на 32,4% - до 9 млрд руб., объемы реализации выросли на 7,2% – до 897 тыс. тонн, а средняя цена продемонстрировала положительную динамику (+23,5%) – до 10 тыс. рублей за тонну. <br>  <br> Операционные расходы продемонстрировали рост в 8,7%, составив 59,2 млрд руб. В числе причин компания называет повысившиеся амортизационные отчисления из-за проекта «Олений ручей» и рост расходов на транспорт (повышение ставок аренды вагонов и индексация тарифов). Отметим, повышение мировых цен на хлористый калий, закупаемый для производства NPK. Коммерческие, общие и административные расходы выросли на 17%, до 6 млрд руб. Среди основных причин – рост затрат на оплату труда, а также расширение международной сети продаж. <br>  <br> В итоге операционная прибыль выросла на четверть - до 18,6 млрд руб. <br>  <br> Долговое бремя компании с начала года выросло на 12,9 млрд руб. до 87,5 млрд руб., около 70% заемных средств выражены в иностранной валюте. В целом по компании нетто-показатель по курсовым разницам составил отрицательное значение в 4,6 млрд руб. против 14 млн руб. годом ранее. <br>  <br> Кроме того, признание расходов от переоценки производных финансовых инструментов в размере 1,9 млрд руб. против доходов в 0,2 млрд руб. годом ранее привело к росту чистых финансовых расходов до 8,7 млрд руб. В итоге чистая прибыль компании сократилась более чем на четверть – до 7 млрд руб. <br>  <br> Цены на карбамид с июня демонстрируют уверенный рост. Этому способствует сильный спрос в странах Латинской Америки и Индии, а также недостаток предложения на мировом рынке, связанный с сокращением экспорта из Китая. Высокие цены на уголь, основное сырье для производства карбамида в Китае, а также экологические меры правительства вынуждают местных производителей держать цены выше 300 долл. США FOB Китай, фокусируясь на внутреннем рынке. По нашим ожиданиям, цены на карбамид останутся на высоком уровне до конца этого года и в начале следующего благодаря традиционно сильному сезонному спросу, а средний уровень цен в 2019 году ожидается выше уровня текущего года. Рост цен на карбамид способствовал повышению цен и на другие азотные удобрения, такие как аммиачная селитра и КАС, для которых они являются бенчмарком. Цены на NPK в этом году также демонстрируют повышательную динамику, чему способствует рост цен во всех трех сегментах рынка – в азотном, фосфорном и калийном. <br>  <br> Отчетность компании вышла в русле наших ожиданий, нами были внесены незначительные коррективы в части прогнозирования выручки и себестоимости. <br>  <br> Напомним, что рост будущих финансовых результатов мы связываем с развитием компанией масштабных инвестиционных проектов, в частности Талицкого ГОКа, на котором в 2021 году компания планирует начать добычу калия. <br>  <br> см. таблицу: <a href="https://bf.arsagera.ru/proizvodstvo_mineralnyh_udobrenij/akron/itogi_9_mes_2018_goda/" rel="nofollow" target="_blank">https://bf.arsagera.ru/proizvodstvo_mineralnyh_...</a> <br>  <br> На данный момент акции компании обращаются с P/E 2018 – 13 и P/BV 2018 – 3 и входят в число наших диверсифицированных портфелей акций <br>  <br> ___________________________________________ <br> Подробнее о выборе акций, расчете потенциальной доходности и принципах формирования и управления портфелем читайте в книге «Заметки в инвестировании»: <a href="https://arsagera.ru/kuda_i_kak_investirovat/kniga_ob_investiciyah_i_upravlenii_kapitalom/?utm_source=post&amp;utm_campaign=Book&amp;utm_medium=banner&amp;utm_content=post_book_txt" rel="nofollow" target="_blank">https://arsagera.ru/kuda_i_kak_investirovat/kni...</a></div></div><button class="mfd-button-attention" data-id="15501364" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button></div></td></tr><tr><td class="mfd-post-signature">--------------------<div>Уважаемые участники форума! Если вы хотите быстро получить наш комментарий или ответ на вопрос будем благодарны за их дублирование в формате личного сообщения. <br>  <br> Ознакомиться с нашей аналитикой и обсудить эмитентов Вы можете на нашем сайте bf.arsagera.ru</div></td></tr></tbody></table></div>"""
    res = await EmptyTestSource("http://mfd.ru").pretty_text(html)
    exp = ("[arsagera](http://mfd.ru/forum/poster/?id=57337)\n"
           "\n"
           "[29.11.2018 18:22](http://forum.mfd.ru/forum/post/?id=15501364)\n"
           "\n"
           "[ ](http://mfd.ru/user/messages/send/?to=57337)       \n"
           "\n"
           "2\n"
           "\n"
           "[Bumerrang](http://mfd.ru/forum/poster/?id=93229)| +  \n"
           "| ---|---  \n"
           "[bsv_sml](http://mfd.ru/forum/poster/?id=69399)| +  \n"
           "|   \n"
           "| −10+1\n"
           "\n"
           "[](http://mfd.ru/forum/poster/?id=57337)\n"
           "\n"
           "[1480](http://mfd.ru/forum/poster/rating/?id=57337)\n"
           "\n"
           "[](http://mfd.ru/forum/poster/?id=57337)\n"
           "\n"
           "|\n"
           "\n"
           " **Акрон (AKRN)  \n"
           "Итоги 9 мес. 2018 года: курсовые\n"
           "разницы сократили прибыль**  \n"
           "  \n"
           "Акрон раскрыл консолидированную\n"
           "финансовую отчетность по МСФО за 9\n"
           "месяцев 2018 года.  \n"
           "  \n"
           "см. таблицу: [https://bf.arsagera.ru/proizvodstvo_mineralnyh_...](https://bf.arsagera.ru/proizvodstvo_mineralnyh_udobrenij/akron/itogi_9_mes_2018_goda/)   \n"
           "  \n"
           "Выручка компании увеличилась на\n"
           "12,3% - до 77,8 млрд руб.\n"
           "Существенный рост\n"
           "продемонстрировала выручка от\n"
           "продажи комплексных удобрений\n"
           "(+12,4%), составившая 34,1 млрд руб.\n"
           "на фоне снижения объемов\n"
           "реализации на 5,6% до 1,88 млн тонн и\n"
           "роста средних цен реализации на 19%\n"
           "– до 18,2 тыс. руб. за тонну. Еще более\n"
           "впечатляющую динамику показала\n"
           "выручка от продаж аммиачной\n"
           "селитры (+30,1%), которая составила\n"
           "12,2 млрд руб. на фоне увеличения\n"
           "объемов реализации до 1 050 тыс.\n"
           "тонн (+7,1%) и средней цены на 21,5%\n"
           "– до 11,6 тыс. руб. за тонну. Выручка\n"
           "от реализации карбамидо-аммиачной\n"
           "смеси увеличилась на 32,4% - до 9\n"
           "млрд руб., объемы реализации\n"
           "выросли на 7,2% – до 897 тыс. тонн, а\n"
           "средняя цена продемонстрировала\n"
           "положительную динамику (+23,5%) –\n"
           "до 10 тыс. рублей за тонну.  \n"
           "  \n"
           "Операционные расходы\n"
           "продемонстрировали рост в 8,7%,\n"
           "составив 59,2 млрд руб. В числе\n"
           "причин компания называет\n"
           "повысившиеся амортизационные\n"
           "отчисления из-за проекта «Олений\n"
           "ручей» и рост расходов на транспорт\n"
           "(повышение ставок аренды вагонов и\n"
           "индексация тарифов). Отметим,\n"
           "повышение мировых цен на\n"
           "хлористый калий, закупаемый для\n"
           "производства NPK. Коммерческие,\n"
           "общие и административные расходы\n"
           "выросли на 17%, до 6 млрд руб. Среди\n"
           "основных причин – рост затрат на\n"
           "оплату труда, а также расширение\n"
           "международной сети продаж.  \n"
           "  \n"
           "В итоге операционная прибыль\n"
           "выросла на четверть - до 18,6 млрд\n"
           "руб.  \n"
           "  \n"
           "Долговое бремя компании с начала\n"
           "года выросло на 12,9 млрд руб. до\n"
           "87,5 млрд руб., около 70% заемных\n"
           "средств выражены в иностранной\n"
           "валюте. В целом по компании нетто-\n"
           "показатель по курсовым разницам\n"
           "составил отрицательное значение в\n"
           "4,6 млрд руб. против 14 млн руб.\n"
           "годом ранее.  \n"
           "  \n"
           "Кроме того, признание расходов от\n"
           "переоценки производных финансовых\n"
           "инструментов в размере 1,9 млрд руб.\n"
           "против доходов в 0,2 млрд руб. годом\n"
           "ранее привело к росту чистых\n"
           "финансовых расходов до 8,7 млрд\n"
           "руб. В итоге чистая прибыль компании\n"
           "сократилась более чем на четверть –\n"
           "до 7 млрд руб.  \n"
           "  \n"
           "Цены на карбамид с июня\n"
           "демонстрируют уверенный рост.\n"
           "Этому способствует сильный спрос в\n"
           "странах Латинской Америки и Индии, а\n"
           "также недостаток предложения на\n"
           "мировом рынке, связанный с\n"
           "сокращением экспорта из Китая.\n"
           "Высокие цены на уголь, основное\n"
           "сырье для производства карбамида в\n"
           "Китае, а также экологические меры\n"
           "правительства вынуждают местных\n"
           "производителей держать цены выше\n"
           "300 долл. США FOB Китай,\n"
           "фокусируясь на внутреннем рынке. По\n"
           "нашим ожиданиям, цены на карбамид\n"
           "останутся на высоком уровне до\n"
           "конца этого года и в начале\n"
           "следующего благодаря традиционно\n"
           "сильному сезонному спросу, а\n"
           "средний уровень цен в 2019 году\n"
           "ожидается выше уровня текущего\n"
           "года. Рост цен на карбамид\n"
           "способствовал повышению цен и на\n"
           "другие азотные удобрения, такие как\n"
           "аммиачная селитра и КАС, для\n"
           "которых они являются бенчмарком.\n"
           "Цены на NPK в этом году также\n"
           "демонстрируют повышательную\n"
           "динамику, чему способствует рост\n"
           "цен во всех трех сегментах рынка – в\n"
           "азотном, фосфорном и калийном.  \n"
           "  \n"
           "Отчетность компании вышла в русле\n"
           "наших ожиданий, нами были внесены\n"
           "незначительные коррективы в части\n"
           "прогнозирования выручки и\n"
           "себестоимости.  \n"
           "  \n"
           "Напомним, что рост будущих\n"
           "финансовых результатов мы\n"
           "связываем с развитием компанией\n"
           "масштабных инвестиционных\n"
           "проектов, в частности Талицкого\n"
           "ГОКа, на кото...")
    assert res == exp

# async def test_text_width():
#     font = ImageFont.truetype("../assets/rmedium.ttf", 14, encoding="unic")
# print(font.getsize("| | ЕВРАЗ внедряет технологию бурения "))  # -- pass
# print(font.getsize("ЕВРАЗ внедряет технологию бурения…."))  # -- pass
# print(font.getsize("встречи наш ФР может и не пережить 😁"))  # -- wrap
# print(font.getsize("ЕВРАЗ внедряет технологию бурения….."))  # -- wrap
# print(font.getsize("Промышленные испытания технологии"))  # -- wrap
