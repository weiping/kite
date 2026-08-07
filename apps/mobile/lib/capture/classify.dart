// 端侧结构化分类（Dart，复刻 services/capture/classify.py 规则）。
// 同一契约 task-struct-classify 的客户端实现；DEC-STRUCT-CLASSIFY 规则分类。
// 离线、纯函数、可测。charter 第4条：规则显式，非 AI 黑箱。

class Item {
  final String kind; // note / task / event
  final String title;
  final String text;
  const Item(this.kind, this.title, this.text);

  Map<String, dynamic> toJson() => {'kind': kind, 'title': title, 'text': text};
  factory Item.fromJson(Map<String, dynamic> j) =>
      Item(j['kind'] as String, j['title'] as String, j['text'] as String);
}

const Set<String> actionWords = {
  '要做', '记得', '别忘了', '计划', '打算', '完成', '办', '买',
  '联系', '回复', '提交', '整理', '准备', '确认',
};

const Set<String> dateWords = {
  '明天', '今天', '后天', '下周一', '下周二', '下周三', '下次',
  '周一', '周二', '周三', '周四', '周五', '周六', '周日',
};

List<String> _sentences(String text) {
  for (final sep in ['。', '！', '？', '!', '?', '\n']) {
    text = text.replaceAll(sep, '$sep\n');
  }
  return text.split('\n').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();
}

String _title(String s, [int n = 20]) => s.substring(0, s.length < n ? s.length : n).trim();

List<Item> classify(String text) {
  final items = <Item>[];
  for (final s in _sentences(text)) {
    if (actionWords.any((w) => s.contains(w))) {
      items.add(Item('task', _title(s), s));
    } else if (dateWords.any((w) => s.contains(w))) {
      items.add(Item('event', _title(s), s));
    }
  }
  if (items.isEmpty) items.add(Item('note', _title(text), text));
  return items;
}
