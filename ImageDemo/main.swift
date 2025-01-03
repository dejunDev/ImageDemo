//
//  main.swift
//  ImageDemo
//
//  Created by coder on 2024/12/24.
//

import Foundation
import CoreImage
import Cocoa


//加载CIImage
func loadCIImage(name:String)->CIImage?{
    guard let ni = NSImage(contentsOf: currentFile(name: name))else{
        fatalError("文件读取失败")
    }
    //    guard let image = CIImage(contentsOf: currentFile(name: name)) else{
    //        print("解析图片失败")
    //       return nil
    //    }
    //    return image
    guard let imageData = ni.tiffRepresentation else { return nil }
    guard let bitmapImageRep = NSBitmapImageRep(data: imageData) else { return nil }
    return CIImage(bitmapImageRep: bitmapImageRep)
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

//应用反鱼眼
func applyAntiFisheyesFilter(image:CIImage,factor:Float)->CIImage?{
    let filter = AntiFisheyesFilter()
    filter.inputImage = image
    filter.inputFactor = factor
    return filter.outputImage
}

//应用镜头模糊
func applyLensBlur(image:CIImage,mask:CIImage,radius:CGFloat,brightness:CGFloat,angle:CGFloat) -> CIImage?{
    let filter = LensBlur()
    filter.inputImage = image
    filter.inputMask = mask
    filter.radius = radius
    filter.brightness = brightness
    filter.angle = angle
    return filter.outputImage
}


//应用Prisma
func applyPrisma(image:CIImage,inputDistortion:Float,inputStrength:Float,inputIterations:Float,inputSeparation:Float) -> CIImage?{
    let filter = Aberration2Filter()
    filter.inputImage = image
    filter.inputDistortion = inputDistortion
    filter.inputStrength = inputStrength
    filter.inputIterations = inputIterations
    filter.inputSeparation = inputSeparation
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
    let context = CIContext(options: [CIContextOption.workingColorSpace:NSNull()])
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

extension CIImage {
    func resizeImg(targetSize: CGSize) -> CIImage {
            let maskSize = extent.size
            let scaleX = targetSize.width / maskSize.width
            let scaleY = targetSize.height / maskSize.height

            let transform = CGAffineTransform(scaleX: scaleX, y: scaleY)
            return transformed(by: transform)
    }

}



guard let image = loadCIImage(name: "input.webp") else{
    print("加载图片失败")
    exit(0)
}



//guard let blurImage = applyGuassianBlur(image: image,radius: 2) else{
//    print("高斯处理失败")
//    exit(0)
//}
//saveImage(image: blurImage, fileName: "gas_swift.png")
//
//guard let hsaImage = applyHighlightShadowAdjust(image: image,highlightAmount:1.0,shadowAmount:0.4) else{
//    print("高光阴影处理失败")
//    exit(0)
//}

//guard let antiFisheyeImage = applyAntiFisheyesFilter(image: image, factor: -0.4) else{
//    fatalError("处理反鱼眼效果失败")
//}
//saveImage(image: antiFisheyeImage, fileName: "anti_fisheye.png")



guard let lensInput = loadCIImage(name: "lens_input.png") else{
    fatalError("加载蒙板图失败")
}
guard var lensMask = loadCIImage(name: "lens_mask.jpg") else{
    fatalError("加载蒙板图失败")
}

lensMask = lensMask.resizeImg(targetSize: CGSize(width: 2048, height: 2048))


//处理镜头模糊
guard let lensBlur = applyLensBlur(image: lensInput, mask: lensMask, radius: 10, brightness: 0.55 ,angle: 100 ) else{
    fatalError("处理镜头模糊失败")
}
saveImage(image: lensBlur, fileName: "lens_blur.png")




saveImage(image: image, fileName: "prisma_0.png")
guard let prismaImage = applyPrisma(image: image,inputDistortion: 0,inputStrength: 0,inputIterations: 1,inputSeparation: 0) else{
    fatalError("prismaImage Handle Failed")
}
saveImage(image: prismaImage, fileName: "prisma_1.png")
guard let prismaImage = applyPrisma(image: image,inputDistortion: 0,inputStrength: 1,inputIterations: 1,inputSeparation: 0) else{
    fatalError("prismaImage Handle Failed")
}
saveImage(image: prismaImage, fileName: "prisma_2.png")

guard let prismaImage = applyPrisma(image: image,inputDistortion: 0,inputStrength: 2,inputIterations: 1,inputSeparation: 0) else{
    fatalError("prismaImage Handle Failed")
}
saveImage(image: prismaImage, fileName: "prisma_3.png")

guard let prismaImage = applyPrisma(image: image,inputDistortion: 0,inputStrength: 3,inputIterations: 1,inputSeparation: 0) else{
    fatalError("prismaImage Handle Failed")
}
saveImage(image: prismaImage, fileName: "prisma_4.png")

guard let prismaImage = applyPrisma(image: image,inputDistortion: 0,inputStrength: 0,inputIterations: 1,inputSeparation: 1) else{
    fatalError("prismaImage Handle Failed")
}
saveImage(image: prismaImage, fileName: "prisma_5.png")






let img = loadCIImage(name: "68_CITemperatureAndTint_setInputImage.png")!
let filter = CIFilter(name: "CIAreaAverage")!
filter.setValue(img, forKey: kCIInputImageKey)
let extent = img.extent
filter.setValue(CIVector(x: extent.origin.x, y: extent.origin.y, z: extent.size.width, w: extent.size.height), forKey: kCIInputExtentKey)
   
// 获取滤镜的输出
guard let outputImage = filter.outputImage else {
    fatalError("输出")
}

// 创建 CIContext 来渲染 1x1 的输出图像
//let context = CIContext(options: [CIContextOption.workingColorSpace:NSNull()])
let context = CIContext(options: nil)
var bitmap = [UInt8](repeating: 0, count: 4) // RGBA 数组
// 创建标准 sRGB 颜色空间
guard let sRGBColorSpace = CGColorSpace(name: CGColorSpace.sRGB) else {
    fatalError("Faile created sRGB color space.")
}
// 渲染 1x1 像素的图像，并将结果存储到 bitmap 数组中
context.render(outputImage, toBitmap: &bitmap, rowBytes: 4, bounds: CGRect(x: 0, y: 0, width: 1, height: 1), format: .RGBA8, colorSpace: sRGBColorSpace)

// 将 RGBA 值转换为 UIColor
let red = CGFloat(bitmap[0])
let green = CGFloat(bitmap[1])
let blue = CGFloat(bitmap[2])
let alpha = CGFloat(bitmap[3])

// 打印平均颜色的 RGBA 值
print("Red: \(red), Green: \(green), Blue: \(blue), Alpha: \(alpha)")
