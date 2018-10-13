import pytest
from trading_bot.sources import MfdSource



def test_tomd():
    text = """
    <div><blockquote class="mfd-quote-14765308"><div class="mfd-quote-info"><a href="/forum/poster/?id=84758" rel="nofollow">Роберт СПБ</a> @ <a href="/forum/post/?id=14765308" rel="nofollow">17.07.2018 13:42</a></div><blockquote class="mfd-quote-14765273"><div class="mfd-quote-info"><a href="/forum/poster/?id=71921" rel="nofollow">malishok</a> @ <a href="/forum/post/?id=14765273" rel="nofollow">17.07.2018 13:35</a></div><div class="mfd-quote-text">есть) у меня она сложнее, смотрю ev/ebitda и p/e конечно, но расчитываю форвард на год+ и смотрю на менеджмент это для меня оч важно</div></blockquote><div class="mfd-quote-text">Но в EV/EBITDA и P/E присутствует капитализация, что не является объективные показателем. Если не брать её во внимание, ты на что больше смотришь, на выручку, операционную прибыль или чистую прибыль?</div></blockquote><div class="mfd-quote-text">смотри, я уже писал, для меня важнее менджмент и их работа, это немного более сложный анализ. <br> Если брать отчеты, то я смотрю операционку больше, чем ЧП ибо в ней много шлака, выручка зависит от компаний - в металлах смотрю, в киви нет, например. Тут компании разные</div></div><button class="mfd-button-attention" data-id="14765341" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>
    """

    text2 = """
    <div><blockquote class="mfd-quote-14765518"><div class="mfd-quote-info"><a href="/forum/poster/?id=83356" rel="nofollow">бык...</a> @ <a href="/forum/post/?id=14765518" rel="nofollow">17.07.2018 14:11</a></div><div class="mfd-quote-text">правильно, чего в провинции открываться<span class="mfd-emoticon mfd-emoticon-wink"></span> сергей, в этот раз поедешь в питер смотреть как локо проигрывает?)</div><blockquote class="mfd-quote-14765420"><div class="mfd-quote-info"><a href="/forum/poster/?id=71921" rel="nofollow">malishok</a> @ <a href="/forum/post/?id=14765420" rel="nofollow">17.07.2018 13:56</a></div><div class="mfd-quote-text">кстати, хочется порекомендовать в Питере парней из Duo Gastrobar и их несколько ресторанов, типа тартарбара <br>  оч крутая кухня, интересная и не так дорого, готовят оч интересно, а в МСК не хотят приходить)</div></blockquote></blockquote><div class="mfd-quote-text">как обычно, чеужтам</div></div><button class="mfd-button-attention" data-id="14765594" name="reportAbuse" title="Пожаловаться на это сообщение" type="button"></button>
    """

    res = """| [Роберт СПБ](http://mfd.ru/forum/poster/?id=84758) @ [17.07.2018 13:42](http://mfd.ru/forum/post/?id=14765308)
|
| 
| | [malishok](http://mfd.ru/forum/poster/?id=71921) @ [17.07.2018 13:35](http://mfd.ru/forum/post/?id=14765273)
| |  
| |  есть) у меня она сложнее,
| | смотрю ev/ebitda и p/e конечно, но
| | расчитываю форвард на год+ и
| | смотрю на менеджмент это для меня
| | оч важно
| | 
|  
|  Но в EV/EBITDA и P/E
| присутствует капитализация, что не
| является объективные показателем.
| Если не брать её во внимание, ты
| на что больше смотришь, на
| выручку, операционную прибыль или
| чистую прибыль?

смотри, я уже писал, для меня
важнее менджмент и их работа, это
немного более сложный анализ.  
Если брать отчеты, то я смотрю
операционку больше, чем ЧП ибо в
ней много шлака, выручка зависит
от компаний - в металлах смотрю, в
киви нет, например. Тут компании
разные"""
    assert MfdSource.pretty_text(text, "http://mfd.ru") == res