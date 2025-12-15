import React from 'react';
import { Layers, Sun, Activity, Image, BarChart2, Palette, Calculator } from 'lucide-react';

const tabs = [
    { id: 'binarization', label: 'Binarización', icon: Layers },
    { id: 'morphology', label: 'Morfología', icon: Image },
    { id: 'convolution', label: 'Convolución', icon: Activity },
    { id: 'luminance', label: 'Luminancia', icon: Sun },
    { id: 'arithmetic', label: 'Aritmética', icon: Calculator },
    { id: 'chromatic', label: 'Espacio Cromático', icon: Palette },
    { id: 'histogram', label: 'Histograma', icon: BarChart2 },
];

const Sidebar = ({ activeTab, onTabChange }) => {
    return (
        <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col h-full">
            <div className="p-6">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    Sistema IPDI
                </h1>
                <p className="text-xs text-gray-500 mt-1">Procesamiento de Imágenes</p>
            </div>
            <nav className="flex-1 px-4 space-y-2">
                {tabs.map((tab) => {
                    const Icon = tab.icon;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => onTabChange(tab.id)}
                            className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg transition-all duration-200 ${activeTab === tab.id
                                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/50'
                                    : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                                }`}
                        >
                            <Icon size={20} />
                            <span className="font-medium">{tab.label}</span>
                        </button>
                    );
                })}
            </nav>
            <div className="p-4 border-t border-gray-800">
                <div className="text-xs text-gray-600 text-center">
                    v1.0.0 • Dockerizado
                </div>
            </div>
        </div>
    );
};

export default Sidebar;
