import PricingCard from '../ui/PricingCard';
import { pricingPlans } from '../../data/pricing';

export default function PricingPreview() {
  return (
    <section className="py-24 bg-gray-50">
      <div className="max-w-6xl mx-auto px-6">
        <div className="text-center mb-16">
          <p className="text-indigo-600 font-semibold text-sm uppercase tracking-widest mb-3">
            Pricing
          </p>
          <h2 className="text-4xl font-bold text-gray-950 tracking-tight mb-4">
            Simple, transparent plans
          </h2>
          <p className="text-gray-500 text-lg max-w-xl mx-auto">
            No hidden fees, no surprises. Pick the plan that fits your dorm and your budget.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-center">
          {pricingPlans.map((plan) => (
            <PricingCard key={plan.id} plan={plan} />
          ))}
        </div>
      </div>
    </section>
  );
}
