import { Link } from 'react-router-dom';
import { Shield, Truck, Users } from 'lucide-react';

const badges = [
  { icon: Truck, label: 'Free Pickup & Delivery' },
  { icon: Shield, label: 'Fully Insured' },
  { icon: Users, label: '5,000+ Students Served' },
];

export default function Hero() {
  return (
    <section className="relative overflow-hidden bg-white pt-32 pb-24">
      {/* Subtle gradient background */}
      <div className="absolute inset-0 bg-gradient-to-b from-indigo-50/60 via-white to-white pointer-events-none" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-indigo-100/40 rounded-full blur-3xl pointer-events-none" />

      <div className="relative max-w-4xl mx-auto px-6 text-center">
        {/* Pill badge */}
        <div className="inline-flex items-center gap-2 bg-indigo-50 text-indigo-700 text-xs font-semibold px-4 py-2 rounded-full mb-8 border border-indigo-100">
          <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-pulse" />
          Now serving Illinois students
        </div>

        <h1 className="text-5xl sm:text-6xl md:text-7xl font-bold text-gray-950 tracking-tight leading-none mb-6">
          Store Smart.{' '}
          <span className="text-indigo-600">Study Hard.</span>
          <br />
          Come Back Ready.
        </h1>

        <p className="text-lg sm:text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
          We pick up your belongings at semester end, store them safely over break, and deliver
          everything back when you return. No trucks, no stress, no problem.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
          <Link
            to="/book"
            className="bg-indigo-600 text-white font-semibold px-8 py-4 rounded-full hover:bg-indigo-700 transition-all duration-200 hover:shadow-lg hover:shadow-indigo-200 hover:-translate-y-0.5 text-base"
          >
            Book Your Storage
          </Link>
          <Link
            to="/services"
            className="text-gray-700 font-semibold px-8 py-4 rounded-full border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 text-base"
          >
            View Pricing →
          </Link>
        </div>

        {/* Trust badges */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 sm:gap-10">
          {badges.map(({ icon: Icon, label }) => (
            <div key={label} className="flex items-center gap-2 text-gray-500 text-sm">
              <Icon size={16} className="text-indigo-500" />
              {label}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
