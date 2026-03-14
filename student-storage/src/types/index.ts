export interface PricingPlan {
  id: string;
  name: string;
  price: number;
  size: string;
  dimensions: string;
  description: string;
  features: string[];
  popular?: boolean;
}

export interface Testimonial {
  id: string;
  name: string;
  university: string;
  year: string;
  quote: string;
  rating: number;
  initials: string;
}

export interface FAQ {
  id: string;
  question: string;
  answer: string;
}

export interface ServiceFeature {
  icon: string;
  title: string;
  description: string;
}

export interface BookingFormState {
  step: number;
  plan: string;
  startDate: string;
  endDate: string;
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  notes: string;
}
