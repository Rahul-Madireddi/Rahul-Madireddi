import type { PricingPlan } from '../types';

export const pricingPlans: PricingPlan[] = [
  {
    id: 'small',
    name: 'Small',
    price: 49,
    size: '5×5 ft',
    dimensions: '5 ft × 5 ft',
    description: 'Perfect for a few boxes, backpacks, and small items.',
    features: [
      'Up to 5 boxes or bags',
      'Free pickup & delivery',
      'Climate-controlled storage',
      'Fully insured up to $500',
      'Online inventory tracking',
    ],
  },
  {
    id: 'medium',
    name: 'Medium',
    price: 89,
    size: '5×10 ft',
    dimensions: '5 ft × 10 ft',
    description: 'Great for a full dorm room worth of belongings.',
    features: [
      'Up to 15 boxes or bags',
      'Free pickup & delivery',
      'Climate-controlled storage',
      'Fully insured up to $2,000',
      'Online inventory tracking',
      'Priority pickup scheduling',
    ],
    popular: true,
  },
  {
    id: 'large',
    name: 'Large',
    price: 139,
    size: '10×10 ft',
    dimensions: '10 ft × 10 ft',
    description: 'Ideal for apartment furniture and large loads.',
    features: [
      'Unlimited boxes & bags',
      'Free pickup & delivery',
      'Climate-controlled storage',
      'Fully insured up to $5,000',
      'Online inventory tracking',
      'Priority pickup scheduling',
      'Mid-storage item access',
    ],
  },
];
