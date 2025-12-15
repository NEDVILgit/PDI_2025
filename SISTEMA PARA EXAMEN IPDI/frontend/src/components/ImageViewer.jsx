import React from 'react';

const ImageViewer = ({ src, title, placeholder = "Sin imagen para mostrar" }) => {
    const [showMagnifier, setShowMagnifier] = React.useState(false);
    const [cursorPosition, setCursorPosition] = React.useState({ x: 0, y: 0 });
    const imgRef = React.useRef(null);

    const handleMouseMove = (e) => {
        if (!imgRef.current) return;
        const { left, top, width, height } = imgRef.current.getBoundingClientRect();
        const x = e.clientX - left;
        const y = e.clientY - top;
        setCursorPosition({ x, y, imgWidth: width, imgHeight: height });
    };

    return (
        <div className="flex flex-col items-center w-full h-full">
            <div
                className="w-full h-full bg-gray-800 rounded-lg overflow-hidden flex items-center justify-center border border-gray-700 relative group"
                onMouseEnter={() => setShowMagnifier(true)}
                onMouseLeave={() => setShowMagnifier(false)}
                onMouseMove={handleMouseMove}
            >
                {src ? (
                    <>
                        <img
                            ref={imgRef}
                            src={src}
                            alt={title}
                            className="max-w-full max-h-full object-contain cursor-crosshair"
                        />
                        {showMagnifier && src && (
                            <div
                                style={{
                                    position: 'absolute',
                                    left: cursorPosition.x + 20, // Offset from cursor
                                    top: cursorPosition.y - 100,
                                    pointerEvents: 'none',
                                    width: '200px',
                                    height: '200px',
                                    border: '2px solid #fff',
                                    borderRadius: '50%',
                                    backgroundColor: 'black',
                                    backgroundImage: `url(${src})`,
                                    backgroundRepeat: 'no-repeat',
                                    // Calculate background position to match cursor
                                    // We need the ratio of natural size vs displayed size if possible, 
                                    // but object-contain makes it tricky to map exactly 1:1 if we don't know natural size.
                                    // However, simpler approach: use backgroundSize to scale up.
                                    // Let's assume 2x zoom.
                                    backgroundSize: `${cursorPosition.imgWidth * 2}px ${cursorPosition.imgHeight * 2}px`,
                                    backgroundPositionX: `${-cursorPosition.x * 2 + 100}px`,
                                    backgroundPositionY: `${-cursorPosition.y * 2 + 100}px`,
                                    zIndex: 50,
                                    boxShadow: '0 0 10px rgba(0,0,0,0.5)'
                                }}
                            />
                        )}
                    </>
                ) : (
                    <div className="text-gray-500 text-sm">{placeholder}</div>
                )}
            </div>
            {title && <div className="mt-2 text-sm font-medium text-gray-300">{title}</div>}
        </div>
    );
};

export default ImageViewer;
