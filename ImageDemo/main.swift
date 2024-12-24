//
//  main.swift
//  ImageDemo
//
//  Created by coder on 2024/12/24.
//

import Foundation
import CoreImage



//加载CIImage
func loadCIImage(name:String)->CIImage?{
    guard let image = CIImage(contentsOf: currentFile(name: name)) else{
        print("解析图片失败")
       return nil
    }
    return image
}

func loadCIImageInPath(from path:String)->CIImage?{
    guard let image = CIImage(contentsOf: URL(fileURLWithPath: path)) else{
        print("解析图片失败")
       return nil
    }
    return image
}


//应用高斯模糊
func applyGuassianBlur(image:CIImage,radius:Float)->CIImage?{
    guard let filter = CIFilter(name: "CIGaussianBlur") else {
        return nil
    }
    filter.setValue(image, forKey: kCIInputImageKey)
    filter.setValue(radius, forKey: kCIInputRadiusKey)
    return filter.outputImage
}

//应用高光滤镜
func applyHighlightShadowAdjust(image:CIImage,highlightAmount:Float,shadowAmount:Float)->CIImage?{
    guard let filter = CIFilter(name: "CIHighlightShadowAdjust") else { return nil }
    filter.setValue(image, forKey: kCIInputImageKey)
    filter.setValue(highlightAmount, forKey: "inputHighlightAmount")
    filter.setValue(shadowAmount, forKey: "inputShadowAmount")
    return filter.outputImage
}

func currentFile(name:String)->URL{
    let filePath = #file
    let srcUrl = URL(fileURLWithPath: filePath)
    // 获取同级目录 (Swift文件的父目录)
    let directoryURL = srcUrl.deletingLastPathComponent()
    return  directoryURL.appendingPathComponent(name)
}


//保存图像
func saveImage(image:CIImage,fileName:String){
    let fileURL = currentFile(name:fileName)
    guard let colorSpace = CGColorSpace(name: CGColorSpace.sRGB) else{
        print("颜色空间初始错误")
        return
    }
    let context = CIContext(options: [CIContextOption.workingColorSpace:colorSpace])
    if(fileName.hasSuffix(".png")){
        try? context.writePNGRepresentation(of: image, to: fileURL, format:.ARGB8, colorSpace: colorSpace)
    }else if(fileName.hasSuffix(".jpg")){
        try? context.writeJPEGRepresentation(of: image, to: fileURL, colorSpace: colorSpace)
    }else if(fileName.hasSuffix(".tiff")){
        try? context.writeTIFFRepresentation(of: image, to: fileURL, format: .ARGB8, colorSpace: colorSpace)
    }else{
        print("不支持的格式")
    }
    
}




guard let image = loadCIImage(name: "input.webp") else{
    print("加载图片失败")
    exit(0)
}

guard let blurImage = applyGuassianBlur(image: image,radius: 2) else{
    print("高斯处理失败")
    exit(0)
}
saveImage(image: blurImage, fileName: "gas_swift.png")

guard let hsaImage = applyHighlightShadowAdjust(image: image,highlightAmount:1.0,shadowAmount:0.4) else{
    print("高光阴影处理失败")
    exit(0)
}
saveImage(image: hsaImage, fileName: "hsa_swift.png")

