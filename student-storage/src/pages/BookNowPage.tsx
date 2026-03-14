import { useReducer, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { CheckCircle, ChevronRight, Package } from 'lucide-react';
import type { BookingFormState } from '../types';
import { pricingPlans } from '../data/pricing';

type Action =
  | { type: 'SET_FIELD'; field: keyof BookingFormState; value: string | number }
  | { type: 'NEXT_STEP' }
  | { type: 'PREV_STEP' };

function reducer(state: BookingFormState, action: Action): BookingFormState {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, [action.field]: action.value };
    case 'NEXT_STEP':
      return { ...state, step: state.step + 1 };
    case 'PREV_STEP':
      return { ...state, step: state.step - 1 };
    default:
      return state;
  }
}

const initialState: BookingFormState = {
  step: 1,
  plan: 'medium',
  startDate: '',
  endDate: '',
  firstName: '',
  lastName: '',
  email: '',
  phone: '',
  address: '',
  city: '',
  state: '',
  zip: '',
  notes: '',
};

const stepLabels = ['Choose Plan', 'Your Info', 'Review'];

export default function BookNowPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [form, dispatch] = useReducer(reducer, {
    ...initialState,
    plan: searchParams.get('plan') || 'medium',
  });

  const [emailError, setEmailError] = useReducerState('');

  useEffect(() => {
    const planParam = searchParams.get('plan');
    if (planParam) {
      dispatch({ type: 'SET_FIELD', field: 'plan', value: planParam });
    }
  }, [searchParams]);

  const selectedPlan = pricingPlans.find((p) => p.id === form.plan) ?? pricingPlans[1];

  function field(name: keyof BookingFormState) {
    return {
      value: form[name] as string,
      onChange: (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) =>
        dispatch({ type: 'SET_FIELD', field: name, value: e.target.value }),
    };
  }

  function validateAndNext() {
    if (form.step === 2) {
      if (!form.email.toLowerCase().endsWith('@illinois.edu')) {
        setEmailError('Only @illinois.edu email addresses are accepted at this time.');
        return;
      }
      setEmailError('');
    }
    dispatch({ type: 'NEXT_STEP' });
  }

  function handleConfirm() {
    navigate('/payment', {
      state: { plan: selectedPlan, startDate: form.startDate, endDate: form.endDate },
    });
  }

  const inputClass =
    'w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition';

  return (
    <div className="pt-16 min-h-screen bg-gray-50">
      <div className="max-w-xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-950 tracking-tight mb-2">Book Storage</h1>
          <p className="text-gray-500">It only takes a few minutes to get started.</p>
        </div>

        {/* Step indicator */}
        <div className="flex items-center justify-center gap-2 mb-10">
          {stepLabels.map((label, i) => {
            const stepNum = i + 1;
            const isActive = form.step === stepNum;
            const isComplete = form.step > stepNum;
            return (
              <div key={label} className="flex items-center gap-2">
                <div className="flex flex-col items-center gap-1">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-semibold transition-all ${
                      isComplete
                        ? 'bg-indigo-600 text-white'
                        : isActive
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    {isComplete ? <CheckCircle size={16} /> : stepNum}
                  </div>
                  <span
                    className={`text-xs font-medium ${
                      isActive ? 'text-indigo-600' : 'text-gray-400'
                    }`}
                  >
                    {label}
                  </span>
                </div>
                {i < stepLabels.length - 1 && (
                  <div className={`w-12 h-px mb-5 ${form.step > stepNum ? 'bg-indigo-400' : 'bg-gray-200'}`} />
                )}
              </div>
            );
          })}
        </div>

        {/* Card */}
        <div className="bg-white rounded-3xl border border-gray-100 p-8 shadow-sm">
          {/* Step 1: Choose Plan & Dates */}
          {form.step === 1 && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900">Choose your plan</h2>
              <div className="grid grid-cols-3 gap-3">
                {pricingPlans.map((p) => (
                  <button
                    key={p.id}
                    onClick={() => dispatch({ type: 'SET_FIELD', field: 'plan', value: p.id })}
                    className={`flex flex-col items-center gap-1 p-4 rounded-2xl border-2 transition-all text-center ${
                      form.plan === p.id
                        ? 'border-indigo-600 bg-indigo-50'
                        : 'border-gray-100 hover:border-gray-200'
                    }`}
                  >
                    <Package
                      size={20}
                      className={form.plan === p.id ? 'text-indigo-600' : 'text-gray-400'}
                    />
                    <span
                      className={`text-sm font-semibold ${
                        form.plan === p.id ? 'text-indigo-700' : 'text-gray-700'
                      }`}
                    >
                      {p.name}
                    </span>
                    <span
                      className={`text-xs ${form.plan === p.id ? 'text-indigo-500' : 'text-gray-400'}`}
                    >
                      ${p.price}/mo
                    </span>
                    {p.popular && (
                      <span className="text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded-full">
                        Popular
                      </span>
                    )}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Pickup date
                  </label>
                  <input type="date" required className={inputClass} {...field('startDate')} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Delivery date
                  </label>
                  <input type="date" required className={inputClass} {...field('endDate')} />
                </div>
              </div>
            </div>
          )}

          {/* Step 2: Contact & Address */}
          {form.step === 2 && (
            <div className="space-y-5">
              <h2 className="text-xl font-bold text-gray-900">Your information</h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    First name
                  </label>
                  <input type="text" required className={inputClass} {...field('firstName')} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Last name
                  </label>
                  <input type="text" required className={inputClass} {...field('lastName')} />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  University email <span className="text-indigo-500 font-normal">(@illinois.edu only)</span>
                </label>
                <input
                  type="email"
                  required
                  className={`${inputClass} ${emailError ? 'border-red-300 focus:ring-red-200 focus:border-red-400' : ''}`}
                  placeholder="netid@illinois.edu"
                  {...field('email')}
                />
                {emailError && (
                  <p className="mt-1.5 text-xs text-red-500">{emailError}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Phone number
                </label>
                <input type="tel" required className={inputClass} {...field('phone')} />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Pickup address
                </label>
                <input
                  type="text"
                  required
                  className={inputClass}
                  placeholder="Dorm name & room number"
                  {...field('address')}
                />
              </div>

              <div className="grid grid-cols-6 gap-3">
                <div className="col-span-3">
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">City</label>
                  <input type="text" required className={inputClass} {...field('city')} />
                </div>
                <div className="col-span-1">
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">State</label>
                  <input type="text" required className={inputClass} {...field('state')} />
                </div>
                <div className="col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">ZIP</label>
                  <input type="text" required className={inputClass} {...field('zip')} />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Special instructions (optional)
                </label>
                <textarea
                  rows={3}
                  className={`${inputClass} resize-none`}
                  placeholder="e.g., call when arriving, access code, fragile items..."
                  {...field('notes')}
                />
              </div>
            </div>
          )}

          {/* Step 3: Review */}
          {form.step === 3 && (
            <div className="space-y-6">
              <h2 className="text-xl font-bold text-gray-900">Review your booking</h2>
              <div className="bg-indigo-50 rounded-2xl p-5 space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Plan</span>
                  <span className="font-semibold text-gray-900">
                    {selectedPlan.name} ({selectedPlan.dimensions})
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Price</span>
                  <span className="font-semibold text-gray-900">${selectedPlan.price}/month</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Pickup</span>
                  <span className="font-semibold text-gray-900">
                    {form.startDate || '—'}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Delivery</span>
                  <span className="font-semibold text-gray-900">{form.endDate || '—'}</span>
                </div>
                <div className="border-t border-indigo-100 my-1" />
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Name</span>
                  <span className="font-semibold text-gray-900">
                    {form.firstName} {form.lastName}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Email</span>
                  <span className="font-semibold text-gray-900">{form.email}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Address</span>
                  <span className="font-semibold text-gray-900 text-right max-w-xs">
                    {form.address}, {form.city}, {form.state} {form.zip}
                  </span>
                </div>
              </div>
              <p className="text-gray-400 text-xs">
                By confirming, you agree to our terms of service. You'll be taken to payment to complete your booking.
              </p>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex justify-between mt-8">
            {form.step > 1 ? (
              <button
                onClick={() => dispatch({ type: 'PREV_STEP' })}
                className="text-gray-500 text-sm font-medium hover:text-gray-700 transition-colors"
              >
                ← Back
              </button>
            ) : (
              <div />
            )}

            {form.step < 3 ? (
              <button
                onClick={validateAndNext}
                className="bg-indigo-600 text-white font-semibold px-6 py-3 rounded-xl hover:bg-indigo-700 transition-colors flex items-center gap-2 text-sm"
              >
                Continue
                <ChevronRight size={16} />
              </button>
            ) : (
              <button
                onClick={handleConfirm}
                className="bg-indigo-600 text-white font-semibold px-6 py-3 rounded-xl hover:bg-indigo-700 transition-colors flex items-center gap-2 text-sm"
              >
                Proceed to Payment
                <ChevronRight size={16} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Tiny local helper to avoid importing useState for a single string
function useReducerState(initial: string): [string, (v: string) => void] {
  const [s, d] = useReducer((_: string, v: string) => v, initial);
  return [s, d];
}
