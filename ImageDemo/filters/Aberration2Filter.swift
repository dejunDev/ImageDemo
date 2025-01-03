//
//  Aberration2Filter.swift
//  VitaCameraLab
//
//  Created by Alan Chen on 2024/12/27.
//

import CoreImage

class Aberration2Filter: CIFilter {
    var inputImage: CIImage?
    var inputDistortion: Float = 0
    var inputIterations: Float = 0
    var inputStrength: Float = 0
    var inputSeparation: Float = 0
    
    private let kernel: CIKernel = {
        do {
            let ciKernel = try CIKernel(functionName: "prism", fromMetalLibraryData: libData)
            
            return ciKernel
        }
        catch {
            print("error = \(error)")
        }
        
        fatalError("no kenel")
    }()
    
    override var outputImage: CIImage? {
        guard let inputImage = inputImage else { return nil }
        return kernel.apply(extent: inputImage.extent, roiCallback: {_, rect in
            return rect
        }, arguments: [inputImage, CIVector(x: CGFloat(inputImage.extent.width), y: CGFloat(inputImage.extent.height)), inputDistortion, inputIterations, inputStrength, inputSeparation])
    }
}
