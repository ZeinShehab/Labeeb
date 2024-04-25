import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart' show Clipboard, ClipboardData, rootBundle;
import 'sentence_generator.dart';
import 'combination_map.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  final firstCamera = cameras.elementAt(1);
  final labelData = await rootBundle.loadString('assets/labels-arabic.txt');
  final wordData = await rootBundle.loadString('assets/words-arabic.txt');
  final gestureData = await rootBundle.loadString('assets/gestures-arabic.txt');
  final combinationData = await rootBundle.loadString('assets/combinations-arabic.json');

  final combinations = await json.decode(combinationData).cast<String, String>();
  final labels = LineSplitter.split(labelData).toList();
  final words = LineSplitter.split(wordData).toList();
  final gestures = LineSplitter.split(gestureData).toList();

  runApp(
    MaterialApp(
      theme: ThemeData.dark(),
      home: TakePictureScreen(
        camera: firstCamera,
        labels: labels,
        words: words,
        gestures: gestures,
        combinations: combinations,
      ),
    ),
  );
}

class TakePictureScreen extends StatefulWidget {
  const TakePictureScreen({
    Key? key,
    required this.camera,
    required this.labels,
    required this.words,
    required this.gestures,
    required this.combinations,
  }) : super(key: key);

  final CameraDescription camera;
  final List<String> labels;
  final List<String> words;
  final Map<String, String> combinations;
  final List<String> gestures;

  @override
  TakePictureScreenState createState() => TakePictureScreenState();
}

