import { Check, X } from 'lucide-react';
import PricingCard from '../components/ui/PricingCard';
import { pricingPlans } from '../data/pricing';
import { whatYouCanStore, comparisonFeatures } from '../data/services';

export default function ServicesPage() {
  return (
    <div className="pt-16">
      {/* Hero */}
      <section className="py-24 bg-gradient-to-b from-indigo-50/60 to-white text-center px-6">
        <div className="max-w-3xl mx-auto">
          <p className="text-indigo-600 font-semibold text-sm uppercase tracking-widest mb-3">
            Services & Pricing
          </p>
          <h1 className="text-5xl font-bold text-gray-950 tracking-tight mb-6">
            Plans built for every student
          </h1>
          <p className="text-xl text-gray-500 leading-relaxed">
            Whether you're storing a few bags or a full dorm room, we have a plan that fits.
            All plans include free pickup and delivery.
          </p>
        </div>
      </section>

      {/* Pricing cards */}
      <section className="py-16 px-6">
        <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
          {pricingPlans.map((plan) => (
            <PricingCard key={plan.id} plan={plan} />
          ))}
        </div>
      </section>

      {/* Comparison table */}
      <section className="py-16 bg-gray-50 px-6">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-950 text-center mb-12 tracking-tight">
            Compare plans
          </h2>
          <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
            {/* Table header */}
            <div className="grid grid-cols-4 bg-gray-50 border-b border-gray-100">
              <div className="p-5 text-sm font-semibold text-gray-500">Feature</div>
              {pricingPlans.map((p) => (
                <div
                  key={p.id}
                  className={`p-5 text-center text-sm font-bold ${
                    p.popular ? 'text-indigo-600' : 'text-gray-900'
                  }`}
                >
                  {p.name}
                  {p.popular && (
                    <span className="block text-xs font-normal text-indigo-400">Popular</span>
                  )}
                </div>
              ))}
            </div>

            {comparisonFeatures.map((row, i) => (
              <div
                key={row.feature}
                className={`grid grid-cols-4 ${i % 2 === 0 ? 'bg-white' : 'bg-gray-50/50'} border-b border-gray-50 last:border-0`}
              >
                <div className="p-5 text-sm text-gray-600 font-medium">{row.feature}</div>
                {(['small', 'medium', 'large'] as const).map((planId) => {
                  const val = row[planId];
                  return (
                    <div key={planId} className="p-5 text-center">
                      {typeof val === 'boolean' ? (
                        val ? (
                          <Check size={18} className="text-indigo-500 mx-auto" />
                        ) : (
                          <X size={18} className="text-gray-300 mx-auto" />
                        )
                      ) : (
                        <span className="text-sm text-gray-700">{val}</span>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* What you can store */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-gray-950 tracking-tight mb-4">
            What can I store?
          </h2>
          <p className="text-gray-500 mb-12">
            Pretty much everything from your dorm or apartment. Here are some common items:
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {whatYouCanStore.map(({ label, emoji }) => (
              <div
                key={label}
                className="bg-gray-50 rounded-2xl p-5 flex flex-col items-center gap-2 hover:bg-indigo-50 transition-colors"
              >
                <span className="text-3xl">{emoji}</span>
                <span className="text-sm text-gray-700 font-medium text-center">{label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
