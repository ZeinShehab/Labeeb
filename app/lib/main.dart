import 'dart:async';
import 'dart:io';

import 'package:camera/camera.dart';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  final firstCamera = cameras.elementAt(1);

  runApp(
    MaterialApp(
      theme: ThemeData.dark(),
      home: TakePictureScreen(
        camera: firstCamera,
      ),
    ),
  );
}

class TakePictureScreen extends StatefulWidget {
  const TakePictureScreen({
    Key? key,
    required this.camera,
  }) : super(key: key);

  final CameraDescription camera;

  @override
  TakePictureScreenState createState() => TakePictureScreenState();
}

class TakePictureScreenState extends State<TakePictureScreen> {
  late CameraController _controller;
  late Future<void> _initializeControllerFuture;
  bool isCapturing = false; // Flag to track if the camera is on or off

  Future<void> captureFrames() async {

    while (isCapturing) {
      print('Running...');
      // final frame = _controller.takePicture();
      // await Future.delayed(Duration(seconds: 1));
      XFile picture = await _controller.takePicture();

  // Create a `http.MultipartRequest`
      var request = http.MultipartRequest('POST', Uri.parse('http://192.168.1.103:5000/predict'));

      // Attach the image file to the request
      request.files.add(await http.MultipartFile.fromPath('image', picture.path));

      // Send the request
      var response = await request.send();

      // Read the response
      String responseBody = await response.stream.bytesToString();

      // Display the response
      print(responseBody);
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
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Take a picture')),
      body: FutureBuilder<void>(
        future: _initializeControllerFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.done) {
            return CameraPreview(_controller);
          } else {
            return const Center(child: CircularProgressIndicator());
          }
        },
      ),
      floatingActionButton: Row(
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
    );
  }
}
