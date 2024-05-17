// import Foundation
// import MediaPipeTasksVision
// import UIKit
// import Flutter

// func detectHandLandmarks(from image: UIImage) -> [NormalizedLandmark]? {
//     // Convert UIImage to MediaPipe's MPImage
//     guard let mpImage = image.toMPImage() else {
//         print("Error converting UIImage to MPImage")
//         return nil
//     }
    
//     // Create a hand landmark detector
//     let options = HandLandmarkerOptions()
//     options.runningMode = .image
//     options.minHandDetectionConfidence = 0.5
//     options.minTrackingConfidence = 0.5
//     options.numHands = 2
//     guard let handLandmarker = try? HandLandmarker(options: options) else {
//         print("Error creating hand landmark detector")
//         return nil
//     }
    
//     // Perform hand landmark detection
//     do {
//         let result = try handLandmarker.detect(image: mpImage)
//         return result.landmarks[0]
//     } catch {
//         print("Error detecting hand landmarks: \(error)")
//         return nil
//     }
// }

// // Helper extension to convert UIImage to MPImage
// extension UIImage {
//     func toMPImage() -> MPImage? {
//         do {
//             return try MPImage(uiImage: self)
//         } catch {
//             print("Error converting UIImage to MPImage: \(error)")
//             return nil
//         }
//     }
// }

// // func testHandLandmarkDetection(UIimage: testImage) {
// //     // Load test image (replace "test_image.jpg" with your image filename)
// //     // let testImage = UIImage(named: "test_image.jpg")
// //     // let testImage = UIImage(named: "test_image.jpg")
// //     // Check if test image is not nil
// //     guard let image = testImage else {
// //         print("Test image not found.")
// //         return
// //     }

// //     // Convert test image to MPImage
// //     guard let mpImage = image.toMPImage() else {
// //         print("Error converting test image to MPImage.")
// //         return
// //     }

// //     // Detect hand landmarks
// //     if let handLandmarks = detectHandLandmarks(from: image) {
// //         // Hand landmarks detected
// //         print("Hand landmarks detected:")
// //         for landmark in handLandmarks {
// //             print(landmark)
// //         }
// //     } else {
// //         // Error occurred during detection
// //         print("Error detecting hand landmarks.")
// //     }
// // }
// import UIKit
// import Flutter

// public class SwiftHandLandmarkPlugin: NSObject, FlutterPlugin {
//   public static func register(with registrar: FlutterPluginRegistrar) {
//     let channel = FlutterMethodChannel(name: "hand_landmark_detector", binaryMessenger: registrar.messenger())
//     let instance = SwiftHandLandmarkPlugin()
//     registrar.addMethodCallDelegate(instance, channel: channel)
//   }

//   public func handle(_ call: FlutterMethodCall, result: @escaping FlutterResult) {
//     if call.method == "detectHandLandmarks" {
//       guard let args = call.arguments as? [String: Any],
//             let imageData = args["imageData"] as? FlutterStandardTypedData,
//             let image = UIImage(data: imageData.data) else {
//         result(nil)
//         return
//       }

//       if let landmarks = detectHandLandmarks(from: image) {
//         result(landmarks.map { ["x": $0.x, "y": $0.y] })
//       } else {
//         result(nil)
//       }
//     } else {
//       result(FlutterMethodNotImplemented)
//     }
//   }

//   func detectHandLandmarks(from image: UIImage) -> [NormalizedLandmark]? {
//     // Your existing detection logic here...
//     print("Hello")
//   }
// }

// import UIKit
// import Flutter

// @UIApplicationMain
// @objc class AppDelegate: FlutterAppDelegate {
//     override func application(
//         _ application: UIApplication,
//         didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
//     ) -> Bool {
//         let controller = window.rootViewController as! FlutterViewController
//         let channel = FlutterMethodChannel(name: "hello_world_channel", binaryMessenger: controller.binaryMessenger)
//         channel.setMethodCallHandler({
//             (call: FlutterMethodCall, result: @escaping FlutterResult) -> Void in
//             if call.method == "getHelloWorld" {
//                 print("Test")
//                 result("Hello, world!")
//             } else {
//                 result(FlutterMethodNotImplemented)
//             }
//         })
//         return super.application(application, didFinishLaunchingWithOptions: launchOptions)
//     }
// }


@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

    let controller : FlutterViewController = window?.rootViewController as! FlutterViewController
    let batteryChannel = FlutterMethodChannel(name: "samples.flutter.dev/battery",
                                              binaryMessenger: controller.binaryMessenger)
    batteryChannel.setMethodCallHandler({
      (call: FlutterMethodCall, result: @escaping FlutterResult) -> Void in
      // This method is invoked on the UI thread.
      // Handle battery messages.
    })

    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }
}

private func receiveBatteryLevel(result: FlutterResult) {
  let device = UIDevice.current
  device.isBatteryMonitoringEnabled = true
  if device.batteryState == UIDevice.BatteryState.unknown {
    result(FlutterError(code: "UNAVAILABLE",
                        message: "Battery level not available.",
                        details: nil))
  } else {
    result(Int(device.batteryLevel * 100))
  }
}

batteryChannel.setMethodCallHandler({
  [weak self] (call: FlutterMethodCall, result: FlutterResult) -> Void in
  // This method is invoked on the UI thread.
  guard call.method == "getBatteryLevel" else {
    result(FlutterMethodNotImplemented)
    return
  }
  self?.receiveBatteryLevel(result: result)
})