import 'dart:async';
import 'dart:convert';
import 'dart:ffi';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

import 'package:flutter/services.dart' show rootBundle;

import 'sentence_generator.dart';
import 'combination_map.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  final firstCamera = cameras.elementAt(1);

  final labelData = await rootBundle.loadString('assets/labels-arabic.txt');
  final wordData = await rootBundle.loadString('assets/words-arabic.txt');
  final combinationData =
      await rootBundle.loadString('assets/combinations-arabic.txt');

  final combinations = await json.decode(combinationData);
  final labels = LineSplitter.split(labelData).toList();
  final words = LineSplitter.split(wordData).toList();

  runApp(
    MaterialApp(
      theme: ThemeData.dark(),
      home: TakePictureScreen(
          camera: firstCamera,
          labels: labels,
          words: words,
          combinations: combinations),
    ),
  );
}

class TakePictureScreen extends StatefulWidget {
  const TakePictureScreen(
      {Key? key,
      required this.camera,
      required this.labels,
      required this.words,
      required this.combinations})
      : super(key: key);

  final CameraDescription camera;
  final List<String> labels;
  final List<String> words;
  final Map<String, String> combinations;

  @override
  TakePictureScreenState createState() => TakePictureScreenState();
}

class TakePictureScreenState extends State<TakePictureScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  late List<String> labels;
  late List<String> words;
  late Map<String, String> combinations;

  bool isCapturing = false; // Flag to track if the camera is on or off
  List<String> charSequence = [];
  String bestSentence = "";
  void clearText() {
    setState(() {
      bestSentence = "";
      charSequence.clear();
    });
  }

  Future<void> captureFrames() async {
    while (isCapturing) {
      print('Running...');
      // final frame = _controller.takePicture();
      // await Future.delayed(Duration(seconds: 1));
      XFile picture = await _controller.takePicture();

      // Create a `http.MultipartRequest`
      var request = http.MultipartRequest(
          'POST', Uri.parse('http://192.168.1.105:5000/predict'));

      // Attach the image file to the request
      request.files
          .add(await http.MultipartFile.fromPath('image', picture.path));

      // Send the request
      var response = await request.send();

      // Read the response
      String responseBody = await response.stream.bytesToString();
      final jsonData = jsonDecode(responseBody);
      int prediction = jsonData['prediction'];

      if (prediction == -1) {
        continue;
      }
      setState(() {
        charSequence.add(labels[prediction]);
        // charSequence.insert(0, labels[prediction]);
      });

      setState(() {
        charSequence = mapCombinations(charSequence, combinations);
        bestSentence = generateBestSentence(charSequence.join(""), words);
      });

      // Display the response
      print("prediction: $prediction");
      print("Sequence : $charSequence");
      print("best sentence : $bestSentence");
      await Future.delayed(Duration(seconds: 1));
    }
  }

  void startCapture() {
    setState(() {
      isCapturing = true;
    });

    captureFrames();
  }

  void stopCapture() {
    setState(() {
      isCapturing = false;
    });
  }

  @override
  void initState() {
    super.initState();
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.medium,
    );
    _initializeControllerFuture = _controller.initialize();
    labels = widget.labels;
    words = widget.words;
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // ... (previous code remains unchanged)

// ... (previous code remains unchanged)

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Translate')),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Expanded(
            child: FutureBuilder<void>(
              future: _initializeControllerFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.done) {
                  return CameraPreview(_controller);
                } else {
                  return const Center(child: CircularProgressIndicator());
                }
              },
            ),
          ),
          SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Column(
                children: [
                  Text(
                    bestSentence,
                    style: TextStyle(fontSize: 16),
                  ),
                  SizedBox(height: 8),
                  ElevatedButton(
                    onPressed: clearText,
                    child: Text('Clear'),
                  ),
                ],
              ),
            ],
          ),
          SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              FloatingActionButton(
                onPressed: () {
                  if (!isCapturing) {
                    startCapture();
                  }
                },
                child: Icon(Icons.camera_alt),
              ),
              FloatingActionButton(
                onPressed: () {
                  // Add functionality for the second button
                  // This is just a placeholder, you can replace it with your own logic
                  stopCapture();
                },
                child: Icon(Icons.stop),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
