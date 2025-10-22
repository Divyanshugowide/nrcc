import re
_DIAC = re.compile(r'[\u0617-\u061A\u064B-\u0652]')
_ARABIC_DIGITS = "٠١٢٣٤٥٦٧٨٩"
_EXT_ARABIC_DIGITS = "۰۱۲۳۴۵۶۷۸۹"

def strip_diacritics(s: str) -> str:
    return re.sub(_DIAC, '', s)

def normalize_ar(s: str) -> str:
    if not isinstance(s, str):
        return s
    s = strip_diacritics(s)
    s = s.replace('ـ', '')  # tatweel
    s = s.replace('أ','ا').replace('إ','ا').replace('آ','ا')
    s = s.replace('ى','ي').replace('ؤ','و').replace('ئ','ي')
    s = s.replace('،', ',').replace('؛',';').replace('؟','?')
    s = s.replace('“','"').replace('”','"').replace('’',"'")
    return s

def to_western_digits(s: str) -> str:
    trans = {ord(a): ord('0')+i for i,a in enumerate(_ARABIC_DIGITS)}
    trans.update({ord(a): ord('0')+i for i,a in enumerate(_EXT_ARABIC_DIGITS)})
    return s.translate(trans)

def tokenize_ar(s: str) -> list[str]:
    s = normalize_ar(to_western_digits(s))
    return re.findall(r'[\u0621-\u064A0-9]+', s)
