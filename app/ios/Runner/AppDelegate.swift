import UIKit
import Flutter
import MediaPipeTasksVision

@UIApplicationMain
@objc class AppDelegate: FlutterAppDelegate {
    override func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

        let controller: FlutterViewController = window?.rootViewController as! FlutterViewController
        let channel = FlutterMethodChannel(name: "samples.flutter.dev/battery",
                                           binaryMessenger: controller.binaryMessenger)
        
        channel.setMethodCallHandler({
            [weak self] (call: FlutterMethodCall, result: @escaping FlutterResult) -> Void in
            guard call.method == "gen_key" else {
                result(FlutterMethodNotImplemented)
                return
            }
            
            guard let arguments = call.arguments as? [String: Any],
                  let imageData = arguments["image"] as? FlutterStandardTypedData,
                  let image = UIImage(data: imageData.data) else {
                result(FlutterError(code: "INVALID_ARGUMENT",
                                    message: "Invalid arguments or failed to convert FlutterStandardTypedData to UIImage",
                                    details: nil))
                return
            }
            
            self?.getMultiHandLandmarks(image, result: result)
        })

        // channel.setMethodCallHandler({ [weak self] (call: FlutterMethodCall, result: @escaping FlutterResult) -> Void in
        //     guard call.method == "gen_key_seq" else {
        //         result(FlutterMethodNotImplemented)
        //         return
        //     }
            
        //     guard let arguments = call.arguments as? [String: Any],
        //     let imageDataList = arguments["images"] as? String else {
        //     result(FlutterError(code: "INVALID_ARGUMENT",
        //                         message: "Invalid arguments or failed to retrieve image data list",
        //                         details: nil))
        //     return
        // }

        // var images = [UIImage]()
        
        // for imageData in imageDataList {
        //     if let imageDataBytes = imageData.data,
        //     let image = UIImage(data: Data(imageDataBytes)) {
        //         images.append(image)
        //     } else {
        //         result(FlutterError(code: "INVALID_ARGUMENT",
        //                             message: "Failed to convert FlutterStandardTypedData to UIImage",
        //                             details: nil))
        //         return
        //     }
        // }
            
        //     self?.getGestureLandmarks(UIimages: images, result: result)
        // })


