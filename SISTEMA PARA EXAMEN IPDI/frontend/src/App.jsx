import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import ImageUploader from './components/ImageUploader';
import ImageViewer from './components/ImageViewer';
import HistogramViewer from './components/HistogramViewer';
import BinarizationControls from './components/controls/BinarizationControls';
import MorphologyControls from './components/controls/MorphologyControls';
import ConvolutionControls from './components/controls/ConvolutionControls';
import LuminanceControls from './components/controls/LuminanceControls';
import ArithmeticControls from './components/controls/ArithmeticControls';
import ChromaticControls from './components/controls/ChromaticControls';

const API_URL = 'http://localhost:8000';

function App() {
    const [activeTab, setActiveTab] = useState('binarization');
    const [originalImage, setOriginalImage] = useState(null);
    const [originalImagePreview, setOriginalImagePreview] = useState(null);
    const [processedImagePreview, setProcessedImagePreview] = useState(null);
    const [histogramData, setHistogramData] = useState(null);
    const [isProcessing, setIsProcessing] = useState(false);
    const [error, setError] = useState(null);

    const [originalMetadata, setOriginalMetadata] = useState({ space: 'RGB', representation: 'RGB (3 canales)' });
    const [processedMetadata, setProcessedMetadata] = useState({ space: 'RGB', representation: 'RGB (3 canales)' });

    const handleUpload = (file) => {
        setOriginalImage(file);
        setOriginalImagePreview(URL.createObjectURL(file));
        setProcessedImagePreview(null);
        setHistogramData(null);
        setError(null);
        setOriginalMetadata({ space: 'RGB', representation: 'RGB (3 canales)' }); // Reset metadata
        setProcessedMetadata({ space: 'RGB', representation: 'RGB (3 canales)' });
        fetchHistogram(file);
    };

    const fetchHistogram = async (file) => {
        try {
            const formData = new FormData();
            formData.append('file', file);
            const res = await axios.post(`${API_URL}/process/histogram`, formData);
            setHistogramData(res.data);
        } catch (err) {
            console.error("Error fetching histogram", err);
        }
    };

    const handleProcess = async (endpoint, formData) => {
        if (!originalImage) {
            setError("Por favor cargue una imagen primero.");
            return;
        }

        setIsProcessing(true);
        setError(null);

        // Append the main file if not already present (Arithmetic handles its own file2)
        if (!formData.has('file')) {
            formData.append('file', originalImage);
        }

        try {
            const res = await axios.post(`${API_URL}/process/${endpoint}`, formData, {
                responseType: 'blob'
            });
            const url = URL.createObjectURL(res.data);
            setProcessedImagePreview(url);

            // Update metadata based on operation
            let newMeta = { ...originalMetadata };
            if (endpoint === 'binarize') {
                newMeta = { space: 'Binario', representation: '1 bit' };
            } else if (endpoint === 'chromatic') {
                const op = formData.get('operation');
                if (op === 'rgb_to_yiq') newMeta = { space: 'YIQ', representation: 'YIQ (3 canales)' };
                else if (op === 'yiq_to_rgb') newMeta = { space: 'RGB', representation: 'RGB (3 canales)' };
                else if (op === 'avg') newMeta = { space: 'Gris', representation: '1 canal' };
                else if (op === 'channel') newMeta = { space: 'Gris', representation: '1 canal (Extraído)' };
            } else if (endpoint === 'luminance' || endpoint === 'morphology' || endpoint === 'convolution') {
                // These usually result in grayscale or keep current space if applied on color
                // Our backend implementation often converts to gray for these.
                newMeta = { space: 'Gris', representation: '1 canal' };
            }
            setProcessedMetadata(newMeta);

            const processedFile = new File([res.data], "processed.png", { type: "image/png" });
            fetchHistogram(processedFile);

        } catch (err) {
            console.error("Processing error", err);
            setError("Ocurrió un error durante el procesamiento.");
        } finally {
            setIsProcessing(false);
        }
    };

    const handleResultToOriginal = async () => {
        if (!processedImagePreview) return;

        // Fetch the blob from the preview URL
        const response = await fetch(processedImagePreview);
        const blob = await response.blob();
        const file = new File([blob], "processed_as_original.png", { type: "image/png" });

        setOriginalImage(file);
        setOriginalImagePreview(processedImagePreview);
        setOriginalMetadata(processedMetadata); // Transfer metadata
        setProcessedImagePreview(null); // Clear result
        setHistogramData(null);
        fetchHistogram(file);
    };

    const handleDownload = (url, filename) => {
        if (!url) return;
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    const renderControls = () => {
        const props = { onProcess: handleProcess, isProcessing };

        switch (activeTab) {
            case 'binarization': return <BinarizationControls {...props} />;
            case 'morphology': return <MorphologyControls {...props} />;
            case 'convolution': return <ConvolutionControls {...props} />;
            case 'luminance': return <LuminanceControls {...props} />;
            case 'arithmetic': return <ArithmeticControls {...props} />;
            case 'chromatic': return <ChromaticControls {...props} />;
            case 'histogram': return (
                <div className="text-gray-400 text-sm">
                    El histograma se muestra abajo. Use "Ecualizar" para mejorar el contraste.
                    <button
                        onClick={() => handleProcess('equalize', new FormData())}
                        className="mt-4 w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg shadow-md transition-colors"
                    >
                        Ecualizar Histograma
                    </button>
                </div>
            );
            default: return null;
        }
    };

    return (
        <div className="flex h-screen bg-gray-950 text-gray-100 font-sans overflow-hidden">
            <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />

            <main className="flex-1 flex flex-col h-full overflow-hidden">
                <header className="h-16 bg-gray-900 border-b border-gray-800 flex items-center px-6 justify-between">
                    <h2 className="text-lg font-semibold text-gray-200 capitalize">{activeTab}</h2>
                    {error && <div className="text-red-400 text-sm">{error}</div>}
                </header>

                <div className="flex-1 flex overflow-hidden">
                    {/* Left Panel: Controls & Upload */}
                    <div className="w-80 bg-gray-900 border-r border-gray-800 p-6 overflow-y-auto flex flex-col gap-6">
                        <div className="flex-shrink-0">
                            <h3 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">Entrada</h3>
                            <ImageUploader onUpload={handleUpload} label={originalImage ? originalImage.name : "Cargar Imagen"} />
                        </div>

                        <div className="flex-1">
                            <h3 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">Controles</h3>
                            <div className="bg-gray-800 rounded-xl p-4 border border-gray-700">
                                {renderControls()}
                            </div>
                        </div>
                    </div>

                    {/* Center Panel: Image Viewers */}
                    <div className="flex-1 p-6 overflow-y-auto bg-gray-950 flex flex-col gap-6">
                        <div className="flex-1 flex items-center justify-center gap-4 min-h-[400px]">
                            {/* Original Image Area */}
                            <div className="flex-1 flex flex-col gap-2 h-full">
                                <ImageViewer src={originalImagePreview} title="Original" placeholder="Cargar imagen" />
                                <div className="flex justify-between items-start text-xs text-gray-400 px-1">
                                    <div>
                                        <div><span className="font-semibold text-gray-300">Espacio cromático:</span> {originalMetadata.space}</div>
                                        <div><span className="font-semibold text-gray-300">Representación:</span> {originalMetadata.representation}</div>
                                    </div>
                                    {originalImagePreview && (
                                        <div className="flex gap-3">
                                            <label className="cursor-pointer text-blue-400 hover:text-blue-300 underline text-xs">
                                                Cambiar imagen
                                                <input
                                                    type="file"
                                                    className="hidden"
                                                    accept="image/*"
                                                    onChange={(e) => {
                                                        if (e.target.files[0]) handleUpload(e.target.files[0]);
                                                    }}
                                                />
                                            </label>
                                            <button
                                                onClick={() => handleDownload(originalImagePreview, "original_image.png")}
                                                className="text-blue-400 hover:text-blue-300 underline"
                                            >
                                                Descargar imagen
                                            </button>
                                        </div>
                                    )}
                                </div>
                            </div>

                            {/* Action Button */}
                            <div className="flex flex-col items-center justify-center">
                                <button
                                    onClick={handleResultToOriginal}
                                    disabled={!processedImagePreview}
                                    className="p-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-full shadow-lg transition-all transform hover:scale-110"
                                    title="Usar Resultado como Original"
                                >
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <line x1="19" y1="12" x2="5" y2="12"></line>
                                        <polyline points="12 19 5 12 12 5"></polyline>
                                    </svg>
                                </button>
                                <span className="text-xs text-gray-500 mt-2">Resultado</span>
                            </div>

                            {/* Processed Image Area */}
                            <div className="flex-1 flex flex-col gap-2 h-full">
                                <ImageViewer src={processedImagePreview} title="Resultado" placeholder="Procesar imagen para ver resultado" />
                                <div className="flex justify-between items-start text-xs text-gray-400 px-1">
                                    <div>
                                        <div><span className="font-semibold text-gray-300">Espacio cromático:</span> {processedMetadata.space}</div>
                                        <div><span className="font-semibold text-gray-300">Representación:</span> {processedMetadata.representation}</div>
                                    </div>
                                    {processedImagePreview && (
                                        <button
                                            onClick={() => handleDownload(processedImagePreview, "processed_image.png")}
                                            className="text-blue-400 hover:text-blue-300 underline"
                                        >
                                            Descargar imagen
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className="h-64 flex-shrink-0">
                            <h3 className="text-sm font-medium text-gray-400 mb-3 uppercase tracking-wider">Análisis de Histograma</h3>
                            <HistogramViewer data={histogramData} />
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default App;
