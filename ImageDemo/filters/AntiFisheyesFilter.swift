//
//  AntiFisheyesFilter.swift
//  VitaCameraLab
//
//  Created by Alan Chen on 2024/12/27.
//

import CoreImage


class AntiFisheyesFilter: CIFilter {
    var inputImage: CIImage?
    var inputFactor: Float = 0
    
    private let kernel: CIKernel = {
        do {
            let ciKernel = try CIKernel(functionName: "antiFishEye", fromMetalLibraryData: libData)
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
        }, arguments: [inputImage, CIVector(x: CGFloat(inputImage.extent.width / 2), y: CGFloat(inputImage.extent.height / 2)), inputFactor])
    }
}
