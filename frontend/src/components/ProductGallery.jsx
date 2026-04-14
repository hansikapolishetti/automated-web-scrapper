import React, { useState, useRef, useCallback } from 'react';

const SWIPE_THRESHOLD = 40;

export default function ProductGallery({ images, title }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAnimating, setIsAnimating]   = useState(false);

  const dragStartX  = useRef(null);
  const isDragging  = useRef(false);
  const dragOffsetX = useRef(0);
  const imgWrapRef  = useRef(null);

  const goTo = useCallback((index) => {
    if (isAnimating) return;
    const next = (index + images.length) % images.length;
    if (next === currentIndex) return;
    setIsAnimating(true);
    setCurrentIndex(next);
    setTimeout(() => setIsAnimating(false), 320);
  }, [currentIndex, images.length, isAnimating]);

  const prev = () => goTo(currentIndex - 1);
  const next = () => goTo(currentIndex + 1);

  const onPointerDown = (e) => {
    dragStartX.current  = e.clientX;
    isDragging.current  = true;
    dragOffsetX.current = 0;
    if (imgWrapRef.current) imgWrapRef.current.style.transition = 'none';
  };
  const onPointerMove = (e) => {
    if (!isDragging.current || dragStartX.current === null) return;
    dragOffsetX.current = e.clientX - dragStartX.current;
    if (imgWrapRef.current) {
      const clamped = Math.max(-80, Math.min(80, dragOffsetX.current));
      imgWrapRef.current.style.transform = `translateX(${clamped}px)`;
    }
  };
  const onPointerUp = () => {
    if (!isDragging.current) return;
    isDragging.current = false;
    if (imgWrapRef.current) {
      imgWrapRef.current.style.transition = 'transform 0.25s ease';
      imgWrapRef.current.style.transform  = 'translateX(0)';
    }
    if (dragOffsetX.current < -SWIPE_THRESHOLD) next();
    else if (dragOffsetX.current > SWIPE_THRESHOLD) prev();
    dragStartX.current  = null;
    dragOffsetX.current = 0;
  };

  const onTouchStart = (e) => { dragStartX.current = e.touches[0].clientX; isDragging.current = true; dragOffsetX.current = 0; };
  const onTouchMove  = (e) => { e.preventDefault(); dragOffsetX.current = e.touches[0].clientX - dragStartX.current; };
  const onTouchEnd   = () => onPointerUp();

  const hasMultiple = images.length > 1;

  return (
    <div className="flex flex-col select-none">

      {/* ── Main Viewer ── */}
      <div
        className="relative rounded-2xl overflow-hidden group"
        style={{
          background: 'linear-gradient(145deg, #f8fafc 0%, #f1f5f9 60%, #e2e8f0 100%)',
          minHeight: '220px',
          maxHeight: '300px',
          boxShadow: '0 4px 24px 0 rgba(99,102,241,0.07), 0 1.5px 6px 0 rgba(0,0,0,0.06)',
          cursor: hasMultiple ? 'grab' : 'default',
        }}
        onMouseDown={hasMultiple ? onPointerDown : undefined}
        onMouseMove={hasMultiple ? onPointerMove : undefined}
        onMouseUp={hasMultiple ? onPointerUp : undefined}
        onMouseLeave={hasMultiple ? onPointerUp : undefined}
        onTouchStart={hasMultiple ? onTouchStart : undefined}
        onTouchMove={hasMultiple ? onTouchMove : undefined}
        onTouchEnd={hasMultiple ? onTouchEnd : undefined}
      >
        {/* Subtle inner glow ring */}
        <div className="absolute inset-0 rounded-2xl ring-1 ring-inset ring-slate-200/80 pointer-events-none z-10" />

        <div
          ref={imgWrapRef}
          className="h-full w-full flex items-center justify-center p-6"
          style={{ willChange: 'transform' }}
        >
          <img
            key={currentIndex}
            src={images[currentIndex]}
            alt={`${title} — view ${currentIndex + 1}`}
            draggable={false}
            className="max-h-[240px] w-full object-contain mix-blend-multiply pointer-events-none gallery-fade-in"
          />
        </div>

        {/* Arrows — fade in on hover */}
        {hasMultiple && (
          <>
            <button
              onClick={(e) => { e.stopPropagation(); prev(); }}
              aria-label="Previous image"
              className="absolute left-3 top-1/2 -translate-y-1/2 z-20
                         w-9 h-9 rounded-full bg-white/90 backdrop-blur-sm
                         border border-slate-200/80 shadow-lg
                         flex items-center justify-center
                         opacity-0 group-hover:opacity-100
                         hover:bg-white hover:scale-110 hover:shadow-xl
                         transition-all duration-200"
            >
              <svg className="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); next(); }}
              aria-label="Next image"
              className="absolute right-3 top-1/2 -translate-y-1/2 z-20
                         w-9 h-9 rounded-full bg-white/90 backdrop-blur-sm
                         border border-slate-200/80 shadow-lg
                         flex items-center justify-center
                         opacity-0 group-hover:opacity-100
                         hover:bg-white hover:scale-110 hover:shadow-xl
                         transition-all duration-200"
            >
              <svg className="w-4 h-4 text-slate-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
              </svg>
            </button>

            {/* Dot indicators */}
            <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-1.5 z-20">
              {images.map((_, i) => (
                <button
                  key={i}
                  onClick={(e) => { e.stopPropagation(); goTo(i); }}
                  className={`rounded-full transition-all duration-300 ${
                    i === currentIndex
                      ? 'w-5 h-1.5 bg-indigo-500 shadow-sm shadow-indigo-300'
                      : 'w-1.5 h-1.5 bg-slate-300 hover:bg-slate-500'
                  }`}
                />
              ))}
            </div>
          </>
        )}
      </div>

      {/* ── Thumbnails ── */}
      {hasMultiple && (
        <div className="flex gap-3 mt-4 justify-center overflow-x-auto pb-1 scrollbar-hide">
          {images.map((img, idx) => (
            <button
              key={idx}
              onClick={() => goTo(idx)}
              className={`relative w-16 h-16 flex-shrink-0 rounded-xl border-2 p-2
                          flex items-center justify-center overflow-hidden
                          transition-all duration-250 ${
                idx === currentIndex
                  ? 'border-indigo-500 shadow-md shadow-indigo-200 scale-105 bg-indigo-50/50'
                  : 'border-slate-200 bg-slate-50 opacity-55 hover:opacity-100 hover:border-slate-300 hover:scale-105 hover:shadow-md'
              }`}
            >
              {/* Active glow ring */}
              {idx === currentIndex && (
                <span className="absolute inset-0 rounded-xl ring-1 ring-indigo-400/50 pointer-events-none" />
              )}
              <img
                src={img}
                alt={`Thumbnail ${idx + 1}`}
                draggable={false}
                className="w-full h-full object-contain mix-blend-multiply"
              />
            </button>
          ))}
        </div>
      )}

      <style>{`
        @keyframes galleryFadeIn {
          from { opacity: 0; transform: scale(0.96); }
          to   { opacity: 1; transform: scale(1); }
        }
        .gallery-fade-in { animation: galleryFadeIn 0.28s cubic-bezier(.4,0,.2,1) forwards; }
      `}</style>
    </div>
  );
}
