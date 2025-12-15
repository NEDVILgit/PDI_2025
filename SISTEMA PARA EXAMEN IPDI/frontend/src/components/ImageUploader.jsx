import React, { useCallback } from 'react';
import { Upload } from 'lucide-react';

const ImageUploader = ({ onUpload, label = "Cargar Imagen" }) => {
    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            onUpload(file);
        }
    };

    return (
        <div className="w-full">
            <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-700 border-dashed rounded-lg cursor-pointer bg-gray-800 hover:bg-gray-700 transition-colors">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="w-10 h-10 mb-3 text-gray-400" />
                    <p className="mb-2 text-sm text-gray-400"><span className="font-semibold">Click para cargar</span> o arrastrar y soltar</p>
                    <p className="text-xs text-gray-500">PNG, JPG o BMP</p>
                </div>
                <input type="file" className="hidden" onChange={handleFileChange} accept="image/*" />
            </label>
            <div className="text-center mt-2 text-sm text-gray-400">{label}</div>
        </div>
    );
};

export default ImageUploader;
