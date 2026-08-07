import 'dart:io';

import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';

import 'capture/audio_recorder.dart';
import 'capture/voice_entry.dart';
import 'capture/whisper_transcriber.dart';

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
  final WhisperTranscriber _transcriber = WhisperTranscriber();
  String _status = '初始化…';

  @override
  void initState() {
    super.initState();
    _maybeInitModel();
  }

  Future<void> _maybeInitModel() async {
    final dir = await getApplicationDocumentsDirectory();
    final modelDir = '${dir.path}/whisper-small';
    if (await File('$modelDir/encoder.int8.onnx').exists()) {
      _transcriber.init(modelDir);
      if (mounted) setState(() => _status = '模型就绪，长按麦克风说话');
    } else {
      if (mounted) setState(() => _status = '长按说话（模型未装，仅录音）');
    }
  }

  Future<void> _onStart() async {
    _entry.onStart();
    await _recorder.start();
    if (mounted) setState(() => _status = '录音中…松手提交');
  }

  Future<void> _onSubmit() async {
    final path = await _recorder.stop();
    _entry.onSubmit();
    String? text;
    if (path != null && _transcriber.isReady) {
      text = _transcriber.transcribe(path);
    }
    if (mounted) {
      setState(() => _status = text == null ? '已录: $path' : '转写: $text');
    }
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
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            Icon(recording ? Icons.mic : Icons.mic_none, size: 72,
                color: recording ? const Color(0xFFEF4444) : const Color(0xFF3B82F6)),
            const SizedBox(height: 16),
            Text(_status, textAlign: TextAlign.center, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 8),
            Text('状态: ${_entry.state.name}', style: const TextStyle(color: Colors.grey)),
          ]),
        ),
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
