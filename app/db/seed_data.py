"""内置 Mock 词库数据（初中 / 高中各约 50 词）与初始化逻辑。

每个词条格式：(spelling, meaning_cn, phonetic, pos, grade, confusion_group)
confusion_group 用于形近词/易混词比对，空字符串表示无易混词组。
"""
from app.db.database import get_connection

JUNIOR_WORDS = [
    ("apple", "苹果", "/ˈæpl/", "n.", "初中", ""),
    ("banana", "香蕉", "/bəˈnɑːnə/", "n.", "初中", ""),
    ("orange", "橙子；橙色的", "/ˈɒrɪndʒ/", "n./adj.", "初中", ""),
    ("book", "书；预订", "/bʊk/", "n./v.", "初中", ""),
    ("pencil", "铅笔", "/ˈpensl/", "n.", "初中", ""),
    ("teacher", "老师", "/ˈtiːtʃə/", "n.", "初中", ""),
    ("student", "学生", "/ˈstjuːdnt/", "n.", "初中", ""),
    ("school", "学校", "/skuːl/", "n.", "初中", ""),
    ("friend", "朋友", "/frend/", "n.", "初中", ""),
    ("family", "家庭", "/ˈfæməli/", "n.", "初中", ""),
    ("mother", "母亲", "/ˈmʌðə/", "n.", "初中", ""),
    ("father", "父亲", "/ˈfɑːðə/", "n.", "初中", ""),
    ("sister", "姐妹", "/ˈsɪstə/", "n.", "初中", ""),
    ("brother", "兄弟", "/ˈbrʌðə/", "n.", "初中", ""),
    ("water", "水；浇水", "/ˈwɔːtə/", "n./v.", "初中", ""),
    ("food", "食物", "/fuːd/", "n.", "初中", ""),
    ("music", "音乐", "/ˈmjuːzɪk/", "n.", "初中", ""),
    ("sport", "运动", "/spɔːt/", "n.", "初中", ""),
    ("morning", "早晨", "/ˈmɔːnɪŋ/", "n.", "初中", ""),
    ("night", "夜晚", "/naɪt/", "n.", "初中", ""),
    ("weather", "天气", "/ˈweðə/", "n.", "初中", "CF_WEATHER"),
    ("whether", "是否", "/ˈweðə/", "conj.", "初中", "CF_WEATHER"),
    ("diary", "日记", "/ˈdaɪəri/", "n.", "初中", ""),
    ("library", "图书馆", "/ˈlaɪbrəri/", "n.", "初中", ""),
    ("beautiful", "美丽的", "/ˈbjuːtɪfl/", "adj.", "初中", ""),
    ("difficult", "困难的", "/ˈdɪfɪkəlt/", "adj.", "初中", ""),
    ("important", "重要的", "/ɪmˈpɔːtnt/", "adj.", "初中", ""),
    ("quiet", "安静的", "/ˈkwaɪət/", "adj.", "初中", "CF_QUIET"),
    ("quite", "相当；很", "/kwaɪt/", "adv.", "初中", "CF_QUIET"),
    ("because", "因为", "/bɪˈkɒz/", "conj.", "初中", ""),
    ("before", "在……之前", "/bɪˈfɔː/", "prep./conj.", "初中", ""),
    ("after", "在……之后", "/ˈɑːftə/", "prep./conj.", "初中", ""),
    ("always", "总是", "/ˈɔːlweɪz/", "adv.", "初中", ""),
    ("never", "从不", "/ˈnevə/", "adv.", "初中", ""),
    ("answer", "回答；答案", "/ˈɑːnsə/", "v./n.", "初中", ""),
    ("question", "问题", "/ˈkwestʃən/", "n.", "初中", ""),
    ("tomorrow", "明天", "/təˈmɒrəʊ/", "n./adv.", "初中", ""),
    ("yesterday", "昨天", "/ˈjestədeɪ/", "n./adv.", "初中", ""),
    ("together", "一起", "/təˈɡeðə/", "adv.", "初中", ""),
    ("remember", "记得", "/rɪˈmembə/", "v.", "初中", ""),
    ("forget", "忘记", "/fəˈɡet/", "v.", "初中", ""),
    ("welcome", "欢迎", "/ˈwelkəm/", "v./adj.", "初中", ""),
    ("different", "不同的", "/ˈdɪfrənt/", "adj.", "初中", ""),
    ("interesting", "有趣的", "/ˈɪntrəstɪŋ/", "adj.", "初中", ""),
    ("delicious", "美味的", "/dɪˈlɪʃəs/", "adj.", "初中", ""),
    ("careful", "仔细的", "/ˈkeəfl/", "adj.", "初中", ""),
    ("dangerous", "危险的", "/ˈdeɪndʒərəs/", "adj.", "初中", ""),
    ("popular", "受欢迎的", "/ˈpɒpjələ/", "adj.", "初中", ""),
    ("holiday", "假日", "/ˈhɒlədeɪ/", "n.", "初中", ""),
    ("garden", "花园", "/ˈɡɑːdn/", "n.", "初中", ""),
]

