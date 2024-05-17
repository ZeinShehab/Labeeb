import 'dart:async';
import 'dart:ffi';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'dart:io';
import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
// import 'package:flutter/services.dart'
//     show Clipboard, ClipboardData, rootBundle;
import 'package:path/path.dart';
import 'sentence_generator.dart';
import 'combination_map.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';
import 'package:path_provider/path_provider.dart';
import 'mediapipe_ios.dart';
import 'package:image/image.dart' as img;

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


// class HandLandmarkDetector {
//   static const MethodChannel _channel = MethodChannel('hand_landmark_detector');

//   static Future<List<Map<String, double>>?> detectHandLandmarks() async {
//   try {

//     final List<dynamic>? result = await _channel.invokeMethod('detectHandLandmarks');
//     if (result != null) {
//       return result.map<Map<String, double>>((dynamic landmark) {
//         return {
//           'x': landmark['x'] as double,
//           'y': landmark['y'] as double,
//           // Add z if needed
//         };
//       }).toList();
//     }
//   } on PlatformException catch (e) {
//     print("Error: '${e.message}'.");
//   }
//   return null;
// }

// }

// class HelloWorldChannel {
//   // static const _channel =
//   //     MethodChannel('hand_landmark_detector');

//   // static Future<String?> getHelloWorld() async {
//   //   try {
//   //     return await _channel.invokeMethod('detectHandLandmarks');
//   //   } on PlatformException catch (e) {
//   //     print("Failed to get hello world: '${e.message}'.");
//   //     return null;
//   //   }
//   static const platform = MethodChannel('samples.flutter.dev/battery');
//   // Get battery level.

// static Future<List<List<double>>> get_landmarks(Uint8List image) async {
//   try {
//     final result = await platform.invokeMethod<List>('gen_key', {"image": image});
//     if (result != null) {
//       // Convert each element of the inner lists to Double
//       List<List<double>> formattedResult = [];
//       for (var list in result) {
//         List<double> doubleList = [];
//         for (var element in list) {
//           try {
//             double value = element.toDouble(); // Change this line
//             doubleList.add(value);
//           } catch (e) {
//             print('Error converting $element to double: $e');
//             // Handle the conversion error, you can choose to ignore or handle it based on your requirements
//           }
//         }
//         formattedResult.add(doubleList);
//       }
      
//       print("Formatted Result:");
//       for (List<double> sublist in formattedResult) {
//         print(sublist);
//       }
//       print(formattedResult.length);
      
//       return formattedResult;
//     } else {
//       // Handle the case when result is null
//       print("[!] Error: Result is null");
//       return [];
//     }
//   } on PlatformException catch (e) {
//     print("[!] Error: $e"); 
//     return [];
//   }
// }

