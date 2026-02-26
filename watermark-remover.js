/**
 * Gemini Watermark Remover - Core Algorithm
 *
 * 实现原理：
 * 1. Gemini 生成的图片水印是通过 alpha blending 叠加在右下角的
 * 2. 水印公式: watermarked = original * (1 - alpha) + watermark * alpha
 * 3. 已知 watermark 为白色 (255, 255, 255)，可通过逆向公式恢复原始图像:
 *    original = (watermarked - alpha * 255) / (1 - alpha)
 * 4. alpha 值从预计算的 alpha map 中获取
 */

class GeminiWatermarkRemover {
    constructor() {
        // Alpha maps for different watermark sizes (48px and 96px)
        // These are pre-calculated from the background images
        this.alphaMaps = this.loadAlphaMaps();
    }

    /**
     * Load pre-calculated alpha maps
     * Alpha 值取 RGB 通道的最大值，归一化到 [0, 1]
     * Uses pre-extracted data from alpha_maps.js
     */
    loadAlphaMaps() {
        // Use pre-calculated alpha maps extracted from background images
        return {
            48: new Float32Array(ALPHA_48),
            96: new Float32Array(ALPHA_96)
        };
    }

    /**
     * Detect watermark configuration based on image size
     */
    detectWatermarkConfig(imageWidth, imageHeight, customConfig) {
        if (customConfig) {
            return customConfig;
        }

        // Large images get large watermark
        if (imageWidth > 1024 && imageHeight > 1024) {
            return { logoSize: 96, marginRight: 64, marginBottom: 64 };
        } else {
            return { logoSize: 48, marginRight: 32, marginBottom: 32 };
        }
    }

    /**
     * Calculate watermark position
     */
    calculateWatermarkPosition(imageWidth, imageHeight, config) {
        return {
            x: imageWidth - config.marginRight - config.logoSize,
            y: imageHeight - config.marginBottom - config.logoSize,
            width: config.logoSize,
            height: config.logoSize
        };
    }

    /**
     * Remove watermark from image data
     */
    removeWatermark(imageData, position, logoSize) {
        const data = imageData.data;
        const width = imageData.width;
        const height = imageData.height;

        // Get alpha map for the logo size
        let alphaMap;
        if (logoSize === 96) {
            alphaMap = this.alphaMaps[96];
        } else {
            alphaMap = this.alphaMaps[48];
        }

        const ALPHA_THRESHOLD = 0.002;
        const MAX_ALPHA = 0.99;
        const LOGO_VALUE = 255;

        const { x, y } = position;

        // Process each pixel in the watermark region
        for (let row = 0; row < logoSize; row++) {
            for (let col = 0; col < logoSize; col++) {
                const alphaIdx = row * logoSize + col;
                const alpha = alphaMap[alphaIdx];

                // Skip pixels with very low alpha (basically no watermark)
                if (alpha < ALPHA_THRESHOLD) {
                    continue;
                }

                // Limit alpha to avoid division by zero
                const clampedAlpha = Math.min(alpha, MAX_ALPHA);
                const oneMinusAlpha = 1.0 - clampedAlpha;

                // Process each color channel
                for (let c = 0; c < 3; c++) {
                    const pixelIdx = ((y + row) * width + (x + col)) * 4 + c;
                    const watermarked = data[pixelIdx];

                    // Apply reverse formula: original = (watermarked - alpha * 255) / (1 - alpha)
                    const original = (watermarked - clampedAlpha * LOGO_VALUE) / oneMinusAlpha;

                    // Clip to [0, 255]
                    data[pixelIdx] = Math.max(0, Math.min(255, original));
                }
            }
        }

        return imageData;
    }

    /**
     * Process an image and remove watermark
     */
    processImage(canvas, config) {
        const ctx = canvas.getContext('2d');
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

        // Get watermark configuration
        const wmConfig = this.detectWatermarkConfig(
            canvas.width,
            canvas.height,
            config
        );

        // Calculate watermark position
        const position = this.calculateWatermarkPosition(
            canvas.width,
            canvas.height,
            wmConfig
        );

        console.log('Removing watermark:', wmConfig, 'at', position);

        // Remove watermark
        const result = this.removeWatermark(imageData, position, wmConfig.logoSize);

        // Put the processed image data back
        ctx.putImageData(result, 0, 0);

        return canvas;
    }
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = GeminiWatermarkRemover;
}
