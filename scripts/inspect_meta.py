import json
META = 'data/idx/meta.json'
if __name__ == '__main__':
    try:
        m = json.load(open(META, 'r', encoding='utf-8'))
    except Exception as e:
        print('Could not read meta:', e)
        raise SystemExit(1)
    print(f'Loaded {len(m)} chunks')
    for i,c in enumerate(m[:5]):
        print(i, c.get('doc_id'), 'article', c.get('article_no'))
