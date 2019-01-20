from tests.conftest import EmptyTestSource


async def test_tomd():
    text = """
    <div><blockquote class="mfd-quote-14765308"><div class="mfd-quote-info"><a href="/forum/poster/?id=84758" rel="nofollow">Роберт СПБ</a> @ <a href="/forum/post/?id=14765308" rel="nofollow">17.07.2018 13:42</a></div><blockquote class="mfd-quote-14765273"><div class="mfd-quote-info"><a href="/forum/poster/?id=71921" rel="nofollow">malishok</a> @ <a href="/forum/post/?id=14765273" rel="nofollow">17.07.2018 13:35</a></div><div class="mfd-quote-text">есть) у меня она сложнее, смотрю ev/ebitda и p/e конечно, но расчитываю форвард на год+ и смотрю на менеджмент это для меня оч важно</div></blockquote><div class="mfd-quote-text">Но в EV/EBITDA и P/E присутствует капитализация, что не является объективные показателем. Если не брать её во внимание, ты на что больше смотришь, на выручку, операционную прибыль или чистую прибыль?</div></blockquote><div class="mfd-quote-text">смотри, я уже писал, для меня важнее менджмент и их работа, это немного более сложный анализ. <br> Если брать отчеты, то я смотрю операционку больше, чем ЧП ибо в ней много шлака, выручка зависит от компаний - в металлах смотрю, в киви нет, например. Тут компании разные</div></div><button class="mfd-button-attention" data-id="14765341" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>
    """
    exp = (
        "| [Роберт СПБ](http://mfd.ru/forum/poster/?id=84758) @ [17.07.2018 13:42](http://mfd.ru/forum/post/?id=14765308)\n"
        "|\n"
        "| \n"
        "| | [malishok](http://mfd.ru/forum/poster/?id=71921) @ [17.07.2018 13:35](http://mfd.ru/forum/post/?id=14765273)\n"
        "| |  \n"
        "| |  есть) у меня она сложнее, смотрю\n"
        "| | ev/ebitda и p/e конечно, но\n"
        "| | расчитываю форвард на год+ и\n"
        "| | смотрю на менеджмент это для меня\n"
        "| | оч важно\n"
        "| | \n"
        "|  \n"
        "|  Но в EV/EBITDA и P/E присутствует\n"
        "| капитализация, что не является\n"
        "| объективные показателем. Если не\n"
        "| брать её во внимание, ты на что\n"
        "| больше смотришь, на выручку,\n"
        "| операционную прибыль или чистую\n"
        "| прибыль?\n"
        "\n"
        "смотри, я уже писал, для меня важнее\n"
        "менджмент и их работа, это немного\n"
        "более сложный анализ.  \n"
        "Если брать отчеты, то я смотрю\n"
        "операционку больше, чем ЧП ибо в\n"
        "ней много шлака, выручка зависит от\n"
        "компаний - в металлах смотрю, в киви\n"
        "нет, например. Тут компании разные"
    )

    res = await EmptyTestSource("http://mfd.ru").pretty_text(text)
    assert res == exp
