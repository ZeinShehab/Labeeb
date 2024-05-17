// import 'package:flutter/material.dart';
// import 'package:flutter/services.dart';

// class mediapipeUtils {
//   static const platform = MethodChannel('samples.flutter.dev/battery');

//   static Future<List<List<double>>> getLandmarks(Uint8List image) async {
//     try {
//       final result = await platform.invokeMethod<List>('gen_key', {"image": image});
//       if (result != null) {
//         List<List<double>> landmarks = (result as List).map<List<double>>((list) => list.cast<double>()).toList();

//         // Check if the length of landmarks is exactly 63
//         if (landmarks.length == 63) {
//           // Append 0.0 values until the length becomes 126
//           while (landmarks.length < 126) {
//             landmarks.add(List<double>.filled(3, 0.0));
//           }
//         }

//         print("Formatted Result:");
//         print(landmarks);
//         print(landmarks.length);

//         return landmarks;
//       } else {
//         print("[!] Error: Result is null");
//         return [];
//       }
//     } on PlatformException catch (e) {
//       print("[!] Error: $e");
//       return [];
//     }
//   }
// }
import 'dart:io';
import 'dart:typed_data';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';
import 'package:tflite_flutter/tflite_flutter.dart' as tfl; // as tfl (try method)
import 'package:typed_data/typed_data.dart';

class mediapipeUtils {
  static const platform = MethodChannel('samples.flutter.dev/battery');

  static Future<List<double>> getLandmarks(Uint8List image) async {
    try {



      final result = await platform.invokeMethod<List>('gen_key', {"image": image});

      // List<List<double>> preprocessedLandmarks = result!.map<List<double>>((list) => list.cast<double>()).toList();
      // print(preprocessedLandmarks);

      if (result != null) {
        List<double> landmarks = [];
        for (var item in result) {
          landmarks.add(item.toDouble());
        }

        // Check if the length of landmarks is exactly 63*3
        if (landmarks.length == 63) {
          // Append 0.0 values until the length becomes 126
          while (landmarks.length < 126) {
            landmarks.add(0.0);
          }
        }

        // return preProcessedLandmarks;
        return landmarks;
      } else {
        print("[!] Error: Result is null");
        return [];
      }
    } on PlatformException catch (e) {
      print("[!] Error: $e");
      return [];
    }
  }
  // static Future<List<double>> getGestureLandmarks(List<Uint8List> images) async {
  //   try {

  //     final result = await platform.invokeMethod<List>('gen_key_seq', {"images": images});
  //     if (result != null) {
  //       List<double> landmarks = [];
  //       for (var item in result) {
  //         landmarks.add(item.toDouble());
  //       }

  //     return landmarks;
  //     }
  //     else{
  //       print("error");
  //       return [];
  //     }
  //   }on PlatformException catch(e) {
  //     print("[!] Error: $e");
  //     return [];
  //   }
    
  // } 
}



// -- before pod install -- 
// class SymbolClassifier {
//   late Interpreter _interpreter;
//   // final model_path = await rootBundle.load
  
//   // String model_path = 'assets/symbol_classifier.tflite'; 
//   SymbolClassifier({String modelPath = 'src/lsl_translator/model/symbol_classifier.tflite', int numThreads = 1}) {
//     _initializeInterpreter(modelPath, numThreads);
//   }

//   Future<void> _initializeInterpreter(String modelPath, int numThreads) async {
//     // final model_file = await File('assets/symbol_classifier.tflite');
//     final fileOnDevice = File('assets/symbol_classifier.tflite');
//     final rawModel = await rootBundle.load('assets/symbol_classifier.tflite'); 
//     final rawBytes = rawModel.buffer.asUint8List();
//     await fileOnDevice.writeAsBytes(rawBytes, flush: true);
//     _interpreter = Interpreter.fromFile(fileOnDevice);
//     _interpreter.allocateTensors();
//   }

//   List<dynamic> predictConfidence(List<double> landmarkList) {
//     // Prepare input tensor
//     var inputTensor = _interpreter.getInputTensors()[0];
//     inputTensor.data = convertListToUint8List(landmarkList);

//     // Run inference
//     _interpreter.invoke();

//     // Get output tensor
//     var outputTensor = _interpreter.getOutputTensors()[0];
//     var output = outputTensor.data.toList();

//     // Find the index of the maximum confidence value
//     int maxConfidence = output.reduce((value, element) => value > element ? value : element);
//     int predictedClass = output.indexOf(maxConfidence);

//     return [predictedClass, maxConfidence];
//   }

//   Uint8List _flattenAndConvertToUint8List(List<List<double>> landmarkList) {
//     var flattenedList = landmarkList.expand((list) => list).toList();
//     return Uint8List.fromList(flattenedList.map((e) => e.round()).toList());
//   }
//   Uint8List convertListToUint8List(List<double> list) {
//   var uint8List = Uint8List(list.length);
//   for (var i = 0; i < list.length; i++) {
//     var value = list[i].round();
//     value = value.clamp(0, 255); // Ensure the value is within the valid range for Uint8
//     uint8List[i] = value;
//   }
//   return uint8List;
// }


