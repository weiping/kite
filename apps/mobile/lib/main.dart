import 'package:flutter/material.dart';

import 'capture/audio_recorder.dart';
import 'capture/voice_entry.dart';

void main() => runApp(const KiteApp());

class KiteApp extends StatelessWidget {
  const KiteApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'Kite',
        theme: ThemeData(
            colorSchemeSeed: const Color(0xFF3B82F6), useMaterial3: true),
        home: const VoiceScreen(),
      );
}

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({super.key});
  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  final VoiceEntry _entry = VoiceEntry();
  final VoiceRecorder _recorder = VoiceRecorder();
  String _status = '长按麦克风说话';

  Future<void> _onStart() async {
    _entry.onStart();
    await _recorder.start();
    if (mounted) setState(() => _status = '录音中…松手提交，点按钮取消');
  }

  Future<void> _onSubmit() async {
    final path = await _recorder.stop();
    _entry.onSubmit();
    if (mounted) setState(() => _status = path == null ? '未录到' : '已录: $path');
  }

  void _onCancel() {
    _recorder.cancel();
    _entry.onCancel();
    setState(() => _status = '已取消');
  }

  @override
  Widget build(BuildContext context) {
    final recording = _entry.state == VoiceState.recording;
    return Scaffold(
      appBar: AppBar(title: const Text('Kite 速记')),
      body: Center(
        child: Column(mainAxisSize: MainAxisSize.min, children: [
          Icon(recording ? Icons.mic : Icons.mic_none, size: 72,
              color: recording ? const Color(0xFFEF4444) : const Color(0xFF3B82F6)),
          const SizedBox(height: 16),
          Text(_status, style: const TextStyle(fontSize: 16)),
          const SizedBox(height: 8),
          Text('状态: ${_entry.state.name}', style: const TextStyle(color: Colors.grey)),
        ]),
      ),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerFloat,
      floatingActionButton: GestureDetector(
        onLongPressStart: (_) => _onStart(),
        onLongPressEnd: (_) => _onSubmit(),
        child: FloatingActionButton.large(
          onPressed: _onCancel,
          backgroundColor: const Color(0xFF3B82F6),
          child: Icon(recording ? Icons.stop : Icons.mic, color: Colors.white),
        ),
      ),
    );
  }
}
