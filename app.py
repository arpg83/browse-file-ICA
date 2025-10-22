from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import webbrowser
import threading
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB por archivo

# Crear carpeta de uploads si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB total

# HTML Template con subida múltiple
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Subir Múltiples Archivos</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #6666667d;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 700px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }
        
        h1 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
            font-size: 25px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: #f8f9ff;
            margin-bottom: 30px;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f0f2ff;
            transform: translateY(-2px);
        }
        
        .upload-area.dragover {
            border-color: #764ba2;
            background: #e8ebff;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 60px;
            margin-bottom: 15px;
        }
        
        .upload-text {
            color: #666;
            font-size: 16px;
        }
        
        .upload-text strong {
            color: #333;
            display: block;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        input[type="file"] {
            display: none;
        }
        
        .files-list {
            margin-bottom: 20px;
            max-height: 400px;
            overflow-y: none;
        }
        
        .file-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 15px;
            background: #f8f9ff;
            border-radius: 10px;
            margin-bottom: 10px;
            border: 2px solid #e0e7ff;
            transition: all 0.3s ease;
        }
        
        .file-item:hover {
            border-color: #667eea;
            transform: translateX(5px);
        }
        
        .file-item.uploading {
            background: #fff4e6;
            border-color: #ffa726;
        }
        
        .file-item.success {
            background: #e8f5e9;
            border-color: #4caf50;
        }
        
        .file-item.error {
            background: #ffebee;
            border-color: #f44336;
        }
        
        .file-info {
            flex: 1;
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .file-icon {
            font-size: 30px;
        }
        
        .file-details {
            flex: 1;
        }
        
        .file-name {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
            word-break: break-all;
        }
        
        .file-size {
            color: #666;
            font-size: 13px;
        }
        
        .file-status {
            font-size: 12px;
            padding: 4px 10px;
            border-radius: 20px;
            font-weight: bold;
        }
        
        .status-pending {
            background: #e3f2fd;
            color: #1976d2;
        }
        
        .status-uploading {
            background: #fff4e6;
            color: #f57c00;
        }
        
        .status-success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        
        .status-error {
            background: #ffebee;
            color: #c62828;
        }
        
        .remove-btn {
            background: #ff5252;
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 8px;
            font-weight: bold;
            transition: all 0.3s ease;
        }
        
        .remove-btn:hover {
            background: #ff1744;
            transform: scale(1.05);
        }
        
        .actions {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }
        
        .btn {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 10px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-upload {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        
        .btn-upload:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn-upload:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .btn-clear {
            background: #f44336;
            color: white;
        }
        
        .btn-clear:hover:not(:disabled) {
            background: #d32f2f;
            transform: translateY(-2px);
        }
        
        .btn-clear:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .summary {
            padding: 20px;
            background: #f0f2ff;
            border-radius: 10px;
            margin-bottom: 20px;
            display: none;
        }
        
        .summary.show {
            display: block;
        }
        
        .summary-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
            font-size: 16px;
        }
        
        .summary-stats {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .stat {
            flex: 1;
            min-width: 150px;
        }
        
        .stat-label {
            color: #666;
            font-size: 13px;
        }
        
        .stat-value {
            font-size: 18px;
            font-weight: bold;
            color: #667eea;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            margin-top: 15px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            width: 0%;
            transition: width 0.3s ease;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .uploading-animation {
            animation: pulse 1.5s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📤 Subir Múltiples Archivos</h1>
        <p class="subtitle">Arrastra archivos o haz clic para seleccionar</p>
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📁</div>
            <div class="upload-text">
                <strong>Selecciona múltiples archivos</strong>
                <p>Puedes arrastrar y soltar archivos aquí</p>
                <p style="font-size: 12px; margin-top: 5px; color: #999;">Máximo 50 MB por archivo</p>
            </div>
            <input type="file" id="fileInput" multiple>
        </div>
        
        <div class="summary" id="summary">
            <div class="summary-title">📊 Resumen</div>
            <div class="summary-stats">
                <div class="stat">
                    <div class="stat-label">Archivos seleccionados</div>
                    <div class="stat-value" id="totalFiles">0</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Tamaño total</div>
                    <div class="stat-value" id="totalSize">0 MB</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Estado</div>
                    <div class="stat-value" id="uploadStatus">Listo</div>
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
        </div>
        
        <div class="files-list" id="filesList"></div>
        
        <div class="actions">
            <button class="btn btn-upload" id="uploadBtn" disabled>
                📤 Subir Archivos (<span id="fileCount">0</span>)
            </button>
            <button class="btn btn-clear" id="clearBtn" disabled>
                🗑️ Limpiar Todo
            </button>
        </div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const filesList = document.getElementById('filesList');
        const uploadBtn = document.getElementById('uploadBtn');
        const clearBtn = document.getElementById('clearBtn');
        const summary = document.getElementById('summary');
        const totalFiles = document.getElementById('totalFiles');
        const totalSize = document.getElementById('totalSize');
        const uploadStatus = document.getElementById('uploadStatus');
        const fileCount = document.getElementById('fileCount');
        const progressFill = document.getElementById('progressFill');
        
        let selectedFiles = [];
        
        uploadArea.addEventListener('click', () => fileInput.click());
        
        fileInput.addEventListener('change', (e) => {
            handleFiles(Array.from(e.target.files));
        });
        
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            handleFiles(Array.from(e.dataTransfer.files));
        });
        
        function handleFiles(files) {
            files.forEach(file => {
                if (!selectedFiles.find(f => f.name === file.name && f.size === file.size)) {
                    selectedFiles.push({
                        file: file,
                        id: Date.now() + Math.random(),
                        status: 'pending'
                    });
                }
            });
            updateUI();
        }
        
        function updateUI() {
            filesList.innerHTML = '';
            
            selectedFiles.forEach((fileObj, index) => {
                const fileItem = document.createElement('div');
                fileItem.className = `file-item ${fileObj.status}`;
                fileItem.innerHTML = `
                    <div class="file-info">
                        <div class="file-icon">${getFileIcon(fileObj.file.name)}</div>
                        <div class="file-details">
                            <div class="file-name">${fileObj.file.name}</div>
                            <div class="file-size">${formatFileSize(fileObj.file.size)}</div>
                        </div>
                        <span class="file-status status-${fileObj.status}">
                            ${getStatusText(fileObj.status)}
                        </span>
                    </div>
                    <button class="remove-btn" onclick="removeFile(${index})" 
                            ${fileObj.status === 'uploading' ? 'disabled' : ''}>
                        ✕
                    </button>
                `;
                filesList.appendChild(fileItem);
            });
            
            const totalSizeBytes = selectedFiles.reduce((sum, f) => sum + f.file.size, 0);
            totalFiles.textContent = selectedFiles.length;
            totalSize.textContent = formatFileSize(totalSizeBytes);
            fileCount.textContent = selectedFiles.length;
            
            uploadBtn.disabled = selectedFiles.length === 0 || selectedFiles.some(f => f.status === 'uploading');
            clearBtn.disabled = selectedFiles.length === 0 || selectedFiles.some(f => f.status === 'uploading');
            summary.classList.toggle('show', selectedFiles.length > 0);
        }
        
        function getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            const icons = {
                'pdf': '📄',
                'doc': '📝', 'docx': '📝',
                'xls': '📊', 'xlsx': '📊',
                'ppt': '📽️', 'pptx': '📽️',
                'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️',
                'mp4': '🎥', 'avi': '🎥', 'mov': '🎥',
                'mp3': '🎵', 'wav': '🎵',
                'zip': '📦', 'rar': '📦',
                'txt': '📃',
                'html': '🌐', 'css': '🎨', 'js': '⚡',
                'py': '🐍', 'java': '☕'
            };
            return icons[ext] || '📄';
        }
        
        function getStatusText(status) {
            const texts = {
                'pending': '⏳ Pendiente',
                'uploading': '⬆️ Subiendo...',
                'success': '✅ Completado',
                'error': '❌ Error'
            };
            return texts[status] || status;
        }
        
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
        }
        
        function removeFile(index) {
            selectedFiles.splice(index, 1);
            updateUI();
        }
        
        clearBtn.addEventListener('click', () => {
            selectedFiles = [];
            fileInput.value = '';
            updateUI();
            progressFill.style.width = '0%';
            uploadStatus.textContent = 'Listo';
        });
        
        uploadBtn.addEventListener('click', async () => {
            let completed = 0;
            const total = selectedFiles.length;
            
            uploadStatus.textContent = '⬆️ Subiendo...';
            uploadStatus.classList.add('uploading-animation');
            
            for (let i = 0; i < selectedFiles.length; i++) {
                if (selectedFiles[i].status === 'success') {
                    completed++;
                    continue;
                }
                
                selectedFiles[i].status = 'uploading';
                updateUI();
                
                const formData = new FormData();
                formData.append('file', selectedFiles[i].file);
                
                try {
                    const response = await fetch('http://localhost:5000/upload_pdf', {
                        method: 'POST',
                        body: formData
                    });
                    if (response.status == 200) {
                        selectedFiles[i].status = 'success';
                        completed++;
                    } else {
                        selectedFiles[i].status = 'error';
                    }
                } catch (error) {
                    selectedFiles[i].status = 'error';
                }
                
                updateUI();
                progressFill.style.width = `${(completed / total) * 100}%`;
            }
            
            uploadStatus.classList.remove('uploading-animation');
            uploadBtn.disabled = true;
            
            const hasErrors = selectedFiles.some(f => f.status === 'error');
            if (hasErrors) {
                uploadStatus.textContent = '⚠️ Con errores';
            } else {
                uploadStatus.textContent = '✅ Completado';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Servir la página HTML principal"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint para subir un archivo"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró ningún archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Si el archivo existe, agregar timestamp
        base, extension = os.path.splitext(filename)
        counter = 1
        while os.path.exists(filepath):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{base}_{timestamp}_{counter}{extension}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            counter += 1
        
        file.save(filepath)
        file_size = os.path.getsize(filepath)
        
        return jsonify({
            'message': 'Archivo subido exitosamente',
            'filename': filename,
            'size': file_size,
            'path': filepath
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Error al guardar el archivo: {str(e)}'}), 500

@app.route('/files', methods=['GET'])
def list_files():
    """Endpoint para listar archivos subidos"""
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                files.append({
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'modified': os.path.getmtime(filepath)
                })
        return jsonify({'files': files, 'total': len(files)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({'error': 'Archivo demasiado grande. Máximo 50 MB por archivo'}), 413

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor Flask - Subida Múltiple de Archivos")
    print("=" * 60)
    print(f"📱 URL: http://localhost:8090")
    print(f"📁 Carpeta de uploads: {os.path.abspath(UPLOAD_FOLDER)}")
    print(f"📊 Límite por archivo: 50 MB")
    print(f"📦 Límite total: 100 MB")
    print("=" * 60)
    print("\n⏳ Abriendo navegador...\n")
    print("Presiona Ctrl+C para detener el servidor\n")
    
    app.run(debug=True, host='0.0.0.0', port=8090, use_reloader=False)