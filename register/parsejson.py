
def parse_json_response(json_dic):
    language = json_dic['language']
    word_space = ''
    if language == 'zh-Hans' or language == 'zh-Hant' or language == 'ja' or language == 'ko':
        pass
    else:
        word_space = ' '

    lines = json_dic['regions'][0]['lines']
    result = ''
    for line in lines:
        for word in line['words']:
            result += word['text'] + word_space
        result = result.rstrip()
        result += '\n'
    if result == '':
        result = '画像から文字を読み込めませんでした'
    return result
def parse_json_response(json_dic):
    language = json_dic['language']
    word_space = ''
    if language == 'zh-Hans' or language == 'zh-Hant' or language == 'ja' or language == 'ko':
        pass
    else:
        word_space = ' '

    lines = json_dic['regions'][0]['lines']
    result = ''
    for line in lines:
        for word in line['words']:
            result += word['text'] + word_space
        result = result.rstrip()
        result += '\n'
    if result == '':
        result = '画像から文字を読み込めませんでした'
    return result