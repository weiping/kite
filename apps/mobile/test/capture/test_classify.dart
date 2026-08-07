import 'package:flutter_test/flutter_test.dart';
import 'package:kite_mobile/capture/classify.dart';

void main() {
  test('触发词产出任务', () {
    final items = classify('要买牛奶');
    expect(items.any((i) => i.kind == 'task'), true);
  });

  test('无触发词归笔记', () {
    final items = classify('天空很蓝');
    expect(items.isEmpty, false);
    expect(items.every((i) => i.kind == 'note'), true);
  });

  test('多类产出', () {
    final items = classify('明天开会。要买牛奶。');
    expect(items.any((i) => i.kind == 'task'), true);
    expect(items.any((i) => i.kind == 'event'), true);
  });

  test('标题非空', () {
    final items = classify('一句话。');
    expect(items.isEmpty, false);
    for (final i in items) {
      expect(i.title.isEmpty, false);
    }
  });
}
