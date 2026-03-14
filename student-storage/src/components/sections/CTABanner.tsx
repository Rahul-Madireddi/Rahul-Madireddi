import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

export default function CTABanner() {
  return (
    <section className="py-24 bg-white">
      <div className="max-w-4xl mx-auto px-6">
        <div className="bg-indigo-600 rounded-3xl px-10 py-16 text-center relative overflow-hidden">
          {/* Decorative blobs */}
          <div className="absolute -top-16 -left-16 w-64 h-64 bg-indigo-500 rounded-full opacity-50 blur-3xl" />
          <div className="absolute -bottom-16 -right-16 w-64 h-64 bg-indigo-700 rounded-full opacity-50 blur-3xl" />

          <div className="relative">
            <h2 className="text-4xl sm:text-5xl font-bold text-white tracking-tight mb-4">
              Ready to store smarter?
            </h2>
            <p className="text-indigo-200 text-lg mb-10 max-w-xl mx-auto">
              Join thousands of students who skip the U-Haul stress. Book your pickup in minutes.
            </p>
            <Link
              to="/book"
              className="inline-flex items-center gap-2 bg-white text-indigo-700 font-semibold px-8 py-4 rounded-full hover:bg-indigo-50 transition-all duration-200 hover:shadow-xl hover:-translate-y-0.5 text-base"
            >
              Book Your Storage
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
