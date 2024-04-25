from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from string import Template

api_key = ""
model = "open-mistral-7b"

client = MistralClient(api_key=api_key)

def get_prompt(question: str, context: dict[str, str]) -> list[dict[str, str]]:
    """Gets prompt for Mistral based on available information

    Args:
        question (str): user's question
        context (dict[str, str]): context related to question extracted from database

    Returns:
        list[dict[str, str]]: Mistral prompt
    """
    values = {'title': context['title'], 'summary': context['summary'], 'question': question}
    if 'author' in context and 'genres' in context and 'date' in context:
        values['author'] = context['author']
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written by $author in $date. It is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'author' in context and 'genres' in context:
        values['author'] = context['author']
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        prompt_template = Template('$title was written by $author. It is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'author' in context and 'date' in context:
        values['author'] = context['author']
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written by $author in $date. Here is a summary of $title: $summary\n$question')
    elif 'genres' in context and 'date' in context:
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written in $date. It is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'author' in context:
        values['author'] = context['author']
        prompt_template = Template('$title was written by $author. Here is a summary of $title: $summary\n$question')
    elif 'genres' in context:
        genres = list(context['genres'].values())
        if len(genres) > 1:
            values['genres'] = ', '.join(genres[:-1]) + ' and ' + genres[-1]
        else:
            values['genres'] = genres[0]
        prompt_template = Template('$title is a work of $genres. Here is a summary of $title: $summary\n$question')
    elif 'date' in context:
        values['date'] = context['date'][:4]
        prompt_template = Template('$title was written in $date. Here is a summary of $title: $summary\n$question')
    else:
        prompt_template = Template('Here is a summary of $title: $summary\n$question')
    
    prompt = prompt_template.substitute(values)
    message = [ChatMessage(role='user', content= prompt)]
    return message

def get_answer(message: list[dict[str, str]]) -> str:
    """Gets Mistral output

    Args:
        message (list[dict[str, str]]): prompt for Mistral

    Returns:
        str: Mistral output
    """
    chat_response = client.chat(
        model=model,
        messages=message,
    )
    return chat_response.choices[0].message.content


if __name__ == '__main__':
    question = "What does the dagger symbolize in Macbeth?"
    context = {'title': 'Macbeth',
                'author': 'William Shakespeare',
                'summary': ' The play opens amidst thunder and lightning, and the Three Witches decide that their next meeting shall be with Macbeth. In the following scene, a wounded sergeant reports to King Duncan of Scotland that his generalsMacbeth, who is the Thane of Glamis, and Banquohave just defeated the allied forces of Norway and Ireland, who were led by the traitorous Macdonwald and the Thane of Cawdor. Macbeth, the King\'s kinsman, is praised for his bravery and fighting prowess. In the following scene, Macbeth and Banquo discuss the weather and their victory. Macbeth\'s first line is "So foul and fair a day I have not seen" (1.3.38). As they wander onto a heath, the Three Witches enter and have been waiting to greet them with prophecies. Though Banquo challenges them first, they address Macbeth, hailing him as "Thane of Glamis," "Thane of Cawdor," and that he shall "be King hereafter." Macbeth appears to be stunned to silence. When Banquo asks of his own fortunes, the witches inform him that he will father a line of kings, though he himself will not be one. While the two men wonder at these pronouncements, the witches vanish, and another thane, Ross, arrives and informs Macbeth of his newly bestowed title: Thane of Cawdor, as the previous Thane of Cawdor shall be put to death for his traitorous activities. The first prophecy is thus fulfilled, and Macbeth immediately begins to harbour ambitions of becoming king. King Duncan welcomes and praises Macbeth and Banquo, and declares that he will spend the night at Macbeth\'s castle at Inverness; he also names his son Malcolm as his heir. Macbeth sends a message ahead to his wife, Lady Macbeth, telling her about the witches\' prophecies. Lady Macbeth suffers none of her husband’s uncertainty, and wishes him to murder Duncan in order to obtain kingship. When Macbeth arrives at Inverness, she overrides all of her husband’s objections by challenging his manhood, and successfully persuades him to kill the king that very night. He and Lady Macbeth plan to get Duncan’s two chamberlains drunk so that they will black out; the next morning they will frame the chamberlains for the murder. They will be defenseless, as they will remember nothing. While Duncan is asleep, Macbeth stabs him, despite his doubts and a number of supernatural portents, including a hallucination of a bloody dagger. He is so shaken that Lady Macbeth has to take charge. In accordance with her plan, she frames Duncan\'s sleeping servants for the murder by placing bloody daggers on them. Early the next morning, Lennox, a Scottish nobleman, and Macduff, the loyal Thane of Fife, arrive. A porter opens the gate and Macbeth leads them to the king\'s chamber, where Macduff discovers Duncan\'s body. In a supposed fit of anger, Macbeth murders the guards (in truth, he kills them to prevent them from claiming their innocence). Macduff is immediately suspicious of Macbeth, but does not reveal his suspicions publicly. Duncan’s sons Malcolm and Donalbain flee to England and Ireland, respectively, fearing that whoever killed Duncan desires their demise as well. The rightful heirs\' flight makes them suspects and Macbeth assumes the throne as the new King of Scotland as a kinsman of the dead king. Banquo reveals this to the audience, and while skeptical of the new King Macbeth, remembers the witches\' prophecy about how his own descendants would inherit the throne. Despite his success, Macbeth, also aware of this part of the prophecy, remains uneasy. Macbeth invites Banquo to a royal banquet, where he discovers that Banquo and his young son, Fleance, will be riding out that night. Macbeth hires two men to kill them; a third murderer appears in the park before the murder. The assassins succeed in killing Banquo, but Fleance escapes. Macbeth becomes furious: as long as Fleance is alive, he fears that his power remains insecure. At the banquet, Macbeth invites his lords and Lady Macbeth to a night of drinking and merriment. Banquo\'s ghost enters and sits in Macbeth\'s place. Macbeth raves fearfully, startling his guests, as the ghost is only visible to himself. The others panic at the sight of Macbeth raging at an empty chair, until a desperate Lady Macbeth tells them that her husband is merely afflicted with a familiar and harmless malady. The ghost departs and returns once more, causing the same riotous anger in Macbeth. This time, Lady Macbeth tells the lords to leave, and they do so. Macbeth, disturbed, visits the three witches once more and asks them to reveal the truth of their prophecies to him. To answer his questions, they summon horrible apparitions, each of which offers predictions and further prophecies to allay Macbeth’s fears. First, they conjure an armed head, which tells him to beware of Macduff (4.1.72). Second, a bloody child tells him that no one born of a woman shall be able to harm him. Thirdly, a crowned child holding a tree states that Macbeth will be safe until Great Birnam Wood comes to Dunsinane Hill. Macbeth is relieved and feels secure, because he knows that all men are born of women and forests cannot move. However, the witches conjure a procession of eight crowned kings, all similar in appearance to Banquo, and the last carrying a mirror that reflects even more kings. Macbeth demands to know the meaning of this final vision, but the witches perform a mad dance and then vanish. Lennox enters and tells Macbeth that Macduff has fled to England. Macbeth orders Macduff\'s castle be seized, and, most cruelly, sends murderers to slaughter Macduff’s wife and children. Everyone in Macduff\'s castle is put to death, including Lady Macduff and their young son. Meanwhile, Lady Macbeth becomes racked with guilt from the crimes she and her husband have committed. At night, in the king’s palace at Dunsinane, a doctor and a gentlewoman discuss Lady Macbeth’s strange habit of sleepwalking. Suddenly, Lady Macbeth enters in a trance with a candle in her hand. Bemoaning the murders of Duncan, Lady Macduff, and Banquo, she tries to wash off imaginary bloodstains from her hands, all the while speaking of the terrible things she knows she pressed her husband to do. She leaves, and the doctor and gentlewoman marvel at her descent into madness. Her belief that nothing can wash away the blood on her hands is an ironic reversal of her earlier claim to Macbeth that “[a] little water clears us of this deed” (2.2.66). In England, Macduff is informed by Ross that his "castle is surprised; [his] wife and babes / Savagely slaughter\'d" (4.3.204-5). When this news of his family’s execution reaches him, Macduff is stricken with grief and vows revenge. Prince Malcolm, Duncan’s son, has succeeded in raising an army in England, and Macduff joins him as he rides to Scotland to challenge Macbeth’s forces. The invasion has the support of the Scottish nobles, who are appalled and frightened by Macbeth’s tyrannical and murderous behavior. Malcolm leads an army, along with Macduff and Englishmen Siward (the Elder), the Earl of Northumberland, against Dunsinane Castle. While encamped in Birnam Wood, the soldiers are ordered to cut down and carry tree limbs to camouflage their numbers. Before Macbeth’s opponents arrive, he receives news that Lady Macbeth has killed herself, causing him to sink into a deep and pessimistic despair and deliver his "Tomorrow, and tomorrow, and tomorrow" soliloquy (5.5.17–28). Though he reflects on the brevity and meaninglessness of life, he nevertheless awaits the English and fortifies Dunsinane. He is certain that the witches’ prophecies guarantee his invincibility, but is struck numb with fear when he learns that the English army is advancing on Dunsinane shielded with boughs cut from Birnam Wood. Birnam Wood is indeed coming to Dunsinane, fulfilling half of the witches’ prophecy. A battle culminates in the slaying of the young Siward and Macduff\'s confrontation with Macbeth, and the English forces overwhelm his army and castle. Macbeth boasts that he has no reason to fear Macduff, for he cannot be killed by any man born of woman. Macduff declares that he was "from his mother\'s womb / Untimely ripp\'d" (5.8.15–16), (i.e., born by Caesarean section) and was not "of woman born" (an example of a literary quibble), fulfilling the second prophecy. Macbeth realizes too late that he has misinterpreted the witches\' words. Though he realizes that he is doomed, he continues to fight. Macduff kills and beheads him, thus fulfilling the first part of the prophecy. Macduff carries Macbeth\'s head onstage and Malcolm discusses how order has been restored. His last reference to Lady Macbeth, however, reveals "\'tis thought, by self and violent hands / Took off her life" (5.9.71–72), leading most to assume that she committed suicide, but the method is undisclosed. Malcolm, now the King of Scotland, declares his benevolent intentions for the country and invites all to see him crowned at Scone. Although Malcolm, and not Fleance, is placed on the throne, the witches\' prophecy concerning Banquo ("Thou shalt get kings") was known to the audience of Shakespeare\'s time to be true: James VI of Scotland (later also James I of England) was supposedly a descendant of Banquo.'}
    answer = get_answer(get_prompt(question, context))
    print(answer)