        GeneratedPluginRegistrant.register(with: self)
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }
    
    private func getMultiHandLandmarks(_ image: UIImage, result: @escaping FlutterResult) {
        guard let mpImage = image.toMPImage() else {
            result(FlutterError(code: "CONVERSION_ERROR",
                                message: "Failed to convert UIImage to MPImage",
                                details: nil))
            return
        }
        
        
        if let multi_hand_landmarks = detectHandLandmarks(from: mpImage) {
            var multi_hand_landmarks_list : [Float] = []
            for hand_landmarks in multi_hand_landmarks {
                var preProcessedLandmarks = preProcessLandmarks(image:image, landmarks: hand_landmarks)
                var relative_landmarks = calcRelativeLandmarkList(landmarks: preProcessedLandmarks)
                for landmark in relative_landmarks {
                    multi_hand_landmarks_list.append(landmark)
                }
            }
            if (multi_hand_landmarks.count == 1) {
                for i in 1...63 {
                    multi_hand_landmarks_list.append(0.0)
                }
            }
            // let landmarkPoints = preProcessLandmarks(image: image, landmarks: mediapipe_landmarks)
            // let relative_landmarks = calcRelativeLandmarkList(landmarks: landmarkPoints)
            result(multi_hand_landmarks_list)
            // result(relative_landmarks)
            // result(landmarkPoints)
            // result(landmarks)
        } else {
            result(FlutterError(code: "PROCESSING_ERROR",
                                message: "Failed to process hand landmarks",
                                details: nil))
        }
    }
    
    private func detectHandLandmarks(from image: MPImage) -> [[[Float]]]? {
        let modelPath = Bundle.main.path(forResource: "hand_landmarker", ofType: "task")
        let options = HandLandmarkerOptions()
        options.baseOptions.modelAssetPath = modelPath!
        options.runningMode = .image
        options.minHandDetectionConfidence = 0.5
        options.minTrackingConfidence = 0.5
        options.numHands = 2
        
        guard let handLandmarker = try? HandLandmarker(options: options) else {
            print("Error creating hand landmark detector")
            return nil
        }
        
        do {
            let result = try handLandmarker.detect(image: image)
            // print(type(of: result.landmarks))
            // print(result.landmarks.compactMap)
            // print("Mediapipe Landmarks")

            // let landmarksCoordinates: [[Float]] = result.landmarks.flatMap { landmarksArray in
            //     return landmarksArray.map { landmark in
            //         // print(landmark.x, landmark.y, landmark.z)
            //         return [landmark.x, landmark.y, landmark.z]
            //     }
            // }
            var multi_hand_landmarks: [[[Float]]] = []
            for landmark_list in result.landmarks {
                var hand_landmarks: [[Float]] = []
                for landmark in landmark_list {
                    hand_landmarks.append([landmark.x, landmark.y, landmark.z])
                }
                multi_hand_landmarks.append(hand_landmarks)
            }

            return multi_hand_landmarks
            // return landmarksCoordinates
        } catch {
            print("Error detecting hand landmarks: \(error)")
            return nil
        }
    }

    func preProcessLandmarks(image: UIImage, landmarks: [[Float]]) -> [[Float]] {
        let imageWidth = Float(image.size.width)
        let imageHeight = Float(image.size.height)
        // print(imageWidth)
        // print(imageHeight)
        var landmarkPoints = [[Float]]()

        for landmark in landmarks {
            let landmarkX = Float(min(Float(landmark[0] * imageWidth), imageWidth - 1))
            let landmarkY = Float(min(Float(landmark[1] * imageHeight), imageHeight - 1))
            let landmarkZ = Float(landmark[2])
            landmarkPoints.append([landmarkX, landmarkY, landmarkZ])
        }
        // print("preprocessed:")
        // print(landmarkPoints)
        return landmarkPoints
    }

    func calcRelativeLandmarkList(landmarks: [[Float]]) -> [Float] {
        var landmarkPoints: [Float] = []
        var baseX: Float = 0
        var baseY: Float = 0
        var baseZ: Float = 0
        var index: Int = 0
        
        // Find the base landmark
        for landmark in landmarks {
            let landmarkX = landmark[0]
            let landmarkY = landmark[1]
            let landmarkZ = landmark[2]

            if index == 0 {
                baseX = landmarkX
                baseY = landmarkY
                baseZ = landmarkZ
            }
            
            // Subtract base landmark from each landmark
            let normalizedX = landmarkX - baseX
            let normalizedY = landmarkY - baseY
            let normalizedZ = landmarkZ - baseZ
            
            landmarkPoints.append(normalizedX)
            landmarkPoints.append(normalizedY)
            landmarkPoints.append(normalizedZ)
            
            index += 1
        }
        
        // Find the maximum absolute value
        // let maxAbsValue = landmarkPoints.max(by: { abs($0) < abs($1) }) ?? 1
        
        // print(landmarkPoints)
        
        // Normalize each value by dividing by the maximum absolute value
        // let normalizedLandmarks = landmarkPoints.map { $0 / maxAbsValue }

        var max: Float = 0.0

        for landmark in landmarkPoints {
            if (abs(landmark) > max) {
                max = abs(landmark)
            }
        }
        // print(max)
        var ret: [Float] = []
        for landmark in landmarkPoints {
            ret.append(landmark / max)
        }
        
        // print(ret)

        return ret
    }

    // private func getGestureLandmarks (UIimages: [UIImage], result: @escaping FlutterResult) {
    //     var images: [MPImage] = []

    //     for i in 0...9 {
    //         images.append((UIimages[i].toMPImage())!)
    //     }

    //     let modelPath = Bundle.main.path(forResource: "hand_landmarker", ofType: "task")
    //     let options = HandLandmarkerOptions()
    //     options.baseOptions.modelAssetPath = modelPath!
    //     options.runningMode = .video
    //     options.minHandDetectionConfidence = 0.5
    //     options.minTrackingConfidence = 0.5
    //     options.numHands = 1

    //     guard let handLandmarker = try? HandLandmarker(options: options) else {
    //         print("Error creating hand landmark detector")
    //         result(FlutterError(code: "PROCESSING_ERROR",
    //                             message: "Failed to process hand landmarks",
    //                             details: nil))
    //         return
    //     }
    //     var multi_hand_gesture_landmarks: [Float] = []
    //     var timestamp: Int = 0
    //     for image in images {

    //         do {

    //             let result = try handLandmarker.detect(videoFrame: image, timestampInMilliseconds: timestamp)
    //             for landmark_list in result.landmarks {
    //                 for landmark in landmark_list {
    //                     multi_hand_gesture_landmarks.append(landmark.x)
    //                     multi_hand_gesture_landmarks.append(landmark.y)
    //                     multi_hand_gesture_landmarks.append(landmark.z)
    //                 }
    //                 if (result.landmarks.count == 1) {
    //                     for i in 1...63 {
    //                         multi_hand_gesture_landmarks.append(0.0)
    //                     }
    //                 }
    //             }
    //             timestamp += 10 
                
    //         } catch {
    //             print("Error detecting hand landmarks: \(error)")
    //                         result(FlutterError(code: "PROCESSING_ERROR",
    //                             message: "Failed to process hand landmarks",
    //                             details: nil))
    //         }

    //     }
    //     result(multi_hand_gesture_landmarks)
    // }


}

extension UIImage {
    func toMPImage() -> MPImage? {
        do {
            return try MPImage(uiImage: self)
        } catch {
            print("Error converting UIImage to MPImage: \(error)")
            return nil
        }
    }
}
