import { Check } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { PricingPlan } from '../../types';

interface PricingCardProps {
  plan: PricingPlan;
}

export default function PricingCard({ plan }: PricingCardProps) {
  return (
    <div
      className={`relative flex flex-col rounded-3xl p-8 transition-all duration-300 ${
        plan.popular
          ? 'bg-indigo-600 text-white shadow-2xl shadow-indigo-200 scale-105'
          : 'bg-white border border-gray-100 hover:shadow-xl hover:-translate-y-1'
      }`}
    >
      {plan.popular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2">
          <span className="bg-amber-400 text-amber-900 text-xs font-semibold px-4 py-1.5 rounded-full">
            Most Popular
          </span>
        </div>
      )}

      <div className="mb-6">
        <div
          className={`inline-block text-sm font-medium px-3 py-1 rounded-full mb-3 ${
            plan.popular ? 'bg-indigo-500 text-indigo-100' : 'bg-indigo-50 text-indigo-600'
          }`}
        >
          {plan.dimensions}
        </div>
        <h3 className={`text-2xl font-bold mb-1 ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
          {plan.name}
        </h3>
        <p className={`text-sm ${plan.popular ? 'text-indigo-200' : 'text-gray-500'}`}>
          {plan.description}
        </p>
      </div>

      <div className="mb-8">
        <span className={`text-5xl font-bold ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
          ${plan.price}
        </span>
        <span className={`text-sm ml-1 ${plan.popular ? 'text-indigo-200' : 'text-gray-400'}`}>
          /month
        </span>
      </div>

      <ul className="space-y-3 mb-8 flex-1">
        {plan.features.map((feature) => (
          <li key={feature} className="flex items-center gap-3 text-sm">
            <Check
              size={16}
              className={`shrink-0 ${plan.popular ? 'text-indigo-200' : 'text-indigo-500'}`}
            />
            <span className={plan.popular ? 'text-indigo-100' : 'text-gray-600'}>{feature}</span>
          </li>
        ))}
      </ul>

      <Link
        to={`/book?plan=${plan.id}`}
        className={`block text-center font-semibold py-3.5 rounded-2xl transition-all duration-200 ${
          plan.popular
            ? 'bg-white text-indigo-600 hover:bg-indigo-50'
            : 'bg-indigo-600 text-white hover:bg-indigo-700'
        }`}
      >
        Get Started
      </Link>
    </div>
  );
}
