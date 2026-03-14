import { useState } from 'react';
import { useLocation, Link } from 'react-router-dom';
import { CheckCircle, ChevronDown, Lock, CreditCard } from 'lucide-react';
import type { PricingPlan } from '../types';

interface LocationState {
  plan: PricingPlan;
  startDate: string;
  endDate: string;
}

export default function PaymentPage() {
  const location = useLocation();
  const state = location.state as LocationState | null;
  const plan = state?.plan ?? { name: 'Medium', price: 89, dimensions: '5×10 ft', id: 'medium' };

  const [showCard, setShowCard] = useState(false);
  const [success, setSuccess] = useState(false);
  const [card, setCard] = useState({ number: '', expiry: '', cvv: '', name: '' });

  function handleApplePay() {
    setSuccess(true);
  }

  function handleCardSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSuccess(true);
  }

  if (success) {
    return (
      <div className="pt-16 min-h-screen bg-gray-50 flex items-center justify-center px-6">
        <div className="max-w-md w-full bg-white rounded-3xl border border-gray-100 p-10 text-center shadow-sm">
          <div className="w-16 h-16 bg-green-50 rounded-full flex items-center justify-center mx-auto mb-5">
            <CheckCircle size={36} className="text-green-500" />
          </div>
          <h1 className="text-3xl font-bold text-gray-950 mb-3">You're all set!</h1>
          <p className="text-gray-500 mb-2">
            Your <strong className="text-gray-700">{plan.name} storage</strong> has been booked.
          </p>
          <p className="text-gray-400 text-sm mb-8">
            A confirmation email has been sent to your @illinois.edu address. We'll reach out 48
            hours before your scheduled pickup.
          </p>
          <div className="bg-indigo-50 rounded-2xl p-5 text-left mb-8 space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Plan</span>
              <span className="font-semibold text-gray-800">{plan.name}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Monthly charge</span>
              <span className="font-semibold text-gray-800">${plan.price}/mo</span>
            </div>
            {state?.startDate && (
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Pickup</span>
                <span className="font-semibold text-gray-800">{state.startDate}</span>
              </div>
            )}
          </div>
          <Link
            to="/"
            className="block bg-indigo-600 text-white font-semibold py-3.5 rounded-xl hover:bg-indigo-700 transition-colors"
          >
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="pt-16 min-h-screen bg-gray-50">
      <div className="max-w-lg mx-auto px-6 py-16">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-bold text-gray-950 tracking-tight mb-2">Checkout</h1>
          <p className="text-gray-500 text-sm flex items-center justify-center gap-1.5">
            <Lock size={13} className="text-indigo-400" />
            Secured with 256-bit SSL encryption
          </p>
        </div>

        {/* Order summary */}
        <div className="bg-white rounded-3xl border border-gray-100 p-6 mb-6 shadow-sm">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
            Order Summary
          </h2>
          <div className="flex items-center justify-between">
            <div>
              <p className="font-semibold text-gray-900">
                {plan.name} Storage Plan
              </p>
              <p className="text-sm text-gray-400">{(plan as PricingPlan).dimensions}</p>
            </div>
            <p className="text-2xl font-bold text-gray-900">${plan.price}</p>
          </div>
          <div className="border-t border-gray-100 mt-4 pt-4 flex justify-between text-sm">
            <span className="text-gray-500">Pickup & delivery</span>
            <span className="text-green-600 font-medium">Free</span>
          </div>
          <div className="flex justify-between text-sm mt-2">
            <span className="text-gray-500">Tax</span>
            <span className="text-gray-700 font-medium">
              ${(plan.price * 0.0875).toFixed(2)}
            </span>
          </div>
          <div className="border-t border-gray-100 mt-4 pt-4 flex justify-between font-bold">
            <span className="text-gray-900">Total due today</span>
            <span className="text-gray-900 text-lg">
              ${(plan.price * 1.0875).toFixed(2)}
            </span>
          </div>
        </div>

        {/* Payment options */}
        <div className="bg-white rounded-3xl border border-gray-100 p-6 shadow-sm space-y-4">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
            Payment Method
          </h2>

          {/* Apple Pay button */}
          <button
            onClick={handleApplePay}
            className="w-full bg-black text-white font-medium py-3.5 rounded-2xl flex items-center justify-center gap-2 hover:bg-gray-900 transition-colors text-sm"
            aria-label="Pay with Apple Pay"
          >
            <svg viewBox="0 0 38 16" fill="none" xmlns="http://www.w3.org/2000/svg" className="h-5">
              <path
                d="M7.5 2.7C7.1 3.2 6.5 3.6 5.8 3.6C5.7 2.9 6.1 2.1 6.5 1.7C6.9 1.2 7.6 0.8 8.2 0.8C8.3 1.5 7.9 2.2 7.5 2.7ZM8.2 3.7C7.2 3.6 6.4 4.3 5.9 4.3C5.4 4.3 4.7 3.7 3.9 3.7C2.9 3.7 1.8 4.3 1.3 5.4C0.2 7.6 1 11 2.1 12.8C2.6 13.7 3.2 14.7 4.1 14.7C4.9 14.7 5.3 14.1 6.3 14.1C7.3 14.1 7.6 14.7 8.5 14.7C9.4 14.7 10 13.8 10.5 12.9C11.1 11.9 11.3 10.9 11.3 10.9C11.3 10.9 9.7 10.2 9.7 8.4C9.7 6.8 11 6.1 11.1 6C10.3 4.8 9.1 3.7 8.2 3.7Z"
                fill="white"
              />
              <path
                d="M16.5 1.3H14.3V8.4H16.5C18.5 8.4 19.8 7.1 19.8 4.8C19.8 2.6 18.5 1.3 16.5 1.3ZM16.4 6.9H15.8V2.8H16.4C17.6 2.8 18.3 3.6 18.3 4.9C18.3 6.2 17.6 6.9 16.4 6.9Z"
                fill="white"
              />
              <path
                d="M22.7 8.5C24 8.5 24.8 7.7 25 6.7H23.7C23.6 7.1 23.2 7.4 22.7 7.4C22 7.4 21.5 6.8 21.5 5.9C21.5 5 22 4.4 22.7 4.4C23.2 4.4 23.5 4.7 23.7 5.1H25C24.8 4.1 24 3.3 22.7 3.3C21.2 3.3 20.2 4.4 20.2 5.9C20.2 7.4 21.2 8.5 22.7 8.5Z"
                fill="white"
              />
              <path
                d="M28.6 8.5C30.2 8.5 31.2 7.4 31.2 5.9C31.2 4.4 30.2 3.3 28.6 3.3C27 3.3 26 4.4 26 5.9C26 7.4 27 8.5 28.6 8.5ZM28.6 7.4C27.8 7.4 27.3 6.8 27.3 5.9C27.3 5 27.8 4.4 28.6 4.4C29.4 4.4 29.9 5 29.9 5.9C29.9 6.8 29.4 7.4 28.6 7.4Z"
                fill="white"
              />
              <path
                d="M34.7 11.4C36.1 11.4 37 10.5 37 9.3V3.4H35.7V4.2C35.4 3.7 34.8 3.3 34.1 3.3C32.8 3.3 31.9 4.3 31.9 5.8C31.9 7.3 32.8 8.2 34.1 8.2C34.8 8.2 35.3 7.9 35.7 7.4V9.2C35.7 9.9 35.3 10.3 34.7 10.3C34.1 10.3 33.8 9.9 33.7 9.5H32.4C32.6 10.6 33.5 11.4 34.7 11.4ZM34.4 7.1C33.7 7.1 33.2 6.6 33.2 5.8C33.2 5 33.7 4.5 34.4 4.5C35.1 4.5 35.7 5 35.7 5.8C35.7 6.6 35.1 7.1 34.4 7.1Z"
                fill="white"
              />
            </svg>
            Pay with Apple Pay
          </button>

          {/* Divider */}
          <div className="flex items-center gap-3">
            <div className="flex-1 h-px bg-gray-100" />
            <span className="text-xs text-gray-400">or pay with card</span>
            <div className="flex-1 h-px bg-gray-100" />
          </div>

          {/* Card toggle */}
          <button
            onClick={() => setShowCard(!showCard)}
            className="w-full flex items-center justify-between p-4 rounded-2xl border border-gray-200 hover:border-gray-300 transition-colors text-sm font-medium text-gray-700"
          >
            <div className="flex items-center gap-2">
              <CreditCard size={16} className="text-gray-400" />
              Credit or debit card
            </div>
            <ChevronDown
              size={16}
              className={`text-gray-400 transition-transform duration-200 ${showCard ? 'rotate-180' : ''}`}
            />
          </button>

          {/* Card form */}
          {showCard && (
            <form onSubmit={handleCardSubmit} className="space-y-4 pt-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Name on card
                </label>
                <input
                  type="text"
                  required
                  className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition"
                  placeholder="Jane Smith"
                  value={card.name}
                  onChange={(e) => setCard({ ...card, name: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Card number
                </label>
                <input
                  type="text"
                  required
                  maxLength={19}
                  className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition"
                  placeholder="1234 5678 9012 3456"
                  value={card.number}
                  onChange={(e) => {
                    const v = e.target.value.replace(/\D/g, '').slice(0, 16);
                    const formatted = v.replace(/(.{4})/g, '$1 ').trim();
                    setCard({ ...card, number: formatted });
                  }}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">
                    Expiry
                  </label>
                  <input
                    type="text"
                    required
                    maxLength={5}
                    className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition"
                    placeholder="MM/YY"
                    value={card.expiry}
                    onChange={(e) => {
                      const v = e.target.value.replace(/\D/g, '').slice(0, 4);
                      const formatted = v.length >= 3 ? `${v.slice(0, 2)}/${v.slice(2)}` : v;
                      setCard({ ...card, expiry: formatted });
                    }}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">CVV</label>
                  <input
                    type="text"
                    required
                    maxLength={4}
                    className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-400 transition"
                    placeholder="123"
                    value={card.cvv}
                    onChange={(e) =>
                      setCard({ ...card, cvv: e.target.value.replace(/\D/g, '').slice(0, 4) })
                    }
                  />
                </div>
              </div>
              <button
                type="submit"
                className="w-full bg-indigo-600 text-white font-semibold py-3.5 rounded-xl hover:bg-indigo-700 transition-colors"
              >
                Pay ${(plan.price * 1.0875).toFixed(2)}
              </button>
            </form>
          )}
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          This is a UI demo. No real payment is processed.
        </p>
      </div>
    </div>
  );
}
