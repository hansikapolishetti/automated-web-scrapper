import React, { useState } from 'react';

export default function ProductGallery({ images, title }) {
  const [mainImage, setMainImage] = useState(images[0]);

  return (
    <div className="flex flex-col">
      <div className="max-w-[420px] mx-auto group">
        <img 
          src={mainImage} 
          alt={title} 
          className="w-full max-h-[420px] object-contain drop-shadow-lg transition-transform duration-500 group-hover:scale-105"
        />
      </div>
      {images.length > 1 && (
        <div className="flex gap-3 mt-4 justify-center overflow-x-auto pb-2 scrollbar-hide">
          {images.map((img, idx) => (
            <button 
              key={idx}
              onClick={() => setMainImage(img)}
              className={`w-14 h-14 flex-shrink-0 bg-slate-50 rounded-md border-2 p-1.5 flex items-center justify-center cursor-pointer transition-all ${
                mainImage === img ? 'border-indigo-600 shadow-md scale-105' : 'border-slate-100 opacity-60 hover:opacity-100'
              }`}
            >
              <img src={img} alt={`Thumbnail ${idx}`} className="w-full h-full object-contain mix-blend-multiply" />
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