//   void close() {
//     _interpreter.close();
//   }
// }
class GestureClassifier {
  Future<List<int>> predictConfidence(List<double> landmarkList) async {
  
  // if (!_isInterpreterReady) {
    await Future.delayed(Duration(milliseconds: 100)); // Add a small delay for stability
    // return await predictConfidence(landmarkList); // Retry inference after delay
  // }
  
  try {


    final interpreter = await tfl.Interpreter.fromAsset('assets/symbol_classifier.tflite');

    var output = List.filled(2, 0.0).reshape([1, 2]);
    interpreter.run(landmarkList, output);
    var prediction = -1;
    var confidence = 0.0;

    for (var i = 0; i < output[0].length; i++) {
      if (output[0][i] > confidence) {
        confidence = output[0][i];
        prediction = i;
      }
    }
    // Return the output tensor
    return [prediction, (confidence*100).toInt()];
  } catch (e) {
    print('Error performing inference: $e');
    throw e;
  }
}
}
class SymbolClassifier {
  // late Interpreter _interpreter;
  // bool _isInterpreterReady = false;

  // SymbolClassifier({int numThreads = 1}) {
  //   _initializeInterpreter(numThreads);
  // }

  // Future<void> _initializeInterpreter(int numThreads) async {
  //   try {
  //     Directory tempDir = await getTemporaryDirectory();
  //     String tempPath = tempDir.path;
  //     String modelPath = '$tempPath/symbol_classifier.tflite';
  //     File modelFile = File(modelPath);
  //     if (!await modelFile.exists()) {
  //       ByteData modelData = await rootBundle.load('assets/symbol_classifier.tflite');
  //       Uint8List bytes = modelData.buffer.asUint8List();
  //       await modelFile.writeAsBytes(bytes, flush: true);
  //     }
  //     _interpreter = Interpreter.fromFile(modelFile);
  //     _interpreter.allocateTensors();
  //     _isInterpreterReady = true; // Set flag to indicate interpreter is ready
  //   } catch (e) {
  //     print('Error initializing interpreter: $e');
  //     throw e;
  //   }
  // }
// Future<List<dynamic>>
Future<List<int>> predictConfidence(List<double> landmarkList) async {
  
  // if (!_isInterpreterReady) {
    await Future.delayed(Duration(milliseconds: 100)); // Add a small delay for stability
    // return await predictConfidence(landmarkList); // Retry inference after delay
  // }
  // newly added
  try {
    if (landmarkList.length == 0) {
      return [-1, 0];
    }
    final interpreter = await tfl.Interpreter.fromAsset('assets/symbol_classifier.tflite');

    var output = List.filled(58, 0.0).reshape([1, 58]);
    interpreter.run(landmarkList, output);
    var prediction = -1;
    var confidence = 0.0;

    for (var i = 0; i < output[0].length; i++) {
      if (output[0][i] > confidence) {
        confidence = output[0][i];
        prediction = i;
      }
    }
    // Return the output tensor
    return [prediction, (confidence*100).toInt()];
  } catch (e) {
    print('Error performing inference: $e');
    throw e;
  }
}


Uint8List convertListToUint8List(List<List<double>> list) {
  var flattenedList = list.expand((subList) => subList).toList(); // Flatten the 2D list
  var uint8List = Uint8List.fromList(
      flattenedList.map<int>((double value) => (value * 255).round().clamp(0, 255)).toList());

  return uint8List;
}


  // Uint8List convertListToUint8List(List<List<double>> list) {
  //   var uint8List = Uint8List(list[0].length); // Create a 1D Uint8List with length 126
  //   for (var i = 0; i < list[0].length; i++) {
  //     var value = (list[0][i] * 255).round().clamp(0, 255); // Normalize and convert to uint8
  //     uint8List[i] = value;
  //   }
  //   return uint8List;
  // }
  // List<List<int>> convertListToUint8List(List<List<double>> list) {
  //   var uint8List = Uint8List.fromList(list[0].map((double value) => (value * 255).round().clamp(0, 255)).toList());
    
  //   // Create a 2D list with one row containing the uint8List
  //   return [uint8List];
  // }
  // void close() {
  //   _interpreter.close();
  // }
}


// class SymbolClassifier {
//   late Interpreter _interpreter;

//   SymbolClassifier({required String modelPath, int numThreads = 1}) {
//     _initializeInterpreter(modelPath, numThreads);
//   }

//   Future<void> _initializeInterpreter(String modelPath, int numThreads) async {
//     // Load the TFLite model file
//     ByteData modelData = await rootBundle.load(modelPath);
//     var modelBuffer = modelData.buffer;
//     var file = File('symbol_classifier.tflite');
//     await file.writeAsBytes(modelBuffer.asUint8List());

//     // Initialize the interpreter
//     _interpreter = Interpreter.fromFile(file);
//     _interpreter.allocateTensors();
//   }

//   List<dynamic> predictConfidence(List<double> landmarkList) {
//     // Prepare input tensor
//     var inputTensor = _interpreter.getInputTensors()[0];
//     inputTensor.data = convertListToUint8List(landmarkList);

//     // Run inference
//     _interpreter.invoke();

//     // Get output tensor
//     var outputTensor = _interpreter.getOutputTensors()[0];
//     var output = outputTensor.data.toList();

//     // Find the index of the maximum confidence value
//     int maxConfidence = output.reduce((value, element) => value > element ? value : element);
//     int predictedClass = output.indexOf(maxConfidence);

//     return [predictedClass, maxConfidence];
//   }

//   Uint8List convertListToUint8List(List<double> list) {
//     var uint8List = Uint8List(list.length);
//     for (var i = 0; i < list.length; i++) {
//       var value = list[i].round();
//       value = value.clamp(0, 255); // Ensure the value is within the valid range for Uint8
//       uint8List[i] = value;
//     }
//     return uint8List;
//   }

//   void close() {
//     _interpreter.close();
//   }
// }
