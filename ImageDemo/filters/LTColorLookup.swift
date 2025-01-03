//
//  LTColorLookup.swift
//  VitaCameraLab
//
//  Created by Alan Chen on 2024/12/27.
//

import CoreImage

class LTColorLookup: CIFilter {
    var inputImage: CIImage?
    var inputColorLookupTable: CIImage?
    var inputIntensity: Float = 1
    
    private let kernel: CIKernel = {
        do {
            let ciKernel = try CIKernel(functionName: "lookup", fromMetalLibraryData: libData)
            return ciKernel
        }
        catch {
            print("error = \(error)")
        }
        
        fatalError("no kenel")
    }()
    
    override var outputImage: CIImage? {
        guard let inputImage else { return nil }
        guard let inputColorLookupTable else { return nil }
        
        let outputImg = kernel.apply(extent: inputImage.extent, roiCallback: {_, rect in
            return rect
        }, arguments: [inputImage, inputColorLookupTable, inputIntensity])
        
        return outputImg
    }
}

