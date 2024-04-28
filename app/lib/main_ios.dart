import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:flutter/services.dart'
    show Clipboard, ClipboardData, rootBundle;
import 'sentence_generator.dart';
import 'combination_map.dart';
import 'package:google_fonts/google_fonts.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  final firstCamera = cameras.elementAt(1);
  final labelData = await rootBundle.loadString('assets/labels-arabic.txt');
  final wordData = await rootBundle.loadString('assets/words-arabic.txt');
  final gestureData = await rootBundle.loadString('assets/gestures-arabic.txt');
  final combinationData =
      await rootBundle.loadString('assets/combinations-arabic.json');

  final combinations =
      await json.decode(combinationData).cast<String, String>();
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
  bool captureGestureSequence =
      false; // Flag to track if capturing gesture sequence is on or off
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

        var request = http.MultipartRequest(
            'POST', Uri.parse('http://192.168.0.105:5000/predict')); // home
        request.files
            .add(await http.MultipartFile.fromPath('image', picture.path));
        var response = await request.send();
        String responseBody = await response.stream.bytesToString();
        final jsonData = jsonDecode(responseBody);

        prediction = jsonData['prediction'];

        if (prediction == -1) {
          continue;
        }

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
      await Future.delayed(const Duration(seconds: 1));
    }
    while (captureGestureSequence && isCapturing == false) {
      int sequenceLength =
          10; // Adjust the number of frames to capture for gesture sequence
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

      var request = http.MultipartRequest(
          'POST', Uri.parse('http://192.168.0.105:5000/predict_gesture'));
      for (int i = 0; i < pictureSequence.length; i++) {
        request.files.add(await http.MultipartFile.fromPath(
            'image', pictureSequence[i].path));
      }
      var responseGesture = await request.send();
      String responseBodyGesture = await responseGesture.stream.bytesToString();
      final jsonDataGesture = jsonDecode(responseBodyGesture);

      prediction = jsonDataGesture['prediction'];

      print("Gesture $prediction");

      if (prediction == -1) {
        continue;
      }
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
      await Future.delayed(const Duration(seconds: 1));
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
      height: 300, // Adjust the height as needed
      width: 300,
      // Define the appearance of the popup widget here
      child: Center(
        child: SingleChildScrollView(
          scrollDirection: Axis.vertical, // Scroll vertically
          child: Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text(
              bestSentence,
              style: GoogleFonts.roboto(
                  textStyle: const TextStyle(
                fontSize: 30,
                color: Color(0xffe0e3f6),
              )),
              textAlign: TextAlign.center,
            ),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    Color backgroundColor = const Color(0xff1f1e23);
    Color lightBackgroundColor = const Color(0xff404758);
    Color darkBackgroundColor = const Color(0xff121317);
    Color primaryColor = const Color(0xffadc6ff);
    Color secondaryColor = const Color(0xff193469);
    Color textColor = const Color(0xffe0e3f6);

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
            child: Container(
              decoration: BoxDecoration(
                color: backgroundColor, // Set background color
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(15),
                  topRight: Radius.circular(15),
                ),
              ),
              child: Padding(
                padding: const EdgeInsets.all(15),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Row(
                      // ADD THE BACKGROUND HERE
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
                                  content: Text(
                                    'Text copied to clipboard',
                                    style: GoogleFonts.roboto(),
                                  ),
                                ),
                              );
                            },
                            child: Container(
                              padding: const EdgeInsets.all(8),
                              // padding: const EdgeInsets.fromLTRB(0, 8, 0, 8),
                              decoration: BoxDecoration(
                                color: darkBackgroundColor,
                                borderRadius: BorderRadius.circular(15),
                              ),
                              child: Center(
                                child: SingleChildScrollView(
                                  scrollDirection: Axis.horizontal,
                                  child: Text(
                                    bestSentence,
                                    style: GoogleFonts.roboto(
                                        textStyle: TextStyle(
                                      fontSize: 25,
                                      color: textColor, // Text color
                                    )),
                                    textAlign: TextAlign.start,
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 15),
                        ElevatedButton(
                          onPressed: clearText,
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(
                              vertical: 10,
                              horizontal: 15,
                            ),
                            backgroundColor:
                                lightBackgroundColor, // Change button color
                          ),
                          child: Text('Clear',
                              style: GoogleFonts.roboto(
                                  textStyle: TextStyle(
                                      fontSize: 12, color: textColor))),
                        ),
                      ],
                    ),
                    const SizedBox(height: 15),
                    IntrinsicHeight(
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                        children: [
                          Column(
                            mainAxisSize: MainAxisSize
                                .min, // Keep the column size to minimum
                            mainAxisAlignment: MainAxisAlignment
                                .center, // Center the items vertically
                            children: <Widget>[
                              FloatingActionButton(
                                shape: const CircleBorder(),
                                backgroundColor: captureGestureSequence
                                    ? primaryColor
                                    : lightBackgroundColor, // Button color
                                child: Icon(
                                  captureGestureSequence
                                      ? Icons.waving_hand_outlined
                                      : Icons.waving_hand_outlined,
                                  color: captureGestureSequence
                                      ? secondaryColor
                                      : textColor, // Icon color
                                ),
                                onPressed: () {
                                  if (captureGestureSequence) {
                                    setState(() {
                                      captureGestureSequence = false;
                                      _controller.setFlashMode(FlashMode.off);
                                      print(captureGestureSequence);
                                      captureFrames();
                                    });
                                  } else {
                                    setState(() {
                                      captureGestureSequence = true;
                                      print(captureGestureSequence);
                                      _controller.setFlashMode(FlashMode.off);
                                      captureFrames();
                                    });
                                  }
                                },
                              ),
                              const SizedBox(
                                  height: 8), // Space between button and text
                              Text(
                                "Gesture", // Label text
                                textAlign: TextAlign.center,
                                style: GoogleFonts.roboto(
                                    textStyle: TextStyle(
                                  color:
                                      textColor, // Text color, change as needed
                                  fontSize:
                                      12, // Adjust the font size as needed
                                  fontWeight: FontWeight.w400,
                                )),
                              ),
                            ],
                          ),
                          VerticalDivider(
                            thickness: 1,
                            color: primaryColor,
                            indent: 5,
                            endIndent: 20,
                          ),
                          Column(
                            mainAxisSize: MainAxisSize
                                .min, // Keep the column size to minimum
                            mainAxisAlignment: MainAxisAlignment
                                .center, // Center the items vertically
                            children: <Widget>[
                              FloatingActionButton(
                                  shape: const CircleBorder(),
                                  onPressed: () {
                                    // Toggle capture state
                                    if (isCapturing) {
                                      _controller.setFlashMode(FlashMode.off);
                                      stopCapture();
                                    } else {
                                      _controller.setFlashMode(FlashMode.off);
                                      startCapture();
                                    }
                                    // Update capture state
                                  },
                                  backgroundColor: isCapturing
                                      ? primaryColor
                                      : lightBackgroundColor, // Change button color
                                  child: Icon(
                                    isCapturing
                                        ? Icons.front_hand_outlined
                                        : Icons.front_hand_outlined,
                                    color: isCapturing
                                        ? secondaryColor
                                        : textColor,
                                  )),
                              const SizedBox(
                                  height: 8), // Space between button and text
                              Text(
                                "Symbol", // Label text
                                textAlign: TextAlign.center,
                                style: GoogleFonts.roboto(
                                    textStyle: TextStyle(
                                  color:
                                      textColor, // Text color, change as needed
                                  fontSize:
                                      12, // Adjust the font size as needed
                                  fontWeight: FontWeight.w400,
                                )),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          )
        ],
      ),
    );
  }
}
