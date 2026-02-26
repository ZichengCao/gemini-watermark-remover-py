/**
 * Gemini Watermark Remover - Application Logic
 */

class WatermarkApp {
    constructor() {
        this.remover = new GeminiWatermarkRemover();
        this.originalImage = null;
        this.init();
    }

    init() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.settings = document.getElementById('settings');
        this.previewArea = document.getElementById('previewArea');
        this.processing = document.getElementById('processing');
        this.originalCanvas = document.getElementById('originalCanvas');
        this.resultCanvas = document.getElementById('resultCanvas');
        this.downloadBtn = document.getElementById('downloadBtn');
        this.resetBtn = document.getElementById('resetBtn');

        this.bindEvents();
    }

    bindEvents() {
        // Upload area click
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            this.handleFileSelect(e.target.files[0]);
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('image/')) {
                this.handleFileSelect(file);
            }
        });

        // Watermark mode change
        document.querySelectorAll('input[name="watermarkMode"]').forEach(radio => {
            radio.addEventListener('change', (e) => {
                this.toggleCustomInputs(e.target.value);
                if (this.originalImage) {
                    this.processImage();
                }
            });
        });

        // Custom input changes
        ['logoSize', 'marginRight', 'marginBottom'].forEach(id => {
            const input = document.getElementById(id);
            input.addEventListener('input', () => {
                if (this.originalImage) {
                    this.processImage();
                }
            });
        });

        // Download button
        this.downloadBtn.addEventListener('click', () => {
            this.downloadResult();
        });

        // Reset button
        this.resetBtn.addEventListener('click', () => {
            this.reset();
        });
    }

    handleFileSelect(file) {
        if (!file || !file.type.startsWith('image/')) {
            alert('请选择有效的图片文件（PNG, JPEG, WEBP）');
            return;
        }

        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                this.originalImage = img;
                this.displayOriginal(img);
                this.settings.style.display = 'block';
                this.processImage();
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }

    displayOriginal(img) {
        // Set canvas size to match image
        this.originalCanvas.width = img.width;
        this.originalCanvas.height = img.height;
        this.resultCanvas.width = img.width;
        this.resultCanvas.height = img.height;

        // Draw image on canvas
        const ctx = this.originalCanvas.getContext('2d');
        ctx.drawImage(img, 0, 0);

        // Limit display size with CSS
        const maxWidth = Math.min(400, window.innerWidth - 80);
        const scale = maxWidth / img.width;

        [this.originalCanvas, this.resultCanvas].forEach(canvas => {
            canvas.style.width = maxWidth + 'px';
            canvas.style.height = (img.height * scale) + 'px';
        });
    }

    toggleCustomInputs(mode) {
        const customInputs = document.getElementById('customInputs');
        if (mode === 'custom') {
            customInputs.classList.remove('hidden');
        } else {
            customInputs.classList.add('hidden');
        }
    }

    getWatermarkConfig() {
        const mode = document.querySelector('input[name="watermarkMode"]:checked').value;

        if (mode === 'custom') {
            return {
                logoSize: parseInt(document.getElementById('logoSize').value),
                marginRight: parseInt(document.getElementById('marginRight').value),
                marginBottom: parseInt(document.getElementById('marginBottom').value)
            };
        } else if (mode === 'large') {
            return {
                logoSize: 96,
                marginRight: 64,
                marginBottom: 64
            };
        } else {
            // small - also use as default
            return {
                logoSize: 48,
                marginRight: 32,
                marginBottom: 32
            };
        }
    }

    processImage() {
        if (!this.originalImage) return;

        // Show processing indicator
        this.processing.classList.add('active');
        this.previewArea.classList.remove('active');

        // Use setTimeout to allow UI to update
        setTimeout(() => {
            // Draw original image to result canvas
            const ctx = this.resultCanvas.getContext('2d');
            ctx.drawImage(this.originalImage, 0, 0);

            // Get watermark config
            const config = this.getWatermarkConfig();

            // Process image
            try {
                this.remover.processImage(this.resultCanvas, config);

                // Show result
                this.processing.classList.remove('active');
                this.previewArea.classList.add('active');
            } catch (error) {
                console.error('处理失败:', error);
                alert('处理图片时出错: ' + error.message);
                this.processing.classList.remove('active');
            }
        }, 50);
    }

    downloadResult() {
        const link = document.createElement('a');
        link.download = 'gemini_no_watermark.png';
        link.href = this.resultCanvas.toDataURL('image/png');
        link.click();
    }

    reset() {
        this.originalImage = null;
        this.fileInput.value = '';
        this.settings.style.display = 'none';
        this.previewArea.classList.remove('active');
        this.processing.classList.remove('active');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new WatermarkApp();
});