// }


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
  String server_url = "https://lsltranslator.pythonanywhere.com";
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
    // print("Capture Frames");
    while (isCapturing) {
      print('Running...');
      await _controller.startVideoRecording();
      final XFile picture = await _controller.takePicture();

      final img.Image? capturedImage = img.decodeImage(await File(picture.path).readAsBytes());
      final img.Image orientedImage = img.bakeOrientation(capturedImage!);
      await File(picture.path).writeAsBytes(img.encodeJpg(orientedImage));
    

      await Future.delayed(const Duration(seconds: 1));
      videoFile = await _controller.stopVideoRecording();
      
      // List<dynamic>? handLandmarks = await HandLandmarkDetector.detectHandLandmarks();
      // print(handLandmarks); 

      if (videoFile != null) {
      // int prediction = -1;

      final fileBytes = await File(picture.path).readAsBytes();
      
      // List<List<double>> ? landmarks = await mediapipeUtils.getLandmarks(fileBytes);
      // final test_image = await rootBundle.load('assets/test_image1.jpg');
      // final test_bytes = await image.tobyte
      // final ByteData data = await rootBundle.load('assets/test_image1.jpg');

      // List<double> ? landmarks = await mediapipeUtils.getLandmarks(data.buffer.asUint8List());
      List<double> ? landmarks = await mediapipeUtils.getLandmarks(fileBytes);
      
      SymbolClassifier symbol_classifier = SymbolClassifier();
      final resp = await symbol_classifier.predictConfidence(landmarks);
      int prediction = resp[0];
      int confidence = resp[1];
      print(prediction);
      print(confidence);
      // print("Flutter response: $resp"); 
      // final tempDir = await getTemporaryDirectory();
      // final tempPath = '${tempDir.path}/${DateTime.now().millisecondsSinceEpoch}.jpg'; 
      // final compressedFile = await FlutterImageCompress.compressAndGetFile(
      //   picture.path,
      //   tempPath,
      //   minHeight: 1080, // Adjust these parameters as needed
      //   minWidth: 1080,  // Adjust these parameters as needed
      //   quality: 10,
      //   keepExif: false
      // );
      //   var request = http.MultipartRequest(
      //       'POST', Uri.parse(server_url +'/predict')); // home
      //   request.files
      //       .add(await http.MultipartFile.fromPath('image', compressedFile!.path));
      //   Stopwatch stopwatch = Stopwatch()..start();
      //   var response = await request.send();
      //   stopwatch.stop();
      //   double elapsedTimeInSeconds = stopwatch.elapsedMilliseconds / 1000;
      //   print('Elapsed time for response: $elapsedTimeInSeconds');
      //   String responseBody = await response.stream.bytesToString();
      //   final jsonData = jsonDecode(responseBody);

      //   prediction = jsonData['prediction'];

        if (prediction == -1) {
          continue;
        }

        setState(() {
          if (confidence > 70) {
            
          
          charSequence.add(labels[prediction]);
          //charSequence.insert(0, labels[prediction]);
          }
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
    // ----------------------------- GESTURES ----------------------------
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
      // List<XFile?> compressed = [];
      // for (int i = 0; i < 10; i++) {
      // // final fileBytes = await File(pictureSequence[i].path).readAsBytes();
      // final tempDir = await getTemporaryDirectory();
      // final tempPath = '${tempDir.path}/${DateTime.now().millisecondsSinceEpoch}.jpg'; 
      // final compressedFile = await FlutterImageCompress.compressAndGetFile(
      //   pictureSequence[i].path,
      //   tempPath,
      //   minHeight: 1080, // Adjust these parameters as needed
      //   minWidth: 1080,  // Adjust these parameters as needed
      //   quality: 10,
      //   keepExif: false
      // );
      // compressed.add(compressedFile);
      // }
      
      var request = http.MultipartRequest(
          'POST', Uri.parse(server_url+'/predict_gesture'));
      for (int i = 0; i < pictureSequence.length; i++) {
        request.files.add(await http.MultipartFile.fromPath(
            'image', pictureSequence[i].path));
            // 'image', compressed[i]!.path));
      }
      // // Stopwatch stopwatch = Stopwatch()..start();
      var responseGesture = await request.send();
      // // stopwatch.stop();
      // // double elapsedTimeInSeconds = stopwatch.elapsedMilliseconds / 1000;
      // print('Elapsed time for response: $elapsedTimeInSeconds');
      String responseBodyGesture = await responseGesture.stream.bytesToString();
      final jsonDataGesture = jsonDecode(responseBodyGesture);

      prediction = jsonDataGesture['prediction'];
      // GestureClassifier gesture_classifier = GestureClassifier();
      // List<Uint8List> gesture_images = [];

      // for (var i = 0; i < 10; i++) {
      //   final fileBytes = await File(pictureSequence[i].path).readAsBytes();
      //   gesture_images.add(fileBytes);
      // }
      
      // List<double> ? landmarks = await mediapipeUtils.getGestureLandmarks(gesture_images);
      // if (landmarks.length == 0 ) continue;
      // final result = await  gesture_classifier.predictConfidence(landmarks);
      
      // int gesturePrediction = result[0];
      // int gestureConfidence = result[1];

      // print("Gesture prediction: $gesturePrediction");
      // print("Gesture confidence: $gestureConfidence");

      // print("Gesture $prediction");

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

  void startCapture() async{
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
                                    backgroundColor: darkBackgroundColor,
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
