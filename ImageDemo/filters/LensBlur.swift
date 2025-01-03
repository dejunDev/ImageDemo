//
//  LensBlur.swift
//  VitaCameraLab
//
//  Created by Alan Chen on 2024/12/27.
//

import CoreImage

class LensBlur: CIFilter {
    var inputImage: CIImage?
    var inputMask: CIImage?
    var radius: CGFloat = 0
    var brightness: CGFloat = 0
    var angle: CGFloat = 0
    
    private let preKernel: CIKernel = {
        do {
            let ciKernel = try CIKernel(functionName: "hexagonalBokehBlurPre", fromMetalLibraryData: libData)
            return ciKernel
        }
        catch {
            print("error = \(error)")
        }
        
        fatalError("no kenel")
    }()
    
    private let alphaVerticalKernel: CIKernel = {
        do {
            let ciKernel = try CIKernel(functionName: "hexagonalBokehBlurAlphaVertical", fromMetalLibraryData: libData)
            return ciKernel
        }
        catch {
            print("error = \(error)")
        }
        
        fatalError("no kenel")
    }()
    
    private let alphaDiagonalKernel: CIKernel = {
        do {
            let ciKernel = try CIKernel(functionName: "hexagonalBokehBlurAlphaDiagonal", fromMetalLibraryData: libData)
            return ciKernel
        }
        catch {
            print("error = \(error)")
        }
        
        fatalError("no kenel")
    }()
    
    private let bravoCharlieKernel: CIKernel = {
        do {
            let ciKernel = try CIKernel(functionName: "hexagonalBokehBlurBravoCharlie", fromMetalLibraryData: libData)
            return ciKernel
        }
        catch {
            print("error = \(error)")
        }
        
        fatalError("no kenel")
    }()
    
    override var outputImage: CIImage? {
        guard let inputImage else { return nil }
        guard radius > 0 else { return inputImage }
        guard let inputMask else { return nil }
        
        var deltas: [CIVector] = []
        for i in 0..<3 {
            let a: CGFloat = angle + CGFloat(i) * CGFloat.pi * 2 / 3
            let delta: CIVector = CIVector(x: radius * sin(a) / inputImage.extent.width, y: radius * cos(a) / inputImage.extent.height)
            deltas.append(delta)
        }
        
        let power: CGFloat = pow(CGFloat(10), min(max(brightness, -1), 1))
        
        let usesOneMinusMaskValue = false // mask.mode == MTIMaskModeOneMinusMaskValue;
        print("lens blur pre [\(power), \(0), \(true)]")
        guard let preOutputImg = preKernel.apply(extent: inputImage.extent, roiCallback: {_, rect in
            return rect
        }, arguments: [inputImage, inputMask, power, 0, 1]) else { usesOneMinusMaskValue // maskComponent == 0? @"maskComponent": @((int)mask.component?
            return inputImage
        }


        guard let alphaVerticalOutputImg = alphaVerticalKernel.apply(extent: preOutputImg.extent, roiCallback: {_, rect in
            return rect
        }, arguments: [preOutputImg, deltas[0], deltas[1]]) else {
            return inputImage
        }
  
        guard let alphaDiagonalOutputImg = alphaDiagonalKernel.apply(extent: preOutputImg.extent, roiCallback: {_, rect in
            return rect
        }, arguments: [preOutputImg, deltas[0], deltas[1]]) else {
            return inputImage
        }

        let outputImg = bravoCharlieKernel.apply(extent: alphaVerticalOutputImg.extent, roiCallback: {_, rect in
            return rect
        }, arguments: [alphaVerticalOutputImg, alphaDiagonalOutputImg, deltas[1], deltas[2], 1 / power])
        return outputImg
    }
}

