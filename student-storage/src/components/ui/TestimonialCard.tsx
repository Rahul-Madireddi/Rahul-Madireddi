import { Star } from 'lucide-react';
import type { Testimonial } from '../../types';

const avatarColors = [
  'bg-indigo-100 text-indigo-700',
  'bg-amber-100 text-amber-700',
  'bg-emerald-100 text-emerald-700',
  'bg-rose-100 text-rose-700',
];

interface TestimonialCardProps {
  testimonial: Testimonial;
  index: number;
}

export default function TestimonialCard({ testimonial, index }: TestimonialCardProps) {
  const colorClass = avatarColors[index % avatarColors.length];

  return (
    <div className="bg-white rounded-3xl p-8 border border-gray-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 flex flex-col gap-5">
      <div className="flex items-center gap-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <Star
            key={i}
            size={14}
            className={i < testimonial.rating ? 'fill-amber-400 text-amber-400' : 'text-gray-200'}
          />
        ))}
      </div>

      <p className="text-gray-700 text-sm leading-relaxed flex-1 italic">
        "{testimonial.quote}"
      </p>

      <div className="flex items-center gap-3">
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold text-sm ${colorClass}`}
        >
          {testimonial.initials}
        </div>
        <div>
          <p className="text-gray-900 font-semibold text-sm">{testimonial.name}</p>
          <p className="text-gray-400 text-xs">
            {testimonial.university} · {testimonial.year}
          </p>
        </div>
      </div>
    </div>
  );
}