class TakePictureScreenState extends State<TakePictureScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  late List<String> labels;
  late List<String> words;
  late Map<String, String> combinations;
  late List<String> gestures;
  late XFile? videoFile;

  bool isCapturing = false; // Flag to track if the camera is on or off
  bool captureGestureSequence = false; // Flag to track if capturing gesture sequence is on or off
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
      await _controller.startVideoRecording();
      final XFile picture = await _controller.takePicture();
      await Future.delayed(const Duration(seconds: 1));
      videoFile = await _controller.stopVideoRecording();

      if (videoFile != null) {
          int prediction = -1;

          var request = http.MultipartRequest('POST', Uri.parse('http://192.168.1.101:5000/predict')); // home
          request.files.add(await http.MultipartFile.fromPath('image', picture.path));
          var response = await request.send();
          String responseBody = await response.stream.bytesToString();
          final jsonData = jsonDecode(responseBody);

          prediction = jsonData['prediction'];

         setState(() {
            charSequence.add(labels[prediction]);
            //charSequence.insert(0, labels[prediction]);
        });

        setState(() {
          charSequence = mapCombinations(charSequence, combinations);
          bestSentence = generateBestSentence(charSequence.join(""), words);
        });
        
        print("Sequence : $charSequence");
        print("best sentence : $bestSentence");
      
        File(picture.path).deleteSync();
      }
      await Future.delayed(Duration(seconds: 1));
    }
    while (captureGestureSequence && isCapturing == false) {
        int sequenceLength = 10; // Adjust the number of frames to capture for gesture sequence
        print('Running...');
        List<XFile> pictureSequence = [];
        int prediction = -1;
        
        int i = 0;
        while (captureGestureSequence && i < sequenceLength) {
          await _controller.startVideoRecording();
          await Future.delayed(const Duration(milliseconds: 10));
          XFile gesturePicture = await _controller.takePicture();
          await _controller.stopVideoRecording();
          pictureSequence.add(gesturePicture);
          i += 1;
        }
        setState(() {
          captureGestureSequence = false;
        });

          var request = http.MultipartRequest('POST', Uri.parse('http://192.168.1.101:5000/predict_gesture'));
          for (int i = 0; i < pictureSequence.length; i++) {
            request.files.add(await http.MultipartFile.fromPath('image', pictureSequence[i].path));
          }
          var responseGesture = await request.send();
          String responseBodyGesture = await responseGesture.stream.bytesToString();
          final jsonDataGesture = jsonDecode(responseBodyGesture);
          prediction = jsonDataGesture['prediction'];
          print("Gesture $prediction");
         setState(() {
            charSequence.add(gestures[prediction]);
            //charSequence.insert(0, labels[prediction]);
        });

        setState(() {
          charSequence = mapCombinations(charSequence, combinations);
          bestSentence = generateBestSentence(charSequence.join(""), words);
        });
        
        print("Sequence : $charSequence");
        print("best sentence : $bestSentence");
      
        for (int i = 0; i < pictureSequence.length; i++) {
            File(pictureSequence[i].path).deleteSync();
        }
        pictureSequence.clear();
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

  void toggleCaptureGestureSequence() {
    setState(() {
      captureGestureSequence = !captureGestureSequence;
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
    _controller.setFlashMode(FlashMode.off);
    labels = widget.labels;
    words = widget.words;
    gestures = widget.gestures;
    combinations = widget.combinations;
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Widget _popupWidget() {
    return SizedBox(
      height: 100, // Adjust the height as needed
      width: double.infinity,
      // Define the appearance of the popup widget here
      child: Center(
        child: Text(
          bestSentence,
          style: TextStyle(
            fontSize: 20,
            color: Colors.white,
          ),
          textAlign: TextAlign.center,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          FutureBuilder<void>(
            future: _initializeControllerFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.done) {
                return SizedBox.expand(
                  child: ClipRect(
                    child: OverflowBox(
                      alignment: Alignment.center,
                      child: FittedBox(
                        fit: BoxFit.cover,
                        child: SizedBox(
                          width: _controller.value.previewSize!.height,
                          height: _controller.value.previewSize!.width,
                          child: CameraPreview(_controller),
                        ),
                      ),
                    ),
                  ),
                );
              } else {
                return const Center(child: CircularProgressIndicator());
              }
            },
          ),
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: GestureDetector(
                          onTap: () {
                            // Show the popup widget when the text is tapped
                            showDialog(
                              context: context,
                              builder: (BuildContext context) {
                                return AlertDialog(
                                  content: _popupWidget(),
                                );
                              },
                            );
                          },
                          onDoubleTap: () async {
                            await Clipboard.setData(
                              ClipboardData(text: bestSentence),
                            );
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('Text copied to clipboard'),
                              ),
                            );
                          },
                          child: Container(
                            padding: EdgeInsets.all(8),
                            decoration: BoxDecoration(
                              color: Colors.black.withOpacity(0.5),
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Center(
                              child: GestureDetector(
                                onTap: () {
                                  print("Tapped on text");
                                },
                                onDoubleTap: () {
                                  print("Double tapped on text");
                                  // Handle double tap action
                                  // Example: Copy text to clipboard
                                  Clipboard.setData(
                                    ClipboardData(text: bestSentence),
                                  );
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text('Text copied to clipboard'),
                                    ),
                                  );
                                },
                                child: Text(
                                  bestSentence,
                                  style: TextStyle(
                                    fontSize: 16,
                                    color: Colors.white, // Text color
                                  ),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            ),
                          ),
                        ),
                      ),
                      SizedBox(width: 8),
                      ElevatedButton(
                        onPressed: clearText,
                        child: Text(
                          'Clear',
                          style: TextStyle(fontSize: 12),
                        ),
                        style: ElevatedButton.styleFrom(
                          padding: EdgeInsets.symmetric(
                            vertical: 10,
                            horizontal: 16,
                          ),
                        ),
                      ),
                    ],
                  ),
                  SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      if (captureGestureSequence) {
                        setState(() {
                          captureGestureSequence = false;
                          print(captureGestureSequence);
                          captureFrames(); 
                        });
                      }
                      else {
                        setState(() {
                          captureGestureSequence = true;
                          print(captureGestureSequence);
                          captureFrames(); 
                        });
                      }
                    },
                    child: Text(
                      'Start Gesture',
                      style: TextStyle(fontSize: 12),
                    ),
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(
                        vertical: 10,
                        horizontal: 16,
                      ),
                    ),
                  ),
                  SizedBox(height: 16),
                  FloatingActionButton(
                    onPressed: () {
                      // Toggle capture state
                      if (isCapturing) {
                        stopCapture();
                      } else {
                        _controller.setFlashMode(FlashMode.off);
                        startCapture();
                      }
                      // Update capture state
                    },
                    child: Icon(isCapturing ? Icons.stop : Icons.camera_alt),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