SENIOR_WORDS = [
    ("adapt", "适应；改编", "/əˈdæpt/", "v.", "高中", "CF_ADAPT"),
    ("adopt", "采纳；收养", "/əˈdɒpt/", "v.", "高中", "CF_ADAPT"),
    ("affect", "影响（动词）", "/əˈfekt/", "v.", "高中", "CF_AFFECT"),
    ("effect", "效果；影响（名词）", "/ɪˈfekt/", "n.", "高中", "CF_AFFECT"),
    ("desert", "沙漠；抛弃", "/ˈdezət/", "n./v.", "高中", "CF_DESSERT"),
    ("dessert", "甜点", "/dɪˈzɜːt/", "n.", "高中", "CF_DESSERT"),
    ("accept", "接受", "/əkˈsept/", "v.", "高中", "CF_ACCEPT"),
    ("except", "除……之外", "/ɪkˈsept/", "prep.", "高中", "CF_ACCEPT"),
    ("advice", "建议（名词）", "/ədˈvaɪs/", "n.", "高中", "CF_ADVICE"),
    ("advise", "建议（动词）", "/ədˈvaɪz/", "v.", "高中", "CF_ADVICE"),
    ("principal", "校长；主要的", "/ˈprɪnsəpl/", "n./adj.", "高中", "CF_PRINCIPAL"),
    ("principle", "原则", "/ˈprɪnsəpl/", "n.", "高中", "CF_PRINCIPAL"),
    ("stationary", "静止的", "/ˈsteɪʃənri/", "adj.", "高中", "CF_STATIONARY"),
    ("stationery", "文具", "/ˈsteɪʃənri/", "n.", "高中", "CF_STATIONARY"),
    ("through", "穿过", "/θruː/", "prep.", "高中", "CF_THROUGH"),
    ("thorough", "彻底的", "/ˈθʌrə/", "adj.", "高中", "CF_THROUGH"),
    ("later", "后来；以后", "/ˈleɪtə/", "adv.", "高中", "CF_LATER"),
    ("latter", "后者", "/ˈlætə/", "adj./n.", "高中", "CF_LATER"),
    ("compliment", "赞美", "/ˈkɒmplɪmənt/", "n./v.", "高中", "CF_COMPLIMENT"),
    ("complement", "补充；补足物", "/ˈkɒmplɪment/", "n./v.", "高中", "CF_COMPLIMENT"),
    ("environment", "环境", "/ɪnˈvaɪrənmənt/", "n.", "高中", ""),
    ("phenomenon", "现象", "/fəˈnɒmɪnən/", "n.", "高中", ""),
    ("attitude", "态度", "/ˈætɪtjuːd/", "n.", "高中", ""),
    ("opportunity", "机会", "/ˌɒpəˈtjuːnəti/", "n.", "高中", ""),
    ("challenge", "挑战", "/ˈtʃælɪndʒ/", "n./v.", "高中", ""),
    ("consequence", "后果", "/ˈkɒnsɪkwəns/", "n.", "高中", ""),
    ("efficient", "高效的", "/ɪˈfɪʃnt/", "adj.", "高中", ""),
    ("sufficient", "充足的", "/səˈfɪʃnt/", "adj.", "高中", ""),
    ("approximately", "大约", "/əˈprɒksɪmətli/", "adv.", "高中", ""),
    ("responsibility", "责任", "/rɪˌspɒnsəˈbɪləti/", "n.", "高中", ""),
    ("achievement", "成就", "/əˈtʃiːvmənt/", "n.", "高中", ""),
    ("appreciate", "欣赏；感激", "/əˈpriːʃieɪt/", "v.", "高中", ""),
    ("approach", "方法；接近", "/əˈprəʊtʃ/", "n./v.", "高中", ""),
    ("appropriate", "适当的", "/əˈprəʊpriət/", "adj.", "高中", ""),
    ("assumption", "假设", "/əˈsʌmpʃn/", "n.", "高中", ""),
    ("available", "可获得的", "/əˈveɪləbl/", "adj.", "高中", ""),
    ("benefit", "益处", "/ˈbenɪfɪt/", "n./v.", "高中", ""),
    ("category", "类别", "/ˈkætəɡəri/", "n.", "高中", ""),
    ("communicate", "交流", "/kəˈmjuːnɪkeɪt/", "v.", "高中", ""),
    ("competition", "竞争；比赛", "/ˌkɒmpəˈtɪʃn/", "n.", "高中", ""),
    ("conclusion", "结论", "/kənˈkluːʒn/", "n.", "高中", ""),
    ("confidence", "自信", "/ˈkɒnfɪdəns/", "n.", "高中", ""),
    ("considerable", "相当大的", "/kənˈsɪdərəbl/", "adj.", "高中", ""),
    ("contribute", "贡献；促成", "/kənˈtrɪbjuːt/", "v.", "高中", ""),
    ("crucial", "关键的", "/ˈkruːʃl/", "adj.", "高中", ""),
    ("definitely", "明确地", "/ˈdefɪnətli/", "adv.", "高中", ""),
    ("demonstrate", "证明；演示", "/ˈdemənstreɪt/", "v.", "高中", ""),
    ("determine", "决定；确定", "/dɪˈtɜːmɪn/", "v.", "高中", ""),
    ("distinguish", "区分", "/dɪˈstɪŋɡwɪʃ/", "v.", "高中", ""),
    ("emphasize", "强调", "/ˈemfəsaɪz/", "v.", "高中", ""),
]


def seed_if_empty(force: bool = False) -> int:
    """若词库为空（或 force=True），写入内置词库。返回新增词数。"""
    conn = get_connection()
    try:
        existing = conn.execute("SELECT COUNT(*) AS c FROM Word").fetchone()["c"]
        if existing > 0 and not force:
            return 0
        inserted = 0
        for row in JUNIOR_WORDS + SENIOR_WORDS:
            cur = conn.execute(
                "INSERT OR IGNORE INTO Word "
                "(spelling, phonetic, meaning_cn, pos, grade, confusion_group) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (row[0], row[2], row[1], row[3], row[4], row[5]),
            )
            inserted += cur.rowcount
        conn.commit()
        return inserted
    finally:
        conn.close